import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import hashlib
import json
import logging
import random
import signal
import sys
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
from loguru import logger
from pydantic import BaseModel, Field
import socketio

from core.data_mapper import DataMapper
from core.layout_classifier import LayoutClassifier
from core.llm import call_llm
from mcp_clients import MCPGenUIService, MCPUserService


# Preload agent expression texts
AGENT_EXPRESSIONS: dict[str, list[str]] = {}

def _read_file_lines(path: str) -> list[str]:
    try:
        with open(path, encoding='utf-8') as f:
            return [line.rstrip('\n') for line in f.readlines()]
    except Exception as e:
        logger.warning(f"Failed to read file {path}: {e}")
        return []

def preload_agent_expressions() -> None:
    """Read agent expression text files into memory as a dict.

    Keys: p1, p2, p3, p4, p5
    Values: list of lines (strings)
    """
    base = "./core/agent_expression"
    mapping = {
        "p1": f"{base}/p1_begin.txt",
        "p2": f"{base}/p2_sequential_thinking.txt",
        "p3": f"{base}/p3_thinking.txt",
        "p4": f"{base}/p4_ui_design.txt",
        "p5": f"{base}/p5_ui_generation.txt",
    }
    loaded: dict[str, list[str]] = {}
    for k, path in mapping.items():
        loaded[k] = _read_file_lines(path)
        logger.info(f"Preloaded agent expression: {k} = {len(loaded[k])} lines")
    global AGENT_EXPRESSIONS
    AGENT_EXPRESSIONS = loaded
    logger.info(
        "Preloaded agent expressions: " +
        ", ".join([f"{k}={len(v)} lines" for k, v in loaded.items()])
    )

# Create service instances
mcp_user_service = MCPUserService()
mcp_genui_service = MCPGenUIService()

# Create core components
layout_classifier = LayoutClassifier()
data_mapper = DataMapper()

# Logger configuration

logger.add(
    "logs/app.log",
    rotation="10 MB",
    level="INFO",
    # filter=lambda record: "Sending packet MESSAGE data" not in record["message"]
)

class UserRequest(BaseModel):
    intent: str = Field(
        default='Show me a photo of a cute cat.',
        description="User's intent or query"
    )
    context: dict = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info("Starting up Socket.IO MCP Host application...")
    try:
        # Preload agent expressions
        preload_agent_expressions()
        # Log preloaded layout summary
        try:
            demo_summary = layout_classifier.get_demo_layouts_summary()
            fixed_types = list(layout_classifier.fixed_layouts.keys())
            logger.info(
                f"Layout preload completed: middle={demo_summary.get('middle_layouts_count', 0)}, fixed_types={fixed_types}"
            )
            for ft, items in (layout_classifier.fixed_layouts or {}).items():
                logger.info(f"  - fixed[{ft}]: {len(items)}")
            mids = [m.get('id') for m in (demo_summary.get('middle_layouts') or [])][:5]
            if mids:
                logger.info(f"  - sample middle ids: {mids}")
        except Exception as e:
            logger.warning(f"Failed to log layout preload summary: {e}")

        # Initialize MCP User Service
        await mcp_user_service.initialize()
        
        # Initialize MCP GenUI service
        await mcp_genui_service.initialize()
                
        logger.info("MCP Services initialized successfully")
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        logger.error("Application will not start due to service initialization failures")
        raise e
    
    yield
    
    # Shutdown
    logger.info("Shutting down Socket.IO MCP Host application...")
    try:
        await mcp_user_service.cleanup()
        logger.info("MCP User Service cleanup completed successfully")
    except Exception as e:
        logger.error(f"Error during MCP User Service cleanup: {str(e)}")
    
    # Clean up MCP GenUI service
    try:
        await mcp_genui_service.cleanup()
        logger.info("MCP GenUI Service cleanup completed successfully")
    except Exception as e:
        logger.error(f"Error during MCP GenUI Service cleanup: {str(e)}")
    
    logger.info("Application shutdown completed")

# FastAPI app with lifespan management
app = FastAPI(
    title="MCP Host Socket.IO API",
    description="Socket.IO based 3-Step MCP Host: 1) MCP Data Collection -> 2) Layout Classification -> 3) Data Mapping",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Socket.IO server
# Silence verbose socketio/engineio internal logs (e.g., "Sending packet MESSAGE data ...")
socketio_logger = logging.getLogger("socketio")
socketio_logger.setLevel(logging.WARNING)
engineio_logger = logging.getLogger("engineio")
engineio_logger.setLevel(logging.WARNING)

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=engineio_logger
)

# Mount Socket.IO to FastAPI
socket_app = socketio.ASGIApp(sio, app)

# In-memory session tracking for running tasks per Socket.IO sid / clientId
active_sessions = {}
client_to_sid_map = {}

