"""
Advanced logging system for marine scraper
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json

class ColoredFormatter(logging.Formatter):
    """컬러 로그 포매터"""
    # ANSI 색상 코드
    COLORS = {
        'DEBUG': '\033[36m',     # 청록색
        'INFO': '\033[32m',      # 녹색
        'WARNING': '\033[33m',   # 노란색
        'ERROR': '\033[31m',     # 빨간색
        'CRITICAL': '\033[35m',  # 자주색
        'RESET': '\033[0m'       # 리셋
    }
    
    def format(self, record):
        # 색상 적용
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        # 기본 포맷팅
        return super().format(record)

class ScrapingLogger:
    """스크래핑 전용 로거"""
    
    def __init__(self, name: str = "marine_scraper", log_dir: Optional[str] = None):
        self.name = name
        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # 로거 생성
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 기존 핸들러 제거 (중복 방지)
        self.logger.handlers.clear()
        
        # 핸들러 설정
        self._setup_handlers()
        
        # 통계 추적
        self.stats = {
            'debug': 0,
            'info': 0,
            'warning': 0,
            'error': 0,
            'critical': 0
        }
    
    def _setup_handlers(self):
        """로그 핸들러 설정"""
        # 1. 콘솔 핸들러 (컬러 출력)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = ColoredFormatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # 2. 파일 핸들러 (상세 로그)
        log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # 3. 에러 전용 파일 핸들러
        error_file = self.log_dir / f"{self.name}_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        self.logger.addHandler(error_handler)
    
    def debug(self, message: str, **kwargs):
        """디버그 로그"""
        self.stats['debug'] += 1
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """정보 로그"""
        self.stats['info'] += 1
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """경고 로그"""
        self.stats['warning'] += 1
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """에러 로그"""
        self.stats['error'] += 1
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """치명적 에러 로그"""
        self.stats['critical'] += 1
        self.logger.critical(message, **kwargs)
    
    def log_scraping_start(self, species_count: int, target_images: int):
        """스크래핑 시작 로그"""
        self.info(f"🚀 스크래핑 시작 - 대상 종: {species_count}개, 목표 이미지: {target_images}장")
    
    def log_species_start(self, genus: str, species: str):
        """종별 스크래핑 시작 로그"""
        self.info(f"🔍 {genus} {species} 스크래핑 시작")
    
    def log_species_complete(self, genus: str, species: str, downloaded: int):
        """종별 스크래핑 완료 로그"""
        self.info(f"✅ {genus} {species} 완료 - {downloaded}장 다운로드")
    
    def log_source_result(self, source: str, genus: str, species: str, count: int):
        """소스별 결과 로그"""
        if count > 0:
            self.debug(f"  📥 {source}: {genus} {species} - {count}장")
        else:
            self.debug(f"  ❌ {source}: {genus} {species} - 이미지 없음")
    
    def log_download_error(self, url: str, error: str):
        """다운로드 에러 로그"""
        self.warning(f"다운로드 실패: {url} - {error}")
    
    def log_file_error(self, filepath: str, error: str):
        """파일 작업 에러 로그"""
        self.error(f"파일 작업 실패: {filepath} - {error}")
    
    def log_session_save(self, session_id: str):
        """세션 저장 로그"""
        self.debug(f"세션 저장: {session_id}")
    
    def log_session_restore(self, session_id: str):
        """세션 복원 로그"""
        self.info(f"세션 복원: {session_id}")
    
    def get_stats(self) -> dict:
        """로그 통계 반환"""
        return self.stats.copy()
    
    def save_stats(self):
        """통계를 파일로 저장"""
        stats_file = self.log_dir / f"{self.name}_stats_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'stats': self.stats
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.error(f"통계 저장 실패: {e}")
    
    def print_summary(self):
        """로그 요약 출력"""
        total = sum(self.stats.values())
        if total > 0:
            self.info("📊 로그 통계:")
            for level, count in self.stats.items():
                if count > 0:
                    percentage = (count / total) * 100
                    self.info(f"  {level.upper()}: {count}개 ({percentage:.1f}%)")

# 전역 로거 인스턴스
_global_logger: Optional[ScrapingLogger] = None

def get_logger(name: str = "marine_scraper", log_dir: Optional[str] = None) -> ScrapingLogger:
    """전역 로거 인스턴스 반환"""
    global _global_logger
    if _global_logger is None:
        _global_logger = ScrapingLogger(name, log_dir)
    return _global_logger

def setup_logging(name: str = "marine_scraper", log_dir: Optional[str] = None) -> ScrapingLogger:
    """로깅 시스템 초기화"""
    global _global_logger
    _global_logger = ScrapingLogger(name, log_dir)
    return _global_logger