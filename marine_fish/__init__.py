"""
Marine Fish Scraper Package
해양어류 이미지 스크래핑 시스템
"""

__version__ = "1.0.0"
__author__ = "Marine Fish Scraper Team"
__description__ = "Advanced marine fish image scraping system"

# 주요 클래스들을 패키지 레벨에서 임포트 가능하게 함
from .marine_scraper import MarineScraper
from .config_manager import ConfigManager
from .taxonomy_manager import TaxonomyManager, SpeciesInfo
from .image_downloader import ImageDownloader
from .image_metadata import ImageMetadata
from .session_manager import SessionManager
from .logger import get_logger, setup_logging

__all__ = [
    'MarineScraper',
    'ConfigManager', 
    'TaxonomyManager',
    'SpeciesInfo',
    'ImageDownloader',
    'ImageMetadata',
    'SessionManager',
    'get_logger',
    'setup_logging'
]