def _register_client_mapping(sid: str, client_id: str | None):
    if isinstance(client_id, str) and client_id:
        client_to_sid_map[client_id] = sid
        session = active_sessions.get(sid) or {}
        session["client_id"] = client_id
        active_sessions[sid] = session

async def cancel_session_by_sid(sid: str, reason: str = "", duration_ms: int | None = None):
    session = active_sessions.pop(sid, None)
    if not session:
        return
    task = session.get("task")
    client_id = session.get("client_id")
    # Best-effort reverse mapping cleanup
    if isinstance(client_id, str) and client_id:
        mapped_sid = client_to_sid_map.get(client_id)
        if mapped_sid == sid:
            client_to_sid_map.pop(client_id, None)
    try:
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    finally:
        logger.info(f"[DISCONNECT] Cleanup completed for sid={sid} client_id={client_id} reason={reason} durationMs={duration_ms}")

async def cancel_session_by_client_id(client_id: str, reason: str = "", duration_ms: int | None = None):
    if not isinstance(client_id, str) or not client_id:
        return
    sid = client_to_sid_map.get(client_id)
    if sid:
        await cancel_session_by_sid(sid, reason=reason, duration_ms=duration_ms)
    else:
        logger.info(f"[DISCONNECT] No active sid found for clientId={client_id}")

def _parse_chunk_data(chunk: str):
    """Parse JSON chunk and extract relevant data"""
    try:
        return json.loads(chunk.strip())
    except (json.JSONDecodeError, AttributeError):
        logger.error(f"Error parsing chunk: {chunk}")
        return None


def _is_image_tool(schema_node: dict) -> bool:
    try:
        val = str((schema_node or {}).get("tool_type", "")).strip().lower()
        return val in ("image_search", "img_search")
    except Exception:
        return False


def find_image_tool_paths_by_schema_and_data(schema: dict, data):
    """스키마의 tool_type: image_search(or img_search) 표기를 기준으로 실제 데이터에서 경로를 수집한다.

    - 스키마의 비표준 구조(parameters에서 object/array를 혼용)와 표준 스타일(properties/items)을 모두 지원한다.
    - 배열은 실제 매핑된 데이터의 인덱스로 확장한다.
    반환: path 리스트 (예: [["thumbnail_list", 0, "thumbnail_img"], ...])
    """
    paths = []

    META_KEYS = {
        "description", "type", "example", "examples", "max", "max_words", "file",
        "html", "layout", "name", "contents_type", "oneOf", "items", "data",
        "default", "tool_type"
    }

    def _walk(sch, dat, cur_path):
        if not isinstance(sch, dict):
            return

        sch_type = sch.get("type")

        # 배열 노드 자체가 이미지 툴이면 실제 데이터의 인덱스로 확장하여 경로를 수집한다.
        if sch_type == "array" and _is_image_tool(sch):
            if isinstance(dat, list) and len(dat) > 0:
                for idx in range(len(dat)):
                    paths.append(cur_path + [idx])
            else:
                # 데이터가 비어있으면 최소 1개를 대상으로 가정
                paths.append(cur_path + [0])
            return

        # 비-배열 노드가 이미지 툴이면 현재 경로를 그대로 추가
        if _is_image_tool(sch):
            paths.append(list(cur_path))
            return

        # 배열: 비표준(data) 우선 지원, 표준(items)도 지원
        if sch_type == "array":
            # 우선 data 필드 (비표준) 처리
            if isinstance(sch.get("data"), dict) and isinstance(dat, list):
                item_schema = sch["data"]
                for idx, item in enumerate(dat):
                    _walk(item_schema, item, cur_path + [idx])
                return

            # 표준 items 처리
            items = sch.get("items")
            if isinstance(items, dict) and isinstance(dat, list):
                # items 자체가 이미지 툴일 수 있음 (배열 원소가 바로 string 이미지 등)
                if _is_image_tool(items):
                    for idx in range(len(dat)):
                        paths.append(cur_path + [idx])
                    return

                item_type = items.get("type")
                if item_type == "object" and isinstance(items.get("properties"), dict):
                    props = items["properties"]
                    for idx, item in enumerate(dat):
                        if isinstance(item, dict):
                            for k, prop_sch in props.items():
                                _walk(prop_sch, item.get(k), cur_path + [idx, k])
                    return

                # 기타 단순 타입(string 등)에는 별도 처리 없음
                return

        # 객체: 표준(properties) 우선, 없으면 parameters 스타일(비표준)로 필드 키 순회
        if sch.get("properties") and isinstance(sch.get("properties"), dict) and isinstance(dat, dict):
            for k, sub_sch in sch["properties"].items():
                _walk(sub_sch, (dat or {}).get(k), cur_path + [k])
            return

        # parameters 스타일: 데이터의 키와 교집합으로 탐색 (메타키 제외)
        if isinstance(dat, dict):
            for k, sub_sch in sch.items():
                if k in META_KEYS:
                    continue
                _walk(sub_sch, dat.get(k), cur_path + [k])

    _walk(schema or {}, data, [])
    return paths


