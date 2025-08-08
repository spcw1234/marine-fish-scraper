"""
Main scraping engine that coordinates all scrapers and components
"""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

# 현재 폴더의 모듈들 import (상대 경로 제거)
try:
    from scraping_session import ScrapingSession, SessionManager, SessionStatus
    from image_metadata import ImageMetadata, MetadataCollection
    from config_manager import ConfigManager
    from taxonomy_manager import TaxonomyManager
    from image_downloader import ImageDownloader, DownloadResult
    from image_validator import ImageValidator
    from logger import get_logger
    from error_handler import get_error_handler, with_retry, ErrorType
except ImportError as e:
    print(f"Import error: {e}")
    print("일부 모듈이 아직 생성되지 않았습니다. 필요한 모듈들을 먼저 생성해주세요.")

# 스크래퍼 임포트 (현재는 주석 처리)
# from fishbase_scraper import FishBaseScraper
# from google_images_scraper import GoogleImagesScraper
# from reef2reef_scraper import Reef2ReefScraper
# from flickr_scraper import FlickrScraper


@dataclass
class ScrapingResult:
    """스크래핑 결과"""
    genus: str
    species: str
    total_found: int
    total_downloaded: int
    source_results: Dict[str, int]
    errors: List[str]
    duration: float


class ScraperCore:
    """메인 스크래핑 엔진"""
    
    def __init__(self, config_path: Optional[str] = None, base_dir: str = "."):
        # 설정 및 기본 컴포넌트 초기화
        self.config = ConfigManager(config_path)
        self.logger = get_logger("scraper_core")
        self.error_handler = get_error_handler()
        
        # 디렉토리 설정
        self.base_dir = Path(base_dir)
        self.dataset_dir = self.base_dir / "dataset"
        self.sessions_dir = self.base_dir / "sessions"
        self.metadata_dir = self.base_dir / "metadata"
        
        # 디렉토리 생성
        for directory in [self.base_dir, self.dataset_dir, self.sessions_dir, self.metadata_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 핵심 컴포넌트 초기화
        self.taxonomy_manager = TaxonomyManager()
        self.session_manager = SessionManager(str(self.sessions_dir))
        self.image_validator = ImageValidator()
        self.image_downloader = ImageDownloader(self.config)
        
        # 스크래퍼들 초기화
        self.scrapers = self._initialize_scrapers()
        
        # 메타데이터 컬렉션
        self.metadata_collection = MetadataCollection()
        
        # 통계
        self.scraping_stats = {
            'total_species_processed': 0,
            'total_images_found': 0,
            'total_images_downloaded': 0,
            'total_errors': 0,
            'source_stats': {},
            'start_time': None,
            'end_time': None
        }
    
    def _initialize_scrapers(self) -> Dict[str, Any]:
        """스크래퍼들 초기화"""
        scrapers = {}
        
        enabled_sources = self.config.get_enabled_sources()
        
        if 'fishbase' in enabled_sources:
            scrapers['fishbase'] = FishBaseScraper(self.config)
            
        if 'google_images' in enabled_sources:
            scrapers['google_images'] = GoogleImagesScraper(self.config)
            
        if 'reef2reef' in enabled_sources:
            scrapers['reef2reef'] = Reef2ReefScraper(self.config)
            
        if 'flickr' in enabled_sources:
            scrapers['flickr'] = FlickrScraper(self.config)
        
        self.logger.info(f"활성화된 스크래퍼: {list(scrapers.keys())}")
        return scrapers
    
    def scrape_all_species(self, resume_session: Optional[str] = None) -> ScrapingSession:
        """모든 종 스크래핑"""
        self.logger.info("🚀 전체 종 스크래핑 시작")
        
        # 세션 생성 또는 복원
        if resume_session:
            session = self.session_manager.load_session(resume_session)
            if not session:
                self.logger.error(f"세션을 찾을 수 없습니다: {resume_session}")
                return None
            session.resume()
            self.logger.info(f"세션 복원: {session.session_id}")
        else:
            # 모든 종 목록 생성
            all_species = []
            for species_info in self.taxonomy_manager.get_all_species():
                all_species.append(species_info.scientific_name)
            
            session = self.session_manager.create_session(all_species, self.config.to_dict())
            session.start()
        
        self.session_manager.set_active_session(session.session_id)
        
        try:
            # 스크래핑 실행
            self._execute_scraping_session(session)
            
            # 세션 완료
            session.complete()
            self.logger.info(f"✅ 전체 스크래핑 완료: {session.session_id}")
            
        except KeyboardInterrupt:
            session.pause()
            self.logger.info(f"⏸️ 사용자에 의해 일시정지: {session.session_id}")
            
        except Exception as e:
            session.fail(str(e))
            self.logger.error(f"❌ 스크래핑 실패: {e}")
            
        finally:
            self.session_manager.save_session(session)
        
        return session
    
    def scrape_specific_family(self, class_name: str, order_name: str, family_name: str) -> ScrapingSession:
        """특정 과 스크래핑"""
        self.logger.info(f"🎯 {family_name} 과 스크래핑 시작")
        
        # 해당 과의 종 목록 생성
        species_list = []
        family_species = self.taxonomy_manager.get_species_by_family(class_name, order_name, family_name)
        
        for genus, species in family_species:
            species_list.append(f"{genus} {species}")
        
        if not species_list:
            self.logger.error(f"❌ {family_name} 과에서 종을 찾을 수 없습니다")
            return None
        
        # 세션 생성
        session = self.session_manager.create_session(species_list, self.config.to_dict())
        session.start()
        
        try:
            self._execute_scraping_session(session)
            session.complete()
            self.logger.info(f"✅ {family_name} 과 스크래핑 완료")
            
        except KeyboardInterrupt:
            session.pause()
            self.logger.info("⏸️ 사용자에 의해 일시정지")
            
        except Exception as e:
            session.fail(str(e))
            self.logger.error(f"❌ 스크래핑 실패: {e}")
            
        finally:
            self.session_manager.save_session(session)
        
        return session
    
    def _execute_scraping_session(self, session: ScrapingSession):
        """스크래핑 세션 실행"""
        remaining_species = session.get_remaining_species()
        total_species = len(remaining_species)
        
        self.logger.info(f"📊 처리할 종 수: {total_species}")
        
        # 병렬 처리 설정
        max_workers = min(self.config.scraping.concurrent_downloads, 3)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 종별 스크래핑 작업 제출
            future_to_species = {}
            
            for i, species_name in enumerate(remaining_species):
                if session.status != SessionStatus.RUNNING:
                    break
                
                genus, species = species_name.split(' ', 1)
                
                future = executor.submit(self._scrape_single_species, genus, species, session)
                future_to_species[future] = species_name
                
                # 진행률 출력
                if (i + 1) % 10 == 0:
                    progress = (i + 1) / total_species * 100
                    self.logger.info(f"📈 진행률: {i + 1}/{total_species} ({progress:.1f}%)")
            
            # 결과 수집
            for future in as_completed(future_to_species):
                species_name = future_to_species[future]
                
                try:
                    result = future.result()
                    if result:
                        self.logger.info(f"✅ {species_name}: {result.total_downloaded}장 다운로드")
                    else:
                        self.logger.warning(f"⚠️ {species_name}: 스크래핑 실패")
                        
                except Exception as e:
                    self.logger.error(f"❌ {species_name} 처리 중 오류: {e}")
                    genus, species = species_name.split(' ', 1)
                    session.mark_species_failed(genus, species, "unknown", str(e))
                
                # 세션 저장 (주기적)
                self.session_manager.save_session(session)
    
    @with_retry(error_types=[ErrorType.NETWORK, ErrorType.FILE_SYSTEM])
    def _scrape_single_species(self, genus: str, species: str, session: ScrapingSession) -> Optional[ScrapingResult]:
        """단일 종 스크래핑"""
        start_time = time.time()
        
        try:
            # 종 정보 조회
            species_info = self.taxonomy_manager.get_species_info(genus, species)
            if not species_info:
                self.logger.warning(f"⚠️ 종 정보를 찾을 수 없습니다: {genus} {species}")
                return None
            
            # 저장 디렉토리 생성
            save_dir = (self.dataset_dir / species_info.class_name / 
                       species_info.order / species_info.family / 
                       f"{genus}_{species}")
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # 각 소스에서 이미지 URL 수집
            all_image_urls = []
            source_results = {}
            errors = []
            
            enabled_sources = self.config.get_enabled_sources()
            
            for source_name, scraper in self.scrapers.items():
                if source_name not in enabled_sources:
                    continue
                
                try:
                    source_config = enabled_sources[source_name]
                    max_images = source_config.max_images
                    
                    self.logger.debug(f"🔍 {source_name}에서 {genus} {species} 검색 중...")
                    
                    # 소스별 이미지 URL 수집
                    if source_name == 'fishbase':
                        image_urls = scraper.search_species_images(genus, species, max_images)
                    else:
                        common_names = species_info.common_names
                        image_urls = scraper.search_species_images(genus, species, common_names, max_images)
                    
                    source_results[source_name] = len(image_urls)
                    all_image_urls.extend(image_urls)
                    
                    self.logger.debug(f"📥 {source_name}: {len(image_urls)}개 URL 수집")
                    
                    # 소스 간 지연
                    time.sleep(self.config.scraping.delay_between_requests)
                    
                except Exception as e:
                    error_msg = f"{source_name} 검색 실패: {str(e)}"
                    errors.append(error_msg)
                    source_results[source_name] = 0
                    session.mark_species_failed(genus, species, source_name, error_msg)
                    self.logger.warning(f"⚠️ {error_msg}")
            
            # 중복 URL 제거
            unique_urls = []
            seen_urls = set()
            
            for img_data in all_image_urls:
                url = img_data['url']
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_urls.append(img_data)
            
            total_found = len(unique_urls)
            self.logger.info(f"🔍 {genus} {species}: 총 {total_found}개 고유 이미지 발견")
            
            # 이미지 다운로드
            downloaded_count = 0
            
            for i, img_data in enumerate(unique_urls):
                try:
                    filename_base = f"{img_data['source']}_{genus}_{species}_{i+1:03d}"
                    
                    result = self.image_downloader.download_image(
                        url=img_data['url'],
                        save_dir=save_dir,
                        filename_base=filename_base,
                        genus=genus,
                        species=species,
                        source=img_data['source'],
                        common_names=species_info.common_names
                    )
                    
                    if result.success:
                        downloaded_count += 1
                        
                        # 메타데이터 컬렉션에 추가
                        if result.metadata:
                            self.metadata_collection.add(result.metadata)
                        
                        # 세션 진행률 업데이트
                        session.update_species_progress(genus, species, 1, img_data['source'])
                    
                    # 다운로드 간 지연
                    time.sleep(self.config.scraping.delay_between_requests * 0.5)
                    
                except Exception as e:
                    error_msg = f"이미지 다운로드 실패: {img_data['url']} - {str(e)}"
                    errors.append(error_msg)
                    self.logger.debug(f"⚠️ {error_msg}")
            
            # 결과 생성
            duration = time.time() - start_time
            
            result = ScrapingResult(
                genus=genus,
                species=species,
                total_found=total_found,
                total_downloaded=downloaded_count,
                source_results=source_results,
                errors=errors,
                duration=duration
            )
            
            # 통계 업데이트
            self._update_stats(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ {genus} {species} 스크래핑 실패: {e}")
            session.mark_species_failed(genus, species, "unknown", str(e))
            return None
    
    def _update_stats(self, result: ScrapingResult):
        """통계 업데이트"""
        self.scraping_stats['total_species_processed'] += 1
        self.scraping_stats['total_images_found'] += result.total_found
        self.scraping_stats['total_images_downloaded'] += result.total_downloaded
        self.scraping_stats['total_errors'] += len(result.errors)
        
        # 소스별 통계
        for source, count in result.source_results.items():
            if source not in self.scraping_stats['source_stats']:
                self.scraping_stats['source_stats'][source] = {'found': 0, 'downloaded': 0}
            self.scraping_stats['source_stats'][source]['found'] += count
    
    def create_training_dataset(self, images_per_class: int = 100, 
                              output_dir: Optional[str] = None) -> bool:
        """훈련용 데이터셋 생성"""
        self.logger.info(f"🎯 훈련용 데이터셋 생성 시작 (클래스당 {images_per_class}장)")
        
        if output_dir:
            train_dir = Path(output_dir)
        else:
            train_dir = self.base_dir / "train"
        
        train_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 클래스별 폴더 생성
            for class_name in self.taxonomy_manager.fish_taxonomy.keys():
                class_dir = train_dir / class_name
                class_dir.mkdir(exist_ok=True)
                
                # 해당 클래스의 모든 이미지 수집
                class_dataset_dir = self.dataset_dir / class_name
                if not class_dataset_dir.exists():
                    self.logger.warning(f"⚠️ {class_name} 데이터셋 폴더가 없습니다")
                    continue
                
                all_images = []
                for img_path in class_dataset_dir.rglob("*"):
                    if (img_path.is_file() and 
                        img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']):
                        all_images.append(img_path)
                
                self.logger.info(f"📊 {class_name}: {len(all_images)}개 이미지 발견")
                
                if len(all_images) == 0:
                    continue
                
                # 랜덤 샘플링
                import random
                selected_count = min(images_per_class, len(all_images))
                selected_images = random.sample(all_images, selected_count)
                
                # 복사
                for i, img_path in enumerate(selected_images, 1):
                    try:
                        # 원본 경로에서 종 정보 추출
                        relative_path = img_path.relative_to(class_dataset_dir)
                        species_info = "_".join(relative_path.parts[:-1])
                        
                        # 새 파일명 생성
                        new_filename = f"{class_name}_{species_info}_{i:03d}{img_path.suffix}"
                        new_path = class_dir / new_filename
                        
                        import shutil
                        shutil.copy2(img_path, new_path)
                        
                    except Exception as e:
                        self.logger.warning(f"⚠️ 파일 복사 실패: {img_path} - {e}")
                
                self.logger.info(f"✅ {class_name}: {selected_count}개 이미지 복사 완료")
            
            self.logger.info(f"🎉 훈련용 데이터셋 생성 완료: {train_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 훈련용 데이터셋 생성 실패: {e}")
            return False
    
    def analyze_dataset(self) -> Dict[str, Any]:
        """데이터셋 분석"""
        self.logger.info("📊 데이터셋 분석 시작")
        
        analysis = {
            'total_images': 0,
            'class_distribution': {},
            'family_distribution': {},
            'species_distribution': {},
            'quality_analysis': {},
            'source_analysis': {},
            'file_size_analysis': {},
            'resolution_analysis': {}
        }
        
        try:
            if not self.dataset_dir.exists():
                self.logger.warning("⚠️ 데이터셋 폴더가 존재하지 않습니다")
                return analysis
            
            all_images = []
            
            # 모든 이미지 파일 수집
            for img_path in self.dataset_dir.rglob("*"):
                if (img_path.is_file() and 
                    img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']):
                    all_images.append(img_path)
            
            analysis['total_images'] = len(all_images)
            self.logger.info(f"📊 총 {len(all_images)}개 이미지 분석 중...")
            
            # 클래스별 분포
            for class_name in self.taxonomy_manager.fish_taxonomy.keys():
                class_dir = self.dataset_dir / class_name
                if class_dir.exists():
                    class_images = list(class_dir.rglob("*.jpg")) + list(class_dir.rglob("*.png"))
                    analysis['class_distribution'][class_name] = len(class_images)
            
            self.logger.info("✅ 데이터셋 분석 완료")
            
        except Exception as e:
            self.logger.error(f"❌ 데이터셋 분석 실패: {e}")
        
        return analysis
    
    def setup_auto_labeling_workspace(self) -> bool:
        """오토 라벨링 작업공간 설정"""
        self.logger.info("🏷️ 오토 라벨링 작업공간 설정 시작")
        
        try:
            # 라벨링 작업공간 폴더 생성
            labeling_dir = self.base_dir / "auto_labeling"
            labeling_dir.mkdir(exist_ok=True)
            
            # 하위 폴더들 생성
            folders = [
                "unlabeled", "labeled", "verified", "rejected", 
                "models", "annotations", "exports"
            ]
            
            for folder in folders:
                (labeling_dir / folder).mkdir(exist_ok=True)
            
            # 클래스별 하위 폴더 생성
            for main_folder in ["labeled", "verified"]:
                for class_name in self.taxonomy_manager.fish_taxonomy.keys():
                    (labeling_dir / main_folder / class_name).mkdir(exist_ok=True)
            
            self.logger.info(f"✅ 오토 라벨링 작업공간 설정 완료: {labeling_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 오토 라벨링 작업공간 설정 실패: {e}")
            return False
    
    def get_scraping_statistics(self) -> Dict[str, Any]:
        """스크래핑 통계 반환"""
        stats = self.scraping_stats.copy()
        
        # 다운로드 통계 추가
        download_stats = self.image_downloader.get_download_statistics()
        stats['download_stats'] = download_stats
        
        # 에러 통계 추가
        error_stats = self.error_handler.get_error_statistics()
        stats['error_stats'] = error_stats
        
        # 메타데이터 통계 추가
        if len(self.metadata_collection) > 0:
            metadata_stats = self.metadata_collection.get_statistics()
            stats['metadata_stats'] = metadata_stats
        
        return stats
    
    def export_metadata(self, file_path: str) -> bool:
        """메타데이터 내보내기"""
        try:
            self.metadata_collection.save_to_file(Path(file_path))
            self.logger.info(f"✅ 메타데이터 내보내기 완료: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"❌ 메타데이터 내보내기 실패: {e}")
            return False
    
    def cleanup_resources(self):
        """리소스 정리"""
        try:
            # 스크래퍼들 정리
            for scraper in self.scrapers.values():
                if hasattr(scraper, 'close'):
                    scraper.close()
            
            # 이미지 다운로더 정리
            self.image_downloader.close()
            
            # 임시 파일 정리
            self.image_downloader.cleanup_temp_files()
            
            self.logger.info("✅ 리소스 정리 완료")
            
        except Exception as e:
            self.logger.error(f"❌ 리소스 정리 실패: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_resources()
    
    def __del__(self):
        try:
            self.cleanup_resources()
        except:
            pass