"""
Configuration management system
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ScrapingConfig:
    """스크래핑 관련 설정"""
    max_images_per_species: int = 1000
    concurrent_downloads: int = 5
    retry_attempts: int = 3
    delay_between_requests: float = 1.0
    timeout_seconds: int = 30


@dataclass
class SourceConfig:
    """소스별 설정"""
    enabled: bool = True
    weight: float = 1.0
    max_images: int = 300


@dataclass
class QualityConfig:
    """이미지 품질 설정"""
    min_file_size: int = 5000
    max_file_size: int = 10485760  # 10MB
    min_resolution: tuple = (200, 200)
    allowed_formats: list = None
    
    def __post_init__(self):
        if self.allowed_formats is None:
            self.allowed_formats = [".jpg", ".jpeg", ".png", ".gif"]


class ConfigManager:
    """설정 관리자"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("config.json")
        self.scraping = ScrapingConfig()
        self.sources = {
            "fishbase": SourceConfig(weight=0.4, max_images=400),
            "google_images": SourceConfig(weight=0.3, max_images=300),
            "reef2reef": SourceConfig(weight=0.2, max_images=200),
            "flickr": SourceConfig(weight=0.1, max_images=100)
        }
        self.quality = QualityConfig()
        
        # 설정 파일이 존재하면 로드
        if self.config_path.exists():
            self.load_config()
    
    def load_config(self) -> None:
        """설정 파일 로드"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 스크래핑 설정 로드
            if 'scraping' in config_data:
                scraping_data = config_data['scraping']
                self.scraping = ScrapingConfig(**scraping_data)
            
            # 소스 설정 로드
            if 'sources' in config_data:
                for source_name, source_data in config_data['sources'].items():
                    if source_name in self.sources:
                        self.sources[source_name] = SourceConfig(**source_data)
            
            # 품질 설정 로드
            if 'quality' in config_data:
                quality_data = config_data['quality']
                # tuple 변환 처리
                if 'min_resolution' in quality_data:
                    quality_data['min_resolution'] = tuple(quality_data['min_resolution'])
                self.quality = QualityConfig(**quality_data)
                
        except Exception as e:
            print(f"⚠️ 설정 파일 로드 실패: {e}")
            print("기본 설정을 사용합니다.")
    
    def save_config(self) -> None:
        """설정 파일 저장"""
        try:
            config_data = {
                'scraping': asdict(self.scraping),
                'sources': {name: asdict(config) for name, config in self.sources.items()},
                'quality': asdict(self.quality)
            }
            
            # 임시 파일에 먼저 저장 (원자적 쓰기)
            temp_path = self.config_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            # 성공하면 원본 파일로 이동
            temp_path.replace(self.config_path)
            
        except Exception as e:
            print(f"❌ 설정 파일 저장 실패: {e}")
    
    def get_enabled_sources(self) -> Dict[str, SourceConfig]:
        """활성화된 소스 목록 반환"""
        return {name: config for name, config in self.sources.items() if config.enabled}
    
    def update_source_config(self, source_name: str, **kwargs) -> None:
        """소스 설정 업데이트"""
        if source_name in self.sources:
            for key, value in kwargs.items():
                if hasattr(self.sources[source_name], key):
                    setattr(self.sources[source_name], key, value)
    
    def validate_config(self) -> bool:
        """설정 유효성 검증"""
        try:
            # 기본 검증
            assert self.scraping.max_images_per_species > 0
            assert self.scraping.concurrent_downloads > 0
            assert self.scraping.retry_attempts >= 0
            assert self.scraping.delay_between_requests >= 0
            
            # 품질 설정 검증
            assert self.quality.min_file_size > 0
            assert self.quality.max_file_size > self.quality.min_file_size
            assert len(self.quality.min_resolution) == 2
            assert all(r > 0 for r in self.quality.min_resolution)
            
            # 소스 가중치 검증
            enabled_sources = self.get_enabled_sources()
            if not enabled_sources:
                print("⚠️ 활성화된 소스가 없습니다.")
                return False
            
            total_weight = sum(config.weight for config in enabled_sources.values())
            if total_weight <= 0:
                print("⚠️ 소스 가중치 합계가 0 이하입니다.")
                return False
            
            return True
            
        except AssertionError as e:
            print(f"❌ 설정 검증 실패: {e}")
            return False
    
    def reset_to_defaults(self) -> None:
        """기본 설정으로 초기화"""
        self.scraping = ScrapingConfig()
        self.sources = {
            "fishbase": SourceConfig(weight=0.4, max_images=400),
            "google_images": SourceConfig(weight=0.3, max_images=300),
            "reef2reef": SourceConfig(weight=0.2, max_images=200),
            "flickr": SourceConfig(weight=0.1, max_images=100)
        }
        self.quality = QualityConfig()
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환"""
        return {
            'scraping': asdict(self.scraping),
            'sources': {name: asdict(config) for name, config in self.sources.items()},
            'quality': asdict(self.quality)
        }
    
    def __str__(self) -> str:
        """설정 정보 문자열 표현"""
        enabled_sources = list(self.get_enabled_sources().keys())
        return f"""
Configuration Summary:
- Max images per species: {self.scraping.max_images_per_species}
- Concurrent downloads: {self.scraping.concurrent_downloads}
- Enabled sources: {', '.join(enabled_sources)}
- Quality filters: {self.quality.min_file_size}B - {self.quality.max_file_size}B
"""