def _path_to_str(path):
    parts = []
    for p in path:
        if isinstance(p, int):
            parts[-1] = f"{parts[-1]}[{p}]" if parts else f"[{p}]"
        else:
            parts.append(str(p))
    return ".".join(parts)


def set_value_at_path(obj, path, value):
    cur = obj
    for i, p in enumerate(path):
        is_last = i == len(path) - 1
        if is_last:
            if isinstance(cur, dict) and isinstance(p, str):
                cur[p] = value
            elif isinstance(cur, list) and isinstance(p, int) and p >= 0:
                # 필요한 경우 리스트를 확장하여 인덱스에 할당 가능하도록 처리
                if p >= len(cur):
                    cur.extend([None] * (p - len(cur) + 1))
                cur[p] = value
            return
        # 이동
        if isinstance(cur, dict) and isinstance(p, str):
            cur = cur.get(p)
        elif isinstance(cur, list) and isinstance(p, int) and 0 <= p < len(cur):
            cur = cur[p]
        else:
            return


def build_image_generation_requests_for_paths(img_paths_by_slot: dict,
                                              intent: str,
                                              context: dict,
                                              default_width: int = 128,
                                              default_height: int = 128,
                                              model: str = "dalle",
                                              prompts_by_key: dict | None = None):
    """경로 기준으로 이미지 요청 배열과 인덱스 매핑을 생성한다."""
    requests = []
    index_map = []  # (slot, path)
    prompt_base = str((context or {}).get("image_prompt") or intent or "image")
    for slot, paths in (img_paths_by_slot or {}).items():
        if not isinstance(paths, list):
            continue
        for path in paths:
            path_str = _path_to_str(path)
            key = f"{slot}|{path_str}"
            prompt = (prompts_by_key or {}).get(key) or prompt_base
            requests.append({
                "prompt": f"{prompt}, {intent}",
                "width": int(default_width),
                "height": int(default_height),
                "model": model
            })
            index_map.append((slot, path))
    return requests, index_map


def _json(v):
    import json as _json
    return _json.dumps(v, ensure_ascii=False, indent=2)


def _parse_json_loose(text: str):
    import json as _json
    t = (text or "").strip()
    if t.startswith("```json"):
        t = t[7:]
    if t.startswith("```"):
        t = t[3:]
    if t.endswith("```"):
        t = t[:-3]
    t = t.strip()
    try:
        return _json.loads(t)
    except Exception:
        pass
    try:
        s = t.find("{")
        e = t.rfind("}")
        if s != -1 and e != -1 and e > s:
            return _json.loads(t[s:e+1])
    except Exception:
        pass
    return {}


async def choose_expression(data: str,
                               candidates: list[str],
                               model_name: str = "gpt-5-nano") -> str:
    """사용자의 intent와 context를 고려해 p1 문장 후보 중 1개를 선택한다.

    선호 순서:
      1) LLM에 선택을 요청하여 index를 받는다.
      2) 실패 시 intent+context의 해시를 이용한 안정적(deteministic) 선택.
    """
    try:
        if not isinstance(candidates, list) or len(candidates) == 0:
            return "Okay, I'm now working on your request."


        # 1) LLM 기반 선택 시도 (정확히 하나의 index 반환을 요구)
        try:
            items = [{"index": i, "text": t} for i, t in enumerate(candidates)]
            prompt = (
                "You are selecting ONE best-fitting short status message to show before user data collection.\n"
                "Consider user's intent and context. Choose exactly one from the list.\n\n"
                "Return strictly JSON with the shape: {\"index\": number}. No extra text.\n\n"
                f"Reference data:\n{data}\n\nCandidates (array of objects [index, text]):\n{json.dumps(items, ensure_ascii=False)}\n"
            )
            resp = await call_llm(prompt, model_name=model_name)
            parsed = _parse_json_loose(resp or "{}")
            if isinstance(parsed, dict):
                idx = parsed.get("index")
                if isinstance(idx, int) and 0 <= idx < len(candidates):
                    return candidates[idx]
        except Exception as e:
            logger.debug(f"LLM-based p1 selection failed, will fallback: {e}")
            return random.choice(candidates)

        # 2) 해시 기반 안정적 선택 (파이썬 내장 hash는 세션마다 달라질 수 있어 md5 사용)
        digest = hashlib.md5(data.encode("utf-8")).hexdigest()
        # 첫 8자리 16진수를 정수로 변환하여 모듈러
        idx = int(digest[:8], 16) % len(candidates)
        return candidates[idx]
    except Exception as e:
        logger.warning(f"choose_expression unexpected error: {e}")
        return candidates[0] if candidates else "Okay, I'm now working on your request."


