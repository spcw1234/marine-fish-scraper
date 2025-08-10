# Design Document

## Overview

안정적인 관상용 해수어 이미지 스크래핑 시스템을 모듈화된 아키텍처로 설계합니다. 각 모듈은 독립적으로 작동하며, 강력한 에러 처리와 복구 메커니즘을 포함합니다. 파일 손상을 방지하기 위해 원자적 파일 작업과 백업 시스템을 구현합니다.

## Architecture

### Core Components

1. **ScraperCore**: 메인 스크래핑 엔진
2. **ImageDownloader**: 이미지 다운로드 및 검증
3. **TaxonomyManager**: 분류학적 데이터 관리
4. **DatasetManager**: 데이터셋 생성 및 관리
5. **AnalyticsEngine**: 통계 및 분석
6. **ConfigManager**: 설정 관리
7. **ErrorHandler**: 에러 처리 및 로깅

### Module Interaction Flow

```
User Interface
    ↓
ScraperCore ←→ ConfigManager
    ↓
TaxonomyManager → ImageDownloader → DatasetManager
    ↓                    ↓               ↓
ErrorHandler ←→ AnalyticsEngine ←→ File System
```

## Components and Interfaces

### 1. ScraperCore

**Purpose**: 전체 스크래핑 프로세스 조율

**Key Methods**:
- `scrape_all_species()`: 전체 종 스크래핑
- `scrape_family(family_name)`: 특정 과 스크래핑
- `resume_scraping()`: 중단된 스크래핑 재개

**Dependencies**: TaxonomyManager, ImageDownloader, ErrorHandler

### 2. ImageDownloader

**Purpose**: 안전한 이미지 다운로드 및 검증

**Key Methods**:
- `download_from_source(url, metadata)`: 단일 소스에서 다운로드
- `validate_image(filepath)`: 이미지 파일 검증
- `handle_duplicates(image_hash)`: 중복 이미지 처리

**Features**:
- 파일 무결성 검증 (해시 체크)
- 원자적 파일 쓰기 (임시 파일 → 최종 파일)
- 자동 재시도 메커니즘
- 대역폭 제한 및 예의 지연

### 3. TaxonomyManager

**Purpose**: 분류학적 데이터와 폴더 구조 관리

**Key Methods**:
- `get_species_info(genus, species)`: 종 정보 조회
- `create_directory_structure()`: 폴더 구조 생성
- `get_common_names(scientific_name)`: 일반명 조회

**Data Structure**:
```python
taxonomy = {
    "class": {
        "order": {
            "family": {
                "genus": {
                    "species": ["common_name1", "common_name2"]
                }
            }
        }
    }
}
```

### 4. DatasetManager

**Purpose**: 훈련 데이터셋 생성 및 관리

**Key Methods**:
- `create_balanced_dataset(samples_per_class)`: 균형잡힌 데이터셋 생성
- `split_dataset(train_ratio, val_ratio, test_ratio)`: 데이터셋 분할
- `export_annotations(format)`: 어노테이션 내보내기

**Features**:
- 계층적 샘플링 (클래스 → 과 → 종)
- 메타데이터 보존
- 다양한 내보내기 형식 지원

### 5. AnalyticsEngine

**Purpose**: 데이터 분석 및 품질 평가

**Key Methods**:
- `analyze_collection()`: 수집 데이터 분석
- `quality_assessment()`: 이미지 품질 평가
- `generate_report()`: 상세 리포트 생성

**Metrics**:
- 종별/과별 이미지 분포
- 이미지 품질 지표 (해상도, 파일 크기, 선명도)
- 수집 성공률 및 소스별 통계

## Data Models

### ImageMetadata
```python
@dataclass
class ImageMetadata:
    filename: str
    source: str
    genus: str
    species: str
    common_names: List[str]
    download_date: datetime
    file_size: int
    resolution: Tuple[int, int]
    hash_md5: str
    quality_score: float
```

### ScrapingSession
```python
@dataclass
class ScrapingSession:
    session_id: str
    start_time: datetime
    target_species: List[str]
    completed_species: List[str]
    failed_species: List[str]
    total_images: int
    status: str  # 'running', 'completed', 'paused', 'failed'
```

## Error Handling

### Error Categories

1. **Network Errors**: 연결 실패, 타임아웃
2. **File System Errors**: 디스크 공간 부족, 권한 문제
3. **Data Validation Errors**: 손상된 이미지, 잘못된 형식
4. **Rate Limiting**: API 제한, 서버 과부하

### Recovery Strategies

1. **Exponential Backoff**: 네트워크 오류 시 점진적 재시도
2. **Circuit Breaker**: 연속 실패 시 일시적 중단
3. **Graceful Degradation**: 일부 소스 실패 시 다른 소스 활용
4. **Session Persistence**: 중단된 작업 재개 가능

### Logging Strategy

```python
# 로그 레벨별 정보
DEBUG: 상세한 실행 흐름
INFO: 주요 진행 상황
WARNING: 복구 가능한 문제
ERROR: 복구 불가능한 오류
CRITICAL: 시스템 중단 수준 오류
```

## Testing Strategy

### Unit Tests
- 각 모듈의 핵심 기능 테스트
- Mock 객체를 사용한 외부 의존성 격리
- 에러 조건 및 경계값 테스트

### Integration Tests
- 모듈 간 상호작용 테스트
- 실제 파일 시스템 작업 테스트
- 네트워크 연결 테스트 (제한적)

### End-to-End Tests
- 전체 스크래핑 워크플로우 테스트
- 데이터셋 생성 및 검증
- 복구 시나리오 테스트

### Performance Tests
- 대량 이미지 처리 성능
- 메모리 사용량 모니터링
- 동시성 처리 테스트

## Configuration Management

### Config Structure
```json
{
  "scraping": {
    "max_images_per_species": 1000,
    "concurrent_downloads": 5,
    "retry_attempts": 3,
    "delay_between_requests": 1.0
  },
  "sources": {
    "fishbase": {"enabled": true, "weight": 0.4},
    "google_images": {"enabled": true, "weight": 0.3},
    "reef2reef": {"enabled": true, "weight": 0.2},
    "flickr": {"enabled": true, "weight": 0.1}
  },
  "quality": {
    "min_file_size": 5000,
    "max_file_size": 10485760,
    "min_resolution": [200, 200],
    "allowed_formats": [".jpg", ".jpeg", ".png"]
  }
}
```

## Security Considerations

1. **Rate Limiting**: 서버 부하 방지를 위한 요청 제한
2. **User Agent Rotation**: 차단 방지를 위한 다양한 User-Agent 사용
3. **Robots.txt Compliance**: 웹사이트 정책 준수
4. **Data Privacy**: 개인정보가 포함된 이미지 필터링

## Scalability Design

1. **Modular Architecture**: 독립적인 모듈로 수평 확장 가능
2. **Async Processing**: 비동기 처리로 성능 최적화
3. **Batch Processing**: 대량 데이터 처리를 위한 배치 시스템
4. **Resource Management**: 메모리 및 디스크 사용량 최적화