"""
Advanced image downloader with atomic file operations and validation
"""
import os
import time
import hashlib
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import requests
from PIL import Image
from logger import get_logger
from error_handler import get_error_handler, with_retry, ErrorType
from config_manager import ConfigManager
from image_metadata import ImageMetadata

class DownloadResult:
    """다운로드 결과 클래스"""
    def __init__(self, success: bool, file_path: Optional[Path] = None, 
                 metadata: Optional[ImageMetadata] = None, error: Optional[str] = None):
        self.success = success
        self.file_path = file_path
        self.metadata = metadata
        self.error = error
        self.download_time = time.time()
    
    def __bool__(self) -> bool:
        return self.success

class ImageDownloader:
    """고급 이미지 다운로더"""
    
    # 문제가 있는 서버들 (블랙리스트)
    PROBLEMATIC_SERVERS = {
        'googleusercontent.com': '구글 사용자 콘텐츠 서버 - 접근 제한',
        'fbcdn.net': '페이스북 CDN - 접근 제한',
        'instagram.com': '인스타그램 - 접근 제한',
        'twitter.com': '트위터 - 접근 제한'
    }
    
    def __init__(self, config: ConfigManager = None):
        self.config = config or ConfigManager()
        self.logger = get_logger("image_downloader")
        self.error_handler = get_error_handler()
        
        # HTTP 세션 설정
        self.session = self._create_session()
        
        # 다운로드 통계
        self.stats = {
            'total_attempts': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'duplicate_skips': 0,
            'invalid_images': 0,
            'blacklist_skips': 0,
            'total_bytes': 0
        }
        
        # 중복 방지를 위한 해시 캐시
        self.hash_cache: Dict[str, str] = {}
    
    def _create_session(self) -> requests.Session:
        """HTTP 세션 생성"""
        session = requests.Session()
        
        # User-Agent 설정
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 타임아웃 설정
        session.timeout = self.config.scraping.timeout_seconds
        return session
    
    def _is_blacklisted(self, url: str) -> tuple[bool, str]:
        """URL이 블랙리스트에 있는지 확인"""
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            if hostname in self.PROBLEMATIC_SERVERS:
                reason = self.PROBLEMATIC_SERVERS[hostname]
                self.logger.info(f"블랙리스트 서버 스킵: {hostname} - {reason}")
                return True, reason
            return False, ""
        except Exception as e:
            self.logger.warning(f"URL 파싱 오류: {url} - {e}")
            return False, ""
    
    @with_retry(error_types=[ErrorType.NETWORK], circuit_breaker_key="image_download")
    def download_image(self, url: str, save_dir: Path, filename_base: str,
                      genus: str, species: str, source: str,
                      common_names: List[str] = None) -> DownloadResult:
        """이미지 다운로드 (원자적 파일 작업)"""
        self.stats['total_attempts'] += 1
        
        # URL 유효성 검사
        if not self._is_valid_url(url):
            error_msg = f"유효하지 않은 URL: {url}"
            self.logger.debug(error_msg)
            self.stats['failed_downloads'] += 1
            return DownloadResult(False, error=error_msg)
        
        # 블랙리스트 확인
        is_blacklisted, reason = self._is_blacklisted(url)
        if is_blacklisted:
            self.stats['blacklist_skips'] += 1
            return DownloadResult(False, error=f"블랙리스트 서버: {reason}")
        
        try:
            # HEAD 요청으로 파일 정보 확인
            head_response = self.session.head(url, timeout=10)
            if head_response.status_code not in [200, 302, 301]:
                error_msg = f"HEAD 요청 실패: {head_response.status_code}"
                self.stats['failed_downloads'] += 1
                return DownloadResult(False, error=error_msg)
            
            # Content-Type 확인
            content_type = head_response.headers.get('content-type', '').lower()
            if not self._is_image_content_type(content_type):
                error_msg = f"이미지가 아닌 콘텐츠: {content_type}"
                self.stats['failed_downloads'] += 1
                return DownloadResult(False, error=error_msg)
            
            # 파일 크기 확인
            content_length = head_response.headers.get('content-length')
            if content_length:
                file_size = int(content_length)
                if file_size < self.config.quality.min_file_size or file_size > self.config.quality.max_file_size:
                    error_msg = f"파일 크기 부적절: {file_size} bytes"
                    self.stats['failed_downloads'] += 1
                    return DownloadResult(False, error=error_msg)
            
            # 실제 이미지 다운로드
            response = self.session.get(url, stream=True, timeout=30)
            if response.status_code != 200:
                error_msg = f"다운로드 실패: {response.status_code}"
                self.stats['failed_downloads'] += 1
                return DownloadResult(False, error=error_msg)
            
            # 파일 확장자 결정
            file_extension = self._get_file_extension(content_type, url)
            final_filename = f"{filename_base}{file_extension}"
            final_path = save_dir / final_filename
            
            # 이미 존재하는 파일 확인
            if final_path.exists():
                self.logger.debug(f"파일이 이미 존재함: {final_path}")
                self.stats['duplicate_skips'] += 1
                return DownloadResult(False, error="파일이 이미 존재함")
            
            # 임시 파일에 다운로드 (원자적 작업)
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_path = Path(temp_file.name)
                downloaded_bytes = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded_bytes += len(chunk)
                        
                        # 최대 크기 제한
                        if downloaded_bytes > self.config.quality.max_file_size:
                            temp_path.unlink()  # 임시 파일 삭제
                            error_msg = f"파일 크기 초과: {downloaded_bytes} bytes"
                            self.stats['failed_downloads'] += 1
                            return DownloadResult(False, error=error_msg)
            
            # 이미지 유효성 검증
            validation_result = self._validate_image(temp_path)
            if not validation_result['valid']:
                temp_path.unlink()  # 임시 파일 삭제
                error_msg = f"이미지 검증 실패: {validation_result['error']}"
                self.stats['invalid_images'] += 1
                return DownloadResult(False, error=error_msg)
            
            # 중복 이미지 확인 (해시 기반)
            image_hash = self._calculate_file_hash(temp_path)
            if self._is_duplicate_hash(image_hash):
                temp_path.unlink()  # 임시 파일 삭제
                self.logger.debug(f"중복 이미지 스킵: {url}")
                self.stats['duplicate_skips'] += 1
                return DownloadResult(False, error="중복 이미지")
            
            # 원자적 파일 이동 (임시 파일 → 최종 위치)
            temp_path.replace(final_path)
            
            # 해시 캐시에 추가
            self.hash_cache[image_hash] = str(final_path)
            
            # 메타데이터 생성
            metadata = ImageMetadata.from_file(
                file_path=final_path,
                source=source,
                genus=genus,
                species=species,
                common_names=common_names or [],
                original_url=url
            )
            
            # 통계 업데이트
            self.stats['successful_downloads'] += 1
            self.stats['total_bytes'] += downloaded_bytes
            
            self.logger.debug(f"다운로드 성공: {final_path}")
            return DownloadResult(True, final_path, metadata)
            
        except Exception as e:
            error_msg = f"다운로드 중 오류: {str(e)}"
            self.logger.warning(f"이미지 다운로드 실패: {url} - {error_msg}")
            self.stats['failed_downloads'] += 1
            return DownloadResult(False, error=error_msg)
    
    def _is_valid_url(self, url: str) -> bool:
        """URL 유효성 검사"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _is_image_content_type(self, content_type: str) -> bool:
        """이미지 Content-Type 확인"""
        image_types = [
            'image/jpeg', 'image/jpg', 'image/png', 
            'image/gif', 'image/webp', 'image/bmp'
        ]
        return any(img_type in content_type for img_type in image_types)
    
    def _get_file_extension(self, content_type: str, url: str) -> str:
        """파일 확장자 결정"""
        # Content-Type 기반
        if 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'png' in content_type:
            return '.png'
        elif 'gif' in content_type:
            return '.gif'
        elif 'webp' in content_type:
            return '.webp'
        
        # URL 기반 (fallback)
        url_path = urlparse(url).path.lower()
        if url_path.endswith(('.jpg', '.jpeg')):
            return '.jpg'
        elif url_path.endswith('.png'):
            return '.png'
        elif url_path.endswith('.gif'):
            return '.gif'
        elif url_path.endswith('.webp'):
            return '.webp'
        
        # 기본값
        return '.jpg'
    
    def _validate_image(self, file_path: Path) -> Dict[str, Any]:
        """이미지 파일 유효성 검증"""
        try:
            with Image.open(file_path) as img:
                # 기본 정보 확인
                width, height = img.size
                
                # 최소 해상도 확인
                min_width, min_height = self.config.quality.min_resolution
                if width < min_width or height < min_height:
                    return {
                        'valid': False,
                        'error': f"Resolution too low: {width}x{height}"
                    }
                
                # 이미지 형식 확인
                if img.format.lower() not in ['jpeg', 'png', 'gif', 'webp']:
                    return {
                        'valid': False,
                        'error': f"Unsupported format: {img.format}"
                    }
                
                # 이미지 로드 테스트 (손상 확인)
                img.load()
                
                return {
                    'valid': True,
                    'width': width,
                    'height': height,
                    'format': img.format,
                    'mode': img.mode
                }
                
        except Exception as e:
            return {
                'valid': False,
                'error': f"Image validation failed: {str(e)}"
            }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """파일 해시 계산"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return ""
    
    def _is_duplicate_hash(self, image_hash: str) -> bool:
        """해시 기반 중복 확인"""
        return image_hash in self.hash_cache and image_hash != ""
    
    def batch_download(self, download_tasks: List[Dict[str, Any]], 
                      max_concurrent: int = None) -> List[DownloadResult]:
        """배치 다운로드"""
        if max_concurrent is None:
            max_concurrent = self.config.scraping.concurrent_downloads
        
        results = []
        
        # 순차 처리 (동시성은 나중에 추가)
        for i, task in enumerate(download_tasks):
            self.logger.debug(f"배치 다운로드 진행: {i+1}/{len(download_tasks)}")
            
            result = self.download_image(
                url=task['url'],
                save_dir=task['save_dir'],
                filename_base=task['filename_base'],
                genus=task['genus'],
                species=task['species'],
                source=task['source'],
                common_names=task.get('common_names', [])
            )
            results.append(result)
            
            # 요청 간 지연
            if i < len(download_tasks) - 1:
                time.sleep(self.config.scraping.delay_between_requests)
        
        return results
    
    def cleanup_temp_files(self) -> int:
        """임시 파일 정리"""
        temp_dir = Path(tempfile.gettempdir())
        cleaned_count = 0
        
        try:
            # 오래된 임시 파일들 찾기
            current_time = time.time()
            for temp_file in temp_dir.glob("tmp*"):
                try:
                    # 1시간 이상 된 임시 파일 삭제
                    if current_time - temp_file.stat().st_mtime > 3600:
                        temp_file.unlink()
                        cleaned_count += 1
                except:
                    continue
        except Exception as e:
            self.logger.warning(f"임시 파일 정리 중 오류: {e}")
        
        if cleaned_count > 0:
            self.logger.info(f"임시 파일 정리 완료: {cleaned_count}개 파일")
        
        return cleaned_count
    
    def get_download_statistics(self) -> Dict[str, Any]:
        """다운로드 통계 반환"""
        total_attempts = self.stats['total_attempts']
        success_rate = (self.stats['successful_downloads'] / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            'total_attempts': total_attempts,
            'successful_downloads': self.stats['successful_downloads'],
            'failed_downloads': self.stats['failed_downloads'],
            'duplicate_skips': self.stats['duplicate_skips'],
            'invalid_images': self.stats['invalid_images'],
            'blacklist_skips': self.stats['blacklist_skips'],
            'success_rate': success_rate,
            'total_mb_downloaded': self.stats['total_bytes'] / (1024 * 1024),
            'average_file_size_kb': (self.stats['total_bytes'] / self.stats['successful_downloads'] / 1024) if self.stats['successful_downloads'] > 0 else 0,
            'unique_images_cached': len(self.hash_cache)
        }
    
    def reset_statistics(self):
        """통계 초기화"""
        self.stats = {
            'total_attempts': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'duplicate_skips': 0,
            'invalid_images': 0,
            'blacklist_skips': 0,
            'total_bytes': 0
        }
        self.hash_cache.clear()
        self.logger.info("다운로드 통계 초기화 완료")
    
    def close(self):
        """리소스 정리"""
        if hasattr(self, 'session'):
            self.session.close()
        self.cleanup_temp_files()
        self.logger.info("ImageDownloader 리소스 정리 완료")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def __del__(self):
        try:
            self.close()
        except Exception:
            pass