async def suggest_image_prompts_by_path(intent: str,
                                        context: dict,
                                        layout_result: dict,
                                        mapped_params_all: dict,
                                        img_paths_by_slot: dict,
                                        model_name: str = "gpt-5-mini") -> dict:
    """LLM에 각 경로별 맞춤 이미지 프롬프트 생성을 요청한다.

    반환: {"slot|path_str": prompt}
    """
    # 입력 구성: 슬롯별 레이아웃 설명과 데이터 스냅샷, 타겟 경로
    targets = []
    for slot, paths in (img_paths_by_slot or {}).items():
        layout_info = (layout_result.get(slot) or {}).get("layout_data") or {}
        desc = layout_info.get("description", "")
        data_obj = (mapped_params_all or {}).get(slot) or {}
        for p in paths:
            targets.append({
                "slot": slot,
                "path": _path_to_str(p),
                "layout_desc": desc,
                "slot_data": data_obj,
            })

    prompt = (
        "You are an expert image search keyword generator.\n"
        "Given the user's intent, context, UI layout descriptions, and the exact data paths of image placeholders,\n"
        "write a short English keyword phrase (<= 5 words) per target that best represents the content at that path.\n\n"
        "Guidelines:\n"
        "- Use mainly nouns and adjectives; avoid verbs and filler words.\n"
        "- Keep it concise; no quotes or special characters; commas allowed.\n"
        "- Avoid brand names and specific person names.\n"
        "- Do NOT include UI/layout/container/action terms (e.g., header, footer, button, order, card, page).\n"
        "- If the target implies a human (e.g., profile/thumbnail/portrait/person/celebrity), DO NOT use real names;\n"
        "  produce abstract keywords instead (e.g., 'women chat thumbnail', 'female athlete action').\n"
        "- If a list item, you may infer subject/context from adjacent fields.\n"
        "- IMPORTANT: All keyword phrases MUST be UNIQUE across all targets. Even if two targets have similar meaning,\n"
        "  do NOT output identical wording. Vary synonyms, word order, or composition descriptors (e.g., close-up,\n"
        "  wide shot, portrait, landscape, macro, aerial, dramatic, calm, minimal, vintage, modern).\n\n"
        "Examples of desired keyword style:\n"
        "- juicy plums, purple background\n"
        "- Dynamic tennis player, active\n"
        "- Dramatic, athletic, female, action\n"
        "- white car, desert, mountain\n"
        "- Luxurious grand living room\n\n"
        "Output strictly JSON (no extra text): { \"slot|path\": \"keywords\", ... }\n"
        "All values must be unique (no duplicate strings across keys).\n\n"
        f"Intent:\n{intent}\n\nContext:\n{_json(context)}\n\nTargets:\n{_json(targets)}\n"
    )

    try:
        response_text = await call_llm(prompt, model_name=model_name)
        parsed = _parse_json_loose(response_text or "{}")
        if not isinstance(parsed, dict):
            parsed = {}
        # 키 형식 정규화 확인 및 로그
        bad_keys = [k for k in parsed.keys() if not isinstance(k, str) or "|" not in k]
        if bad_keys:
            logger.warning(f"LLM prompt map has unexpected keys: {bad_keys}")
        return parsed
    except Exception as e:
        logger.warning(f"suggest_image_prompts_by_path failed: {e}")
        return {}


def validate_and_fix_bottom_structure(final_result: dict) -> dict:
    """bottom 부분의 구조를 검증하고 수정합니다.
    
    - bottom에서 'data', 'html'만 허용
    - 'data'에는 파라미터만 존재해야 함
    - 에러 케이스: 'data' 안에 'parameters'가 또 존재하는 경우
    - 이런 경우 'parameters' 데이터들을 'data' 아래로 옮겨서 반환
    
    Args:
        final_result: 전체 결과 딕셔너리
        
    Returns:
        수정된 final_result 딕셔너리
    """
    if not isinstance(final_result, dict):
        return final_result
    
    bottom_data = final_result.get('bottom')
    if not isinstance(bottom_data, dict):
        return final_result
    
    logger.info("Bottom validation 시작")
    
    # bottom에서 허용되지 않는 키 제거 (data, html 외)
    allowed_keys = {'data', 'html'}
    removed_keys = []
    for key in list(bottom_data.keys()):
        if key not in allowed_keys:
            removed_keys.append(key)
            del bottom_data[key]
    
    if removed_keys:
        logger.info(f"Bottom에서 허용되지 않는 키 제거: {removed_keys}")
    
    # data 구조 검증 및 수정
    data_section = bottom_data.get('data')
    if isinstance(data_section, dict):
        # parameters가 data 안에 있는 경우 (에러 케이스)
        if 'parameters' in data_section:
            logger.info("Bottom data에서 parameters 발견 - 재구조화 진행")
            parameters = data_section.pop('parameters')
            
            if isinstance(parameters, dict):
                # parameters의 내용을 data 레벨로 이동
                for param_key, param_value in parameters.items():
                    data_section[param_key] = param_value
                logger.info(f"Parameters를 data 레벨로 이동: {list(parameters.keys())}")
            elif isinstance(parameters, list):
                # parameters가 리스트인 경우 적절히 처리
                logger.warning("Parameters가 리스트 형태입니다 - 추가 처리 필요할 수 있음")
        
        logger.info(f"Bottom data 최종 키들: {list(data_section.keys())}")
    
    logger.info("Bottom validation 완료")
    return final_result


