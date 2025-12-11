"""
Swagger 파일 export 유틸리티
FastAPI 서버 시작 시 자동으로 OpenAPI 스키마를 JSON과 YAML 형식으로 저장합니다.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
from loguru import logger


def ensure_swagger_directory(swagger_dir: str = "swagger") -> Path:
    """Swagger 파일을 저장할 디렉토리를 생성합니다."""
    swagger_path = Path(swagger_dir)
    swagger_path.mkdir(exist_ok=True)
    return swagger_path


def export_openapi_json(app, file_path: str) -> bool:
    """
    FastAPI 앱의 OpenAPI 스키마를 JSON 파일로 export합니다.
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
        file_path: 저장할 JSON 파일 경로
        
    Returns:
        bool: export 성공 여부
    """
    try:
        openapi_schema = app.openapi()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
        
        logger.info(f"OpenAPI JSON 스키마가 성공적으로 export되었습니다: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"OpenAPI JSON export 중 오류 발생: {str(e)}")
        return False


def export_openapi_yaml(app, file_path: str) -> bool:
    """
    FastAPI 앱의 OpenAPI 스키마를 YAML 파일로 export합니다.
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
        file_path: 저장할 YAML 파일 경로
        
    Returns:
        bool: export 성공 여부
    """
    try:
        import yaml
        
        openapi_schema = app.openapi()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(openapi_schema, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"OpenAPI YAML 스키마가 성공적으로 export되었습니다: {file_path}")
        return True
        
    except ImportError:
        logger.warning("PyYAML이 설치되지 않아 YAML export를 건너뜁니다. 'pip install pyyaml'로 설치하세요.")
        return False
    except Exception as e:
        logger.error(f"OpenAPI YAML export 중 오류 발생: {str(e)}")
        return False


def export_swagger_files(app, swagger_dir: str = "swagger") -> Dict[str, bool]:
    """
    FastAPI 앱의 OpenAPI 스키마를 JSON과 YAML 파일로 export합니다.
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
        swagger_dir: Swagger 파일을 저장할 디렉토리
        
    Returns:
        Dict[str, bool]: 각 파일 형식별 export 성공 여부
    """
    results = {}
    
    # 디렉토리 생성
    swagger_path = ensure_swagger_directory(swagger_dir)
    
    # JSON 파일 export
    json_file = swagger_path / "openapi.json"
    results['json'] = export_openapi_json(app, str(json_file))
    
    # YAML 파일 export
    yaml_file = swagger_path / "openapi.yaml"
    results['yaml'] = export_openapi_yaml(app, str(yaml_file))
    
    # 요약 로그
    successful_exports = [fmt for fmt, success in results.items() if success]
    if successful_exports:
        logger.info(f"Swagger 파일 export 완료: {', '.join(successful_exports)} 형식")
    else:
        logger.error("모든 Swagger 파일 export가 실패했습니다.")
    
    return results


def create_swagger_info_file(swagger_dir: str = "swagger") -> bool:
    """
    Swagger 파일에 대한 정보를 담은 README 파일을 생성합니다.
    
    Args:
        swagger_dir: Swagger 파일이 저장된 디렉토리
        
    Returns:
        bool: 파일 생성 성공 여부
    """
    try:
        swagger_path = Path(swagger_dir)
        readme_file = swagger_path / "README.md"
        
        readme_content = """# Swagger API Documentation

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
"""
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.info(f"Swagger README 파일이 생성되었습니다: {readme_file}")
        return True
        
    except Exception as e:
        logger.error(f"Swagger README 파일 생성 중 오류 발생: {str(e)}")
        return False
