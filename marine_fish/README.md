# Marine Fish Scraper

고급 해양어류 이미지 스크래핑 시스템

## 🐠 개요

Marine Fish Scraper는 다양한 해양어류 종의 이미지를 자동으로 수집하고 분류하는 고급 스크래핑 시스템입니다. 분류학적 체계를 기반으로 체계적인 데이터 수집과 관리를 제공합니다.

## ✨ 주요 기능

- **분류학적 체계 기반**: 과학적 분류 체계에 따른 체계적 데이터 수집
- **다중 소스 지원**: 여러 이미지 소스에서 동시 수집
- **품질 관리**: 이미지 품질 검증 및 중복 제거
- **세션 관리**: 중단된 작업 재시작 및 진행 상황 추적
- **메타데이터 관리**: 상세한 이미지 메타데이터 자동 생성
- **에러 처리**: 고급 에러 처리 및 재시도 메커니즘

## 🚀 빠른 시작

### 설치

```bash
# 의존성 설치
pip install -r requirements.txt
```

### 기본 사용법

```bash
# 특정 종 스크래핑
python main.py --species "Amphiprion ocellaris" --count 50

# 특정 속의 모든 종 스크래핑  
python main.py --genus "Amphiprion" --count 30

# 특정 과의 모든 종 스크래핑
python main.py --family "Pomacentridae" --count 20

# 모든 종 스크래핑
python main.py --all --count 10
```

### 고급 옵션

```bash
# 사용자 정의 설정 파일 사용
python main.py --config custom_config.json --species "Paracanthurus hepatus"

# 중단된 세션 재시작
python main.py --resume session_abc123

# 저장된 세션 목록 확인
python main.py --list-sessions

# 시뮬레이션 모드 (실제 다운로드 없음)
python main.py --dry-run --family "Acanthuridae"

# 상세 로그 출력
python main.py --verbose --species "Zebrasoma flavescens"
```

## 📁 프로젝트 구조

```
marine_fish/
├── main.py                 # 메인 진입점
├── config_manager.py       # 설정 관리
├── marine_scraper.py       # 메인 스크래퍼 클래스
├── scraper_core.py         # 핵심 스크래핑 로직
├── taxonomy_manager.py     # 분류학적 데이터 관리
├── image_downloader.py     # 이미지 다운로드 엔진
├── image_metadata.py       # 이미지 메타데이터 모델
├── session_manager.py      # 세션 관리
├── logger.py              # 로깅 시스템
├── error_handler.py       # 에러 처리 시스템
├── requirements.txt       # 의존성 목록
├── dataset/              # 다운로드된 이미지 저장소
├── metadata/             # 메타데이터 저장소
└── sessions/             # 세션 데이터 저장소
```

## ⚙️ 설정

`config.json` 파일을 통해 다양한 설정을 조정할 수 있습니다:

```json
{
  "scraping": {
    "concurrent_downloads": 3,
    "delay_between_requests": 1.0,
    "timeout_seconds": 30,
    "max_retries": 3
  },
  "quality": {
    "min_resolution": [200, 200],
    "min_file_size": 10240,
    "max_file_size": 10485760
  },
  "paths": {
    "output_dir": "dataset",
    "metadata_dir": "metadata",
    "sessions_dir": "sessions"
  }
}
```

## 🐟 지원하는 어종

현재 다음과 같은 해양어류 과(Family)를 지원합니다:

- **Pomacentridae** (자리돔과): 클라운피쉬, 크로미스, 댐셀피쉬
- **Acanthuridae** (쥐치과): 탱, 서전피쉬
- **Pomacanthidae** (엔젤피쉬과): 엔젤피쉬
- **Chaetodontidae** (나비고기과): 버터플라이피쉬
- **Tetraodontidae** (복어과): 퍼퍼피쉬
- **Balistidae** (쥐치과): 트리거피쉬
- **Hemiscylliidae** (대나무상어과): 뱀부샤크

## 📊 통계 및 모니터링

스크래핑 진행 상황과 통계를 실시간으로 모니터링할 수 있습니다:

- 종별 다운로드 진행률
- 소스별 성공률
- 이미지 품질 분포
- 에러 발생 통계
- 세션 관리 현황

## 🔧 개발자 가이드

### 새로운 소스 추가

```python
from scraper_core import ScraperCore

class CustomScraper(ScraperCore):
    def search_images(self, genus: str, species: str, limit: int):
        # 커스텀 검색 로직 구현
        pass
```

### 분류 체계 확장

```python
from taxonomy_manager import TaxonomyManager

# 외부 분류 데이터 로드
taxonomy = TaxonomyManager()
taxonomy.load_taxonomy_from_file("custom_taxonomy.json")
```

## 🐛 문제 해결

### 일반적인 문제들

1. **네트워크 연결 오류**: 재시도 메커니즘이 자동으로 처리
2. **이미지 품질 문제**: 품질 설정을 조정하여 해결
3. **중복 이미지**: 해시 기반 중복 제거 자동 적용
4. **세션 복원 실패**: 세션 파일 무결성 확인

### 로그 확인

```bash
# 로그 파일 위치
logs/marine_scraper_YYYYMMDD.log
logs/marine_scraper_errors_YYYYMMDD.log
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요.

---

**Marine Fish Scraper** - 해양 생물 연구와 교육을 위한 고급 이미지 수집 도구