def test_bottom_validation():
    """Bottom validation 로직을 테스트합니다."""
    print("=== Bottom Validation 테스트 시작 ===")
    
    # 테스트 케이스 1: 정상적인 구조
    test_case_1 = {
        'top': {'data': {'title': 'Weekend Picks'}, 'html': '<div>top</div>'},
        'bottom': {
            'data': {'name': 'Showtime Options', 'layout': 'thumbnail'},
            'html': '<div>bottom</div>'
        }
    }
    
    print("테스트 케이스 1 (정상 구조):")
    print(f"입력: {test_case_1['bottom']}")
    result_1 = validate_and_fix_bottom_structure(test_case_1)
    print(f"출력: {result_1['bottom']}")
    print()
    
    # 테스트 케이스 2: parameters가 data 안에 있는 에러 케이스
    test_case_2 = {
        'bottom': {
            'data': {
                'name': 'Showtime Options',
                'layout': 'thumbnail',
                'description': 'Showtime Suggestions',
                'parameters': {
                    'title': 'Movie List',
                    'items': ['Movie 1', 'Movie 2'],
                    'count': 5
                }
            },
            'html': '<div>bottom</div>',
            'extra_key': 'should_be_removed'
        }
    }
    
    print("테스트 케이스 2 (parameters 에러 케이스):")
    print(f"입력: {test_case_2['bottom']}")
    result_2 = validate_and_fix_bottom_structure(test_case_2)
    print(f"출력: {result_2['bottom']}")
    print()
    
    # 테스트 케이스 3: 사용자가 제공한 예시와 유사한 구조
    test_case_3 = {
        'bottom': {
            'data': {
                'name': 'Showtime Options',
                'layout': 'thumbnail',
                'description': 'Showtime Suggestions',
                'parameters': {
                    'component_title': 'Weekend Movies',
                    'thumbnail_list': [
                        {'title': 'Movie 1', 'thumbnail': 'img1.jpg'},
                        {'title': 'Movie 2', 'thumbnail': 'img2.jpg'}
                    ]
                }
            },
            'html': '<div class="footer">...</div>'
        }
    }
    
    print("테스트 케이스 3 (사용자 예시와 유사한 구조):")
    print(f"입력: {test_case_3['bottom']}")
    result_3 = validate_and_fix_bottom_structure(test_case_3)
    print(f"출력: {result_3['bottom']}")
    print()
    
    print("=== Bottom Validation 테스트 완료 ===")


# 테스트 실행 (개발 중에만)
if __name__ == "__main__" and False:  # False로 설정하여 실제 서버 실행 시에는 테스트 안 함
    test_bottom_validation()


def validate_image_injection(final_result: dict, paths_by_slot: dict, prefix: str = ""):
    """치환 검증: 각 경로 위치에 data:image/png;base64, 형태가 제대로 들어갔는지 로그 출력."""
    total_targets = 0
    total_filled = 0
    for slot, paths in (paths_by_slot or {}).items():
        data_obj = ((final_result or {}).get(slot) or {}).get("data") or {}
        slot_filled = 0
        for path in paths:
            total_targets += 1
            cur = data_obj
            ok = False
            for i, p in enumerate(path):
                is_last = i == len(path) - 1
                if is_last:
                    if isinstance(cur, dict) and isinstance(p, str):
                        val = cur.get(p)
                        ok = isinstance(val, str) and val.startswith("data:image/")
                    elif isinstance(cur, list) and isinstance(p, int) and 0 <= p < len(cur):
                        val = cur[p]
                        ok = isinstance(val, str) and val.startswith("data:image/")
                else:
                    if isinstance(cur, dict) and isinstance(p, str):
                        cur = cur.get(p)
                    elif isinstance(cur, list) and isinstance(p, int) and 0 <= p < len(cur):
                        cur = cur[p]
                    else:
                        break
            if ok:
                slot_filled += 1
                total_filled += 1
            logger.info(f"Image injection check [{slot}] {_path_to_str(path)} => {'OK' if ok else 'MISS'}")
        logger.info(f"Image injection summary for slot '{slot}': {slot_filled}/{len(paths)} filled")
    logger.info(f"Image injection total summary: {total_filled}/{total_targets} filled")


