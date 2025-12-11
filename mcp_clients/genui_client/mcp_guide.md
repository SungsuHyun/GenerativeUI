# MCP GenUI Client 가이드

## 개요

MCP GenUI Client는 UI 요구사항 생성에 특화된 MCP (Model Context Protocol) 기반 클라이언트입니다. 
사용자의 의도, 컨텍스트, 데이터를 분석하여 최적의 UI 요구사항을 정의하는 서비스를 제공합니다.

## 주요 특징

- **외부 MCP 서버 전용**: mcp_servers.json 설정만 사용
- **UI 특화 프롬프트**: UI/UX 요구사항 분석에 최적화된 시스템 프롬프트
- **스트리밍 지원**: 실시간 진행 상황 및 tool 실행 결과 스트리밍
- **병렬 처리**: 여러 MCP 도구를 동시에 실행하여 성능 최적화
- **간단한 구조**: 핵심 기능에 집중한 경량화된 구조
- **유연한 확장**: 새로운 MCP 서버 추가 용이

## 디렉토리 구조

```
mcp_genui_client/
├── __init__.py                     # 패키지 초기화
├── genui_service.py               # 메인 서비스 로직
├── mcp_servers.json     # 외부 MCP 서버 설정
├── core/
│   ├── __init__.py               # Core 패키지 초기화
│   ├── client.py                 # MCP 클라이언트 구현
│   ├── manager.py                # MCP 매니저
│   └── genui_client_system_prompt.txt  # 시스템 프롬프트
└── mcp_guide.md                   # 이 가이드 문서
```

## 사용법

### 1. 서비스 초기화

```python
from mcp_genui_client import MCPGenUIService, GenUIRequest

# 서비스 생성
genui_service = MCPGenUIService()

# 초기화 (MCP 서버 연결)
await genui_service.initialize()
```

### 2. UI 요구사항 생성 (기본)

```python
# 요청 생성
request = GenUIRequest(
    intent="사용자가 원하는 기능이나 목적",
    context={"key": "value"},  # 추가 컨텍스트
    user_data="분석할 사용자 데이터"
)

# UI 요구사항 생성
response = await genui_service.generate_ui_requirements(request)
print(response.ui_requirements)
```

### 3. UI 요구사항 생성 (스트리밍)

```python
# 스트리밍으로 실시간 진행 상황 확인
async for chunk in genui_service.generate_ui_requirements_stream(request):
    print(f"📦 {chunk}")
    
    # 이벤트 파싱
    try:
        import json
        chunk_data = json.loads(chunk.strip())
        
        if chunk_data.get('event') == 'ui_generation_start':
            print("🚀 UI 생성 시작")
        elif chunk_data.get('event') == 'tool_execution':
            tool_info = chunk_data.get('data', {}).get('tool', {})
            print(f"🔧 도구 실행: {tool_info.get('name')}")
        elif chunk_data.get('event') == 'ui_generation_end':
            final_result = chunk_data.get('data', {}).get('ui_requirements')
            print(f"✅ 완료: {final_result}")
    except json.JSONDecodeError:
        pass
```

### 4. 정리

```python
# 서비스 정리
await genui_service.cleanup()
```

## 스트리밍 이벤트 타입

### ui_generation_start
UI 요구사항 생성 시작을 알림
```json
{"event": "ui_generation_start", "data": "UI requirements generation started"}
```

### tool_execution
MCP 도구 실행 및 결과를 실시간으로 전송
```json
{
  "event": "tool_execution",
  "data": {
    "tool": {
      "name": "server_name.tool_name",
      "arguments": {...}
    },
    "raw_result": "도구 실행 결과"
  }
}
```

### ui_generation_end
최종 UI 요구사항 완성
```json
{
  "event": "ui_generation_end", 
  "data": {
    "ui_requirements": "생성된 UI 요구사항 전체 내용"
  }
}
```

### error
오류 발생시
```json
{"event": "error", "data": "오류 메시지"}
```

## 설정

### mcp_servers.json

외부 MCP 서버들의 설정을 정의합니다:

```json
{
  "mcpServers": {
    "brave-search": {
      "image": "mcp/brave-search",
      "command": "docker",
      "args": [...],
      "env": {...}
    },
    "memory": {
      "image": "mcp/memory",
      "command": "docker",
      "args": [...]
    }
  }
}
```

### 시스템 프롬프트

`core/genui_client_system_prompt.txt`에서 UI 요구사항 생성에 특화된 프롬프트를 설정할 수 있습니다.

## API 참조

### MCPGenUIService

#### 메서드

- `initialize()`: MCP 서버 연결 초기화
- `cleanup()`: 리소스 정리
- `generate_ui_requirements(request)`: UI 요구사항 생성
- `list_available_tools()`: 사용 가능한 도구 목록
- `reconnect()`: 연결 재시도

#### 속성

- `is_connected`: 연결 상태 확인

### GenUIRequest

- `intent`: 사용자 의도 (필수)
- `context`: 추가 컨텍스트 (선택)
- `user_data`: 사용자 데이터 (선택)

### GenUIResponse

- `status`: 처리 상태
- `intent_received`: 받은 의도
- `context_received`: 받은 컨텍스트
- `user_data_received`: 받은 사용자 데이터
- `ui_requirements`: 생성된 UI 요구사항
- `processing_time`: 처리 시간

## 오류 처리

### MCPGenUIManagerError

MCP GenUI 매니저와 관련된 오류를 처리합니다:

- 서버 연결 실패
- 설정 파일 문제
- UI 요구사항 생성 실패

### MCPGenUIClientError

MCP GenUI 클라이언트 레벨의 오류를 처리합니다:

- 서버 통신 문제
- 도구 실행 오류
- 응답 파싱 문제

## 로깅

loguru를 사용하여 상세한 로깅을 제공합니다:

```python
logger.info("MCP GenUI 서비스 초기화 완료")
logger.error("UI 요구사항 생성 실패: {error}")
```

## 확장

새로운 MCP 서버를 추가하려면:

1. `mcp_servers.json`에 서버 설정 추가
2. 필요한 환경 변수 설정
3. 서비스 재시작

## 주의사항

- 환경 변수 (.env 파일)에 API 키 등 민감한 정보 저장
- 적절한 타임아웃 설정으로 안정성 확보
- 서버 연결 상태 주기적 모니터링 권장 