# Swagger API Documentation

이 디렉토리에는 FastAPI 애플리케이션의 OpenAPI 스키마 파일들이 포함되어 있습니다.

## 파일 목록

- `openapi.json`: OpenAPI 3.0 스키마 (JSON 형식)
- `openapi.yaml`: OpenAPI 3.0 스키마 (YAML 형식)

## 사용 방법

### 1. Swagger UI로 보기
브라우저에서 다음 URL에 접속하세요:
```
http://localhost:8000/docs
```

### 2. ReDoc으로 보기
브라우저에서 다음 URL에 접속하세요:
```
http://localhost:8000/redoc
```

### 3. 스키마 파일 직접 사용
- JSON 파일: `openapi.json`
- YAML 파일: `openapi.yaml`

이 파일들은 서버 시작 시 자동으로 생성됩니다.