async def call_image_service(service_url: str, requests_payload: list) -> list:
    """
        이미지 생성 서버를 호출하여 결과 리스트를 반환한다.
    """
    if not requests_payload:
        return []

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(service_url, json={"requests": requests_payload})
            resp.raise_for_status()
            data = resp.json()
            return [f'data:image/png;base64,{d["image_data"]}' for d in data.get("images")]
    except Exception as e:
        logger.error(f"Image generation service call failed: {e}")
        return []


async def process(user_request: UserRequest, sid: str):
    """Process user request through new 3-step workflow with Socket.IO updates"""
    
    try:
        async def on_update(msg: str):
            try:
                await sio.emit('update', msg, room=sid)
            except Exception as _:
                pass
            
            
        request = user_request.model_dump()
        logger.info(f"User Request: {request}")
        
        test1_intent = [
            'test1',
            'at the grocery store',
            'in the grocery store',
            'grocery store',
            'what should i buy',
            '마트에 왔는데 뭐 사야',
            "나 지금 마트에",
            "나 지금 마트인데",
            '지금 마트인데',
            '오늘 뭐 사야',
        ]
        if user_request.intent == 'test1' or any(intent in user_request.intent.lower() for intent in test1_intent):
            with open('demo/demo1.json') as fr:
                demo1 = json.load(fr)
            
            await on_update("I’m finding<br>what you need<br>for shopping")
            await on_update("Searching notes<br>for market list<br>in Notes")
            await sio.emit('standby', 'standby', room=sid)
            await sio.emit('result', demo1, room=sid)
            return
        
        list_of_intent = [
            'recommend a snack for the movie night',
            'recommenda a snack for the movie night',
            'snack for the movie night',
            'snack for movie night',
            'suggest a snack for the movie',
            'movie night based on',
            'recommenda a snack for the movie night',
            'snack for the movie night',
            'snack for movie night',
            'suggest a snack for the movie',
            'movie night based on',
            'snack for movie night',
            'suggest a snack for the movie',
            'movie night based on',
            
        ]
        if user_request.intent == 'test2' or any(intent in user_request.intent.lower() for intent in list_of_intent):
            with open('demo/demo2.json') as fr:
                demo1 = json.load(fr)
                
            await on_update("Checking<br>today’s steps<br>in Samsung Health")
            await on_update("I'm reviewing<br>your past snack<br>purchase history")
            await sio.emit('standby', 'standby', room=sid)
            await sio.emit('result', demo1, room=sid)
            return
        
        if 1 == random.randint(1,5):
            await on_update("Thinking about<br>how I can<br>help best.")
        else:
            selected_p1 = await choose_expression(
                    data=user_request.model_dump_json(),
                    candidates=AGENT_EXPRESSIONS.get("p1") or [],
                    model_name='gpt-4.1-nano'
                )
            await on_update(selected_p1)
        
        # Step 1: MCP Data Collection
        user_data = await mcp_user_service.process_request(
                request,
                # model='claude-opus-4-20250514',
                model='claude-3-5-haiku-20241022',
                on_update=on_update,    
                multi_agent_expression=AGENT_EXPRESSIONS
        )
        
        
        # Before UI Code Generation
        candidates = (AGENT_EXPRESSIONS.get("p4") or []) + (AGENT_EXPRESSIONS.get("p5") or [])
        selected_p45 = await choose_expression(
                data=user_request.intent,
                candidates=candidates,
                model_name='gpt-4.1-mini'
            )
        await on_update(selected_p45)
        
        # Add fixed layouts first (top, button) - bottom is now classified via LLM
        layout_result = {}
        for layout_type in ["top", "button", "bottom"]:
            fixed_layout_list = layout_classifier.fixed_layouts.get(layout_type)
            if fixed_layout_list:
                fixed_layout = random.choice(fixed_layout_list)
                layout_result[layout_type] = {
                    "id": fixed_layout["id"],
                    "name": fixed_layout["name"],
                    "layout_data": fixed_layout["layout_data"]
                }
        try:
            # Step 2: Layout Classification
            # Classify by content types order
            selected_list = await layout_classifier.classify_layouts(
                intent=user_request.intent,
                context=user_request.context,
                user_data='\n'.join([str(data) for data in user_data]),
                slots=["middle"],
                model_name='gpt-5-nano'
            )
            # Assign using generic keys: first occurrence of each type uses its type name
            # If list contains duplicates of a type in future, you may adapt naming here
            keys_in_order = ["middle"]
            for idx, sel in enumerate(selected_list or []):
                if not sel:
                    continue
                key = keys_in_order[idx] if idx < len(keys_in_order) else f"slot_{idx}"
                layout_result[key] = {
                    "id": sel["id"],
                    "name": sel["name"],
                    "layout_data": sel["layout_data"]
                }
        except Exception as e:
            logger.error(f"Layout classification error: {e}")
            await sio.emit('update', f"step2_error: Layout classification failed: {str(e)} (fallback to default) ({datetime.now().isoformat()})", room=sid)
            # Fallback to default (first middle layout + fixed layouts)
            demo_summary = layout_classifier.get_demo_layouts_summary()
            
            # Default middle layout
            if demo_summary["middle_layouts"]:
                first_middle = layout_classifier.get_layout_by_id(demo_summary["middle_layouts"][0]["id"])
                if first_middle:
                    layout_result["middle"] = {
                        "id": first_middle["id"],
                        "name": first_middle["name"],
                        "layout_data": first_middle["layout_data"]
                    }
            # Default bottom from fixed bottom pool if available
            bottom_pool = (layout_classifier.fixed_layouts or {}).get("bottom", [])
            if bottom_pool and "bottom" not in layout_result:
                b = bottom_pool[0]
                layout_result["bottom"] = {"id": b["id"], "name": b["name"], "layout_data": b["layout_data"]}
                    
        logger.info("Selected Layouts: {}", [f"{t}:{info['id']}" for t, info in layout_result.items()])
        
        # Step 3: Data Mapping (then image search based on mapped data)
        try:
            # 1) 항상 매핑을 먼저 수행
            mapped_params_all = await data_mapper.map_all_layouts_to_parameters(
                layouts=layout_result,
                intent=user_request.intent,
                context=user_request.context,
                user_data_text='\n'.join([str(data) for data in user_data]),
                model_name='gpt-4.1-mini'
            )

            # 2) 매핑된 데이터와 스키마를 활용해 이미지 검색 대상 경로를 수집
            img_paths_by_slot = {}
            for slot, info in layout_result.items():
                try:
                    layout_data = (info or {}).get("layout_data", {})
                    schema = data_mapper.extract_parameters_schema(layout_data) or {}
                    data_obj = (mapped_params_all or {}).get(slot) or {}
                    paths = find_image_tool_paths_by_schema_and_data(schema, data_obj)
                    if paths:
                        img_paths_by_slot[slot] = paths
                except Exception as e:
                    logger.warning(f"Failed to collect image tool paths for slot {slot}: {e}")

            has_img_paths = any(isinstance(v, list) and v for v in img_paths_by_slot.values())

            # 3) 경로가 있으면 프롬프트 생성 후 이미지 생성 서버 호출 (완전 순차)
            prompts_by_key = {}
            img_requests, img_index_map = [], []
            if has_img_paths:
                prompts_by_key = await suggest_image_prompts_by_path(
                    intent=user_request.intent,
                    context=user_request.context,
                    layout_result=layout_result,
                    mapped_params_all=mapped_params_all,
                    img_paths_by_slot=img_paths_by_slot,
                    model_name='gpt-4.1-mini'
                )

                img_requests, img_index_map = build_image_generation_requests_for_paths(
                    img_paths_by_slot,
                    user_request.intent,
                    user_request.context,
                    default_width=1024,
                    default_height=1024,
                    model="dalle",
                    prompts_by_key=prompts_by_key
                )

                logger.info(f"Running image generation ({len(img_requests)} image requests) after mapping")
                image_urls = await call_image_service(
                    service_url="http://0.0.0.0:8000/generate",
                    requests_payload=img_requests
                )
            else:
                logger.info("No image generation needed")
                image_urls = []

            # 4) 최종 결과 조립: {slot: {data, html}}
            final_result = {}
            for key, info in layout_result.items():
                layout_data = info["layout_data"]
                final_result[key] = {
                    "data": mapped_params_all.get(key, layout_data.get("sample", {})),
                    "html": layout_data.get("html", "<div>No HTML available</div>")
                }

            # 5) 생성된 이미지를 해당 경로에 주입
            if image_urls and img_index_map:
                try:
                    for idx, (slot, path) in enumerate(img_index_map):
                        if idx >= len(image_urls):
                            break
                        url = image_urls[idx]
                        if not isinstance(url, str) or not slot:
                            continue
                        slot_obj = final_result.setdefault(slot, {"data": {}, "html": ""})
                        data_obj = slot_obj.setdefault("data", {})
                        set_value_at_path(data_obj, path, url)
                except Exception as e:
                    logger.warning(f"Failed to inject image URLs into final_result: {e}")

            # 6) 검증 로그: 프롬프트 사용/주입 정확도
            try:
                if img_index_map:
                    sample_prompts = []
                    for i, (slot, path) in enumerate(img_index_map[:10]):
                        key = f"{slot}|{_path_to_str(path)}"
                        sample_prompts.append({"slot": slot, "path": _path_to_str(path), "prompt": (prompts_by_key or {}).get(key)})
                    logger.info(f"Image prompt samples: {sample_prompts}")

                if image_urls and img_index_map:
                    paths_by_slot = {}
                    for slot, path in img_index_map:
                        paths_by_slot.setdefault(slot, []).append(path)
                    validate_image_injection(final_result, paths_by_slot)
            except Exception as e:
                logger.warning(f"Image injection validation failed: {e}")

        except Exception as e:
            logger.error(f"Data mapping error: {e}")
            # On error, use the selected layouts as-is, matching the required shape
            final_result = {}
            for layout_type, layout_info in layout_result.items():
                final_result[layout_type] = {
                    "data": {},
                    "html": layout_info["layout_data"].get("html", "<div>Error loading layout</div>")
                }
        
        # Bottom validation 및 구조 수정
        final_result = validate_and_fix_bottom_structure(final_result)
        
        await sio.emit('standby', 'standby', room=sid)
        
        # Final result: send UI code as structured payload
        await sio.emit('result', final_result, room=sid)
        logger.info("Completed about intent: {}", user_request.intent)
        
    except asyncio.CancelledError:
        # Graceful cancellation: do not emit error, just log
        logger.info(f"Workflow cancelled for sid={sid}")
        raise
    except Exception as e:
        logger.error(f"Workflow error: {str(e)}")
        await sio.emit('result', f"error: {str(e)} ({datetime.now().isoformat()})", room=sid)

