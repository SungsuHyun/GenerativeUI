import os
import json
from typing import Dict, Any, Optional
from loguru import logger
from .llm import call_llm

class DataMapper:
    """
    선택된 레이아웃의 파라미터를 LLM을 통해서만 매핑하는 클래스
    """
    
    def __init__(self):
        pass
    
    def extract_parameters_schema(self, layout_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """레이아웃 JSON에서 parameters 스키마를 일관되게 추출한다.

        일부 레이아웃은 최상위에 `parameters` 키가 있고, 일부는 `properties.parameters` 아래에 정의되어 있음.
        없으면 None 반환.
        """
        if not isinstance(layout_data, dict):
            return None
        if "parameters" in layout_data and isinstance(layout_data.get("parameters"), dict):
            return layout_data.get("parameters")
        # footer 등 스키마가 properties 하위에 존재
        props = layout_data.get("properties")
        if isinstance(props, dict):
            parameters = props.get("parameters")
            if isinstance(parameters, dict):
                return parameters
        return None

    def _parse_json_from_text(self, text: str) -> Any:
        """응답 텍스트에서 JSON 객체를 최대한 견고하게 파싱한다."""
        import json as _json
        text = (text or "").strip()
        # 코드펜스 제거
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        # 바로 파싱 시도
        try:
            return _json.loads(text)
        except Exception:
            pass
        # 중괄호 범위를 찾아 파싱
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return _json.loads(text[start:end+1])
        except Exception:
            pass
        # 배열로 감싼 경우 첫 객체 뽑기
        try:
            start = text.find("[")
            end = text.rfind("]")
            if start != -1 and end != -1 and end > start:
                arr = _json.loads(text[start:end+1])
                if isinstance(arr, list) and arr:
                    return arr[0]
        except Exception:
            pass
        raise ValueError("Failed to parse JSON from text")

    async def map_all_layouts_to_parameters(self,
                                            layouts: Dict[str, Dict[str, Any]],
                                            intent: str,
                                            context: Dict[str, Any],
                                            user_data_text: str,
                                            model_name: str) -> Dict[str, Any]:
        """
        하나의 LLM 호출로 top/middle/bottom/button 4개 레이아웃의 파라미터를 동시에 산출한다.

        layouts: {
          "top": {"layout_data": {...}, "id": ..., "name": ...},
          "middle": {...},
          "bottom": {...},
          "button": {...}
        }
        반환: {"top": {...}, "middle": {...}, "bottom": {...}, "button": {...}}
        """
        # 준비: 각 슬롯별 스키마/설명/샘플 수집
        def _slot(key: str) -> Dict[str, Any]:
            info = layouts.get(key) or {}
            data = info.get("layout_data") or {}
            return {
                "schema": self.extract_parameters_schema(data) or {},
                "desc": data.get("description", "")
            }

        slots = {k: _slot(k) for k in ["top", "middle", "bottom", "button"]}

        prompt = self._build_4layouts_prompt(
            intent=intent,
            context=context,
            user_data_text=user_data_text,
            top_desc=slots["top"]["desc"],
            mid_desc=slots["middle"]["desc"],
            bottom_desc=slots["bottom"]["desc"],
            button_desc=slots["button"]["desc"],
            top_schema=slots["top"]["schema"],
            mid_schema=slots["middle"]["schema"],
            bottom_schema=slots["bottom"]["schema"],
            button_schema=slots["button"]["schema"],
        )

        try:
            response_text = await call_llm(prompt, model_name=model_name)
            parsed = self._parse_json_from_text(response_text) or {}
            if not isinstance(parsed, dict):
                raise ValueError("4-layouts mapping result is not a JSON object")
        except Exception as e:
            logger.error(f"4-layouts 매핑 호출 실패: {e}")
            parsed = {}

        # 키 보정 및 폴백 처리
        result: Dict[str, Any] = {}
        for key in ["top", "middle", "bottom", "button"]:
            value = parsed.get(key)
            if not isinstance(value, dict):
                # 스키마가 있더라도 sample은 사용하지 않음. 빈 객체로 폴백
                value = {}
            result[key] = value

        return result

    def _build_4layouts_prompt(self,
                               intent: str,
                               context: Dict[str, Any],
                               user_data_text: str,
                               top_desc: str,
                               mid_desc: str,
                               bottom_desc: str,
                               button_desc: str,
                               top_schema: Dict[str, Any],
                               mid_schema: Dict[str, Any],
                               bottom_schema: Dict[str, Any],
                               button_schema: Dict[str, Any]) -> str:
        """core/prompt/data_mapping_4layouts_en.txt 템플릿을 불러와 플레이스홀더를 치환한다."""
        template_paths = [
            os.path.join("core/prompt", "data_mapping_4layouts_en.txt"),
            os.path.join(os.path.dirname(__file__), "..", "core/prompt", "data_mapping_4layouts_en.txt"),
        ]

        template_content = None
        for path in template_paths:
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        template_content = f.read()
                        break
            except Exception as e:
                logger.warning(f"Failed to read 4-layouts prompt template at {path}: {e}")

        if not template_content:
            # 최소 동작 보장용 인라인 템플릿
            template_content = (
                "You are a UI parameter mapping assistant. Output JSON with keys top/middle/bottom/button.\n\n"
                "Intent:\n{{INTENT}}\n\nContext:\n{{CONTEXT}}\n\nUser Data:\n{{USER_DATA}}\n\n"
                "TOP desc:\n{{DESC_TOP}}\nMIDDLE desc:\n{{DESC_MIDDLE}}\nBOTTOM desc:\n{{DESC_BOTTOM}}\nBUTTON desc:\n{{DESC_BUTTON}}\n\n"
                "TOP schema:\n{{SCHEMA_TOP}}\nMIDDLE schema:\n{{SCHEMA_MIDDLE}}\nBOTTOM schema:\n{{SCHEMA_BOTTOM}}\nBUTTON schema:\n{{SCHEMA_BUTTON}}\n\n"
                "Rules: JSON only. Follow schema. Short Korean text.\n"
            )

        def _js(v: Any) -> str:
            return json.dumps(v, ensure_ascii=False, indent=2)

        prompt = template_content
        prompt = prompt.replace("{{INTENT}}", str(intent))
        prompt = prompt.replace("{{CONTEXT}}", _js(context))
        prompt = prompt.replace("{{USER_DATA}}", str(user_data_text))
        prompt = prompt.replace("{{DESC_TOP}}", str(top_desc or ""))
        prompt = prompt.replace("{{DESC_MIDDLE}}", str(mid_desc or ""))
        prompt = prompt.replace("{{DESC_BOTTOM}}", str(bottom_desc or ""))
        prompt = prompt.replace("{{DESC_BUTTON}}", str(button_desc or ""))
        prompt = prompt.replace("{{SCHEMA_TOP}}", _js(top_schema or {}))
        prompt = prompt.replace("{{SCHEMA_MIDDLE}}", _js(mid_schema or {}))
        prompt = prompt.replace("{{SCHEMA_BOTTOM}}", _js(bottom_schema or {}))
        prompt = prompt.replace("{{SCHEMA_BUTTON}}", _js(button_schema or {}))
        return prompt

