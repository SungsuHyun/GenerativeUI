# MCP Host - Generative UI Platform

MCP (Model Context Protocol) Host는 사용자 의도 분석과 UI 생성을 위한 통합 플랫폼입니다.

## 아키텍처

```
사용자 요청 → MCP Host (main.py) → MCP User Client → MCP GenUI Client → UI 결과
                    ↓
            Legacy UI Flow (기존 core 모듈)
```

## 프로젝트 구조

```
mcp_host/
├── main.py                    # 메인 FastAPI 앱 (MCP Host)
├── core/                      # 레거시 UI 생성 모듈
│   ├── __init__.py
│   ├── core.py               # UI 생성 파이프라인
│   ├── generate_planner.py
│   ├── layout_classifier.py
│   ├── component_connector.py
│   ├── ui_generator.py
│   └── prompt/               # 프롬프트 템플릿들
├── mcp_user_client/          # MCP User 클라이언트 (라이브러리)
│   ├── __init__.py
│   ├── client_service.py     # 사용자 의도 분석 서비스
│   └── mcp_client/           # MCP 클라이언트 모듈
│       ├── __init__.py
│       ├── client.py         # MCP 클라이언트 구현
│       ├── manager.py        # MCP 매니저
│       └── pyproject.toml
├── mcp_genui_client/         # MCP GenUI 클라이언트 (라이브러리)
│   ├── __init__.py
│   └── genui_service.py      # UI 생성 서비스
├── logs/                     # 로그 파일들
├── requirements.txt
└── README.md
```

## 워크플로우

### 1. MCP Flow (기본)
1. **MCP User Client**: 사용자 의도를 분석하고 컨텍스트를 파악
2. **MCP GenUI Client**: 분석 결과를 바탕으로 UI 코드 생성

### 2. UI Flow (레거시)
- 기존 `core` 모듈을 사용한 UI 생성 파이프라인

## API 엔드포인트

### POST `/process`
사용자 요청을 처리합니다.

**요청 예시:**
```json
{
  "intent": "사용자의 의도나 질문",
  "context": {"key": "value"},
  "options": {
    "llm_model": "gemini-1.5-flash"
  },
  "workflow": "mcp_flow"  // 또는 "ui_flow"
}
```

**쿼리 파라미터:**
- `stream`: boolean - 스트리밍 응답 여부 (MCP flow만 지원)

### 기타 엔드포인트
- `GET /health` - 서비스 상태 확인
- `GET /mcp/user/tools` - MCP User 도구 목록
- `POST /mcp/user/reconnect` - MCP User 클라이언트 재연결
- `POST /mcp/genui/reconnect` - MCP GenUI 클라이언트 재연결

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 필요한 API 키 설정:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# 환경 설정 (선택적)
ENVIRONMENT=development  # development 또는 production
ENABLE_CLEANUP=false     # 개발 모드에서도 cleanup 강제 실행하려면 true
```

**환경 변수 설명:**
- `ENVIRONMENT`: 개발(`development`) 또는 프로덕션(`production`) 모드 설정
- `ENABLE_CLEANUP`: 개발 모드에서도 MCP 연결 cleanup을 강제로 실행할지 여부

### 3. MCP 서버 설정
`mcp_user_client/mcp_servers.json` 파일에서 외부 MCP 서버들을 설정합니다.

### 4. 서버 실행
```bash
python main.py
```

또는

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 주요 특징

- **통합 워크플로우**: MCP User Client와 MCP GenUI Client를 순차적으로 실행
- **스트리밍 지원**: 실시간 응답 스트리밍 (MCP flow)
- **다중 워크플로우**: MCP flow와 기존 UI flow 지원
- **견고한 에러 처리**: 서비스별 연결 상태 모니터링
- **자동 라이프사이클 관리**: 앱 시작/종료시 자동 초기화/정리
- **상세 로깅**: 모든 처리 과정 로깅

## 개발 노트

- MCP User Client는 외부 MCP 서버들(sequentialthinking, google-maps, time, brave-search, memory, weather 등)과 연동
- MCP GenUI Client는 현재 mock 구현이며, 실제 UI 생성 로직은 추후 구현 예정
- 기존 `core` 모듈은 하위 호환성을 위해 유지됨 