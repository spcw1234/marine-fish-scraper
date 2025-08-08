# 🐠 Marine Fish Image Scraper v2.0

고성능 해양어류 이미지 대량 수집 시스템 - 머신러닝 학습용 데이터셋 생성

## ✨ 주요 기능

- **14개 소스 동시 수집**: FishBase, Google, Bing, Yandex, iNaturalist, Flickr, Wikipedia, EOL, GBIF, WoRMS, Reef2Reef, 수족관 사이트, Pinterest
- **대량 수집**: 종당 최대 1000장 이미지 수집
- **분류학적 체계**: 과학적 분류 체계 기반 자동 분류 (54종 지원)
- **품질 관리**: 해상도, 파일 크기, 중복 제거 자동 처리
- **세션 관리**: 중단된 작업 재시작 가능
- **CLI & GUI**: 명령행 및 인터랙티브 메뉴 지원
- **ML 최적화**: 다양한 각도, 상황, 개체 변화 수집

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone <repository-url>
cd stable-marine-scraper

# 의존성 설치
pip install -r requirements.txt
```

### 2. 실행

```bash
python main.py
```

### 3. 기본 사용법

1. **전체 이미지 다운로드**: 모든 해수어 종의 이미지를 대량 수집
2. **특정 과 다운로드**: 원하는 과(Family)만 선택하여 수집
3. **세션 재개**: 중단된 작업을 이어서 진행
4. **데이터셋 생성**: 머신러닝 훈련용 데이터셋 자동 생성

## 📁 프로젝트 구조

```
stable-marine-scraper/
├── stable_marine_scraper/          # 메인 패키지
│   ├── core/                       # 핵심 모듈
│   │   ├── scraper_core.py        # 메인 스크래핑 엔진
│   │   ├── config_manager.py      # 설정 관리
│   │   ├── taxonomy_manager.py    # 분류학적 데이터 관리
│   │   └── image_downloader.py    # 이미지 다운로드 엔진
│   ├── models/                     # 데이터 모델
│   │   ├── image_metadata.py      # 이미지 메타데이터
│   │   └── scraping_session.py    # 스크래핑 세션
│   ├── scrapers/                   # 소스별 스크래퍼
│   │   ├── fishbase_scraper.py    # FishBase 스크래퍼
│   │   ├── google_images_scraper.py # Google Images 스크래퍼
│   │   ├── reef2reef_scraper.py   # Reef2Reef 스크래퍼
│   │   └── flickr_scraper.py      # Flickr 스크래퍼
│   └── utils/                      # 유틸리티
│       ├── logger.py              # 로깅 시스템
│       ├── error_handler.py       # 에러 처리
│       └── image_validator.py     # 이미지 품질 검증
├── main.py                         # 메인 실행 파일
├── config.json                     # 설정 파일
└── requirements.txt                # 의존성 목록
```

## ⚙️ 설정

`config.json` 파일에서 다양한 설정을 조정할 수 있습니다:

```json
{
  "scraping": {
    "max_images_per_species": 1000,
    "concurrent_downloads": 5,
    "retry_attempts": 3,
    "delay_between_requests": 1.0
  },
  "sources": {
    "fishbase": {"enabled": true, "weight": 0.4, "max_images": 400},
    "google_images": {"enabled": true, "weight": 0.3, "max_images": 300},
    "reef2reef": {"enabled": true, "weight": 0.2, "max_images": 200},
    "flickr": {"enabled": true, "weight": 0.1, "max_images": 100}
  },
  "quality": {
    "min_file_size": 5000,
    "max_file_size": 10485760,
    "min_resolution": [200, 200]
  }
}
```

## 📊 데이터 구조

수집된 이미지는 분류학적 계층구조에 따라 정리됩니다:

```
marine_fish/
├── dataset/                        # 원본 데이터셋
│   ├── Chondrichthyes/            # 연골어류
│   │   └── Carcharhiniformes/     # 목
│   │       └── Hemiscylliidae/    # 과
│   │           └── Chiloscyllium_punctatum/  # 종
│   └── Osteichthyes/              # 경골어류
│       ├── Acanthuriformes/       # 가시고등어목
│       ├── Tetraodontiformes/     # 복어목
│       └── ...
├── train/                          # 훈련용 데이터셋
│   ├── Chondrichthyes/
│   └── Osteichthyes/
├── sessions/                       # 세션 파일들
├── metadata/                       # 메타데이터
└── logs/                          # 로그 파일들
```

## 🔧 고급 기능

### 세션 관리

```python
# 세션 생성
session = scraper.scrape_all_species()