@sio.event
async def client_disconnected(sid, payload):
    """Handle frontend-reported client disconnection to cancel work early.

    Expected payload: { clientId: string, reason?: string, durationMs?: number }
    """
    try:
        payload = payload or {}
        client_id = payload.get('clientId') or payload.get('client_id')
        reason = payload.get('reason')
        duration_ms = payload.get('durationMs') or payload.get('duration_ms')
        if not isinstance(client_id, str):
            return
        logger.info(f"[DISCONNECT] {{'clientId': '{client_id}', 'reason': '{reason}', 'durationMs': {duration_ms}}}")
        await cancel_session_by_client_id(client_id, reason=reason or 'client_disconnected', duration_ms=duration_ms)
    except Exception as e:
        logger.warning(f"client_disconnected handler error: {e}")

async def connect(sid, environ):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    await sio.emit('update', f"connected: Connected to MCP Host server ({datetime.now().isoformat()})", room=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")
    await cancel_session_by_sid(sid, reason="socketio_disconnect")

@sio.event
async def query(sid, data):
    """Handle query event from client"""
    logger.info(f"Query received from {sid}: {data}")
    
    try:
        # Validate and create user request
        if isinstance(data, dict):
            intent = data.get('intent', '')
            raw_context = data.get('context', {})

            # Frontend may send context as empty string; normalize to dict
            if isinstance(raw_context, str):
                if raw_context.strip() == '' or raw_context.strip().lower() in ('null', 'none', 'undefined'):
                    context = {}
                else:
                    try:
                        parsed_ctx = json.loads(raw_context)
                        context = parsed_ctx if isinstance(parsed_ctx, dict) else {}
                    except Exception:
                        context = {}
            elif isinstance(raw_context, dict):
                context = raw_context
            else:
                context = {}
        else:
            intent = str(data)
            context = {}
        
        if not intent:
            await sio.emit('result', f"error: Intent is required ({datetime.now().isoformat()})", room=sid)
            return
        
        # Ensure current time is included in the request context
        safe_context = dict(context or {})
        now_dt = datetime.now()
        safe_context['current_time'] = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        safe_context['current_iso'] = now_dt.isoformat()
        safe_context['current_unix'] = int(time.time())
        safe_context['current_location'] = "Seocho-gu, Seoul, Republic of Korea"

        user_request = UserRequest(intent=intent, context=safe_context)
        
        # Optional: map provided clientId for later cancellation
        client_id = None
        if isinstance(data, dict):
            client_id = data.get('clientId') or data.get('client_id')
        _register_client_mapping(sid, client_id)
        
        # Run process as background task to enable cancellation
        task = asyncio.create_task(process(user_request, sid))
        active_sessions[sid] = {"task": task, "client_id": client_id, "started_at": time.time()}
        
        def _done_cb(t: asyncio.Task):
            # Cleanup when task finishes
            session = active_sessions.get(sid)
            if session and session.get("task") is t:
                active_sessions.pop(sid, None)
        task.add_done_callback(_done_cb)
        
    except Exception as e:
        logger.error(f"Error processing query from {sid}: {str(e)}")
        await sio.emit('result', {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, room=sid)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    mcp_user_status = "connected" if mcp_user_service.is_connected else "disconnected"
    
    return {
        "status": "healthy",
        "mcp_user_service_status": mcp_user_status,
        "server_type": "Socket.IO",
        "timestamp": time.time()
    }

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    import uvicorn
    
    logger.info("Starting Socket.IO MCP Host server...")
    
    uvicorn.run(
        socket_app,  # Use socket_app instead of app
        host="0.0.0.0",
        port=8001,
        reload=False,  # Socket.IO and reload may have compatibility issues
        log_level="info"
    )