# 세션 재개
session = scraper.scrape_all_species(resume_session="session_id")

# 세션 상태 확인
print(session.get_progress_summary())
```

### 품질 검증

시스템은 다음 기준으로 이미지 품질을 평가합니다:

- **선명도**: Laplacian variance 기반
- **밝기**: 적절한 밝기 범위 확인
- **대비**: 표준편차 기반 대비 측정
- **색상 다양성**: 색상 히스토그램 엔트로피
- **해상도**: 최소/최대 해상도 기준
- **파일 크기**: 적절한 크기 범위

### 에러 처리

- **재시도 메커니즘**: 네트워크 오류 시 자동 재시도
- **Circuit Breaker**: 연속 실패 시 일시적 차단
- **우아한 실패**: 일부 실패가 전체에 영향을 주지 않음
- **에러 로깅**: 상세한 에러 정보 기록

## 📈 성능 최적화

- **병렬 다운로드**: 동시에 여러 이미지 다운로드
- **메모리 효율성**: 스트리밍 다운로드로 메모리 사용량 최소화
- **캐싱**: 중복 검출을 위한 해시 캐싱
- **배치 처리**: 대량 데이터 효율적 처리

## 🛠️ 개발자 가이드

### 경고 및 로깅 설정

시스템은 SSL 및 urllib3 경고를 자동으로 억제하여 깔끔한 콘솔 출력을 제공합니다.

#### config.json에서 로깅 설정

```json
{
  "logging": {
    "suppress_ssl_warnings": true,
    "suppress_urllib3_warnings": true,
    "log_level": "INFO"
  }
}
```

#### 프로그래밍 방식으로 경고 제어

```python
from stable_marine_scraper.utils.warning_suppressor import (
    suppress_urllib3_warnings,
    enable_verbose_warnings,
    configure_warnings
)

# 경고 억제
suppress_urllib3_warnings()

# 디버깅 시 경고 재활성화
enable_verbose_warnings()

# 설정 기반 경고 제어
config = {"logging": {"suppress_urllib3_warnings": True}}
configure_warnings(config)
```

### 새로운 스크래퍼 추가

```python
from stable_marine_scraper.scrapers.base_scraper import BaseScraper

class MyCustomScraper(BaseScraper):
    def search_species_images(self, genus, species, max_images=100):
        # 구현
        pass
```

### 커스텀 품질 검증

```python
from stable_marine_scraper.utils.image_validator import ImageValidator

validator = ImageValidator()
validator.update_quality_thresholds(
    min_sharpness=0.5,
    min_overall_quality=0.6
)
```

## 🐛 문제 해결

### 일반적인 문제들

1. **네트워크 오류**: 재시도 횟수와 지연 시간 조정
2. **메모리 부족**: 동시 다운로드 수 줄이기
3. **디스크 공간**: 정기적인 정리 작업
4. **차단 문제**: User-Agent 로테이션과 지연 시간 증가

### 로그 확인

```bash
# 로그 파일 위치
tail -f logs/marine_scraper_YYYYMMDD.log

# 에러 로그만 확인
tail -f logs/marine_scraper_errors_YYYYMMDD.log
```

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 지원

문제가 발생하면 다음을 확인해주세요:

1. `error_log.json` 파일의 상세 오류 정보
2. `logs/` 폴더의 로그 파일들
3. 설정 파일의 유효성
4. 네트워크 연결 상태

---

**⚠️ 주의사항**: 이 도구는 연구 및 교육 목적으로만 사용해주세요. 웹사이트의 이용약관을 준수하고, 서버에 과도한 부하를 주지 않도록 적절한 지연 시간을 설정해주세요.