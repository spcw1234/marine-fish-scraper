"""
Image metadata model with serialization support
"""

import json
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from PIL import Image


@dataclass
class ImageMetadata:
    """이미지 메타데이터 클래스"""
    
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
    file_path: Optional[str] = None
    original_url: Optional[str] = None
    
    def __post_init__(self):
        """초기화 후 처리"""
        if isinstance(self.download_date, str):
            self.download_date = datetime.fromisoformat(self.download_date)
    
    @classmethod
    def from_file(cls, file_path: Path, source: str, genus: str, species: str, 
                  common_names: List[str] = None, original_url: str = None) -> 'ImageMetadata':
        """파일로부터 메타데이터 생성"""
        
        if not file_path.exists():
            raise FileNotFoundError(f"파일이 존재하지 않습니다: {file_path}")
        
        # 기본값 설정
        if common_names is None:
            common_names = []
        
        # 파일 정보 수집
        file_size = file_path.stat().st_size
        hash_md5 = cls._calculate_md5(file_path)
        
        # 이미지 해상도 및 품질 점수 계산
        try:
            with Image.open(file_path) as img:
                resolution = img.size
                quality_score = cls._calculate_quality_score(img, file_size)
        except Exception:
            # 이미지 파일이 아니거나 손상된 경우
            resolution = (0, 0)
            quality_score = 0.0
        
        return cls(
            filename=file_path.name,
            source=source,
            genus=genus,
            species=species,
            common_names=common_names,
            download_date=datetime.now(),
            file_size=file_size,
            resolution=resolution,
            hash_md5=hash_md5,
            quality_score=quality_score,
            file_path=str(file_path),
            original_url=original_url
        )
    
    @staticmethod
    def _calculate_md5(file_path: Path) -> str:
        """파일의 MD5 해시 계산"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    @staticmethod
    def _calculate_quality_score(img: Image.Image, file_size: int) -> float:
        """이미지 품질 점수 계산 (0.0 ~ 1.0)"""
        try:
            width, height = img.size
            
            # 해상도 점수 (0.0 ~ 0.4)
            resolution_score = min(0.4, (width * height) / (1920 * 1080) * 0.4)
            
            # 파일 크기 점수 (0.0 ~ 0.3)
            # 적절한 크기: 50KB ~ 2MB
            if 50000 <= file_size <= 2000000:
                size_score = 0.3
            elif file_size < 50000:
                size_score = file_size / 50000 * 0.3
            else:
                size_score = max(0.1, 0.3 - (file_size - 2000000) / 8000000 * 0.2)
            
            # 종횡비 점수 (0.0 ~ 0.2)
            aspect_ratio = width / height if height > 0 else 0
            if 0.5 <= aspect_ratio <= 2.0:
                aspect_score = 0.2
            else:
                aspect_score = max(0.0, 0.2 - abs(aspect_ratio - 1.0) * 0.1)
            
            # 색상 모드 점수 (0.0 ~ 0.1)
            mode_score = 0.1 if img.mode in ['RGB', 'RGBA'] else 0.05
            
            return min(1.0, resolution_score + size_score + aspect_score + mode_score)
            
        except Exception:
            return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        # datetime을 ISO 형식 문자열로 변환
        data['download_date'] = self.download_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageMetadata':
        """딕셔너리로부터 생성"""
        # datetime 문자열을 datetime 객체로 변환
        if isinstance(data.get('download_date'), str):
            data['download_date'] = datetime.fromisoformat(data['download_date'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ImageMetadata':
        """JSON 문자열로부터 생성"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save_to_file(self, metadata_path: Path) -> None:
        """메타데이터를 파일로 저장"""
        try:
            # 임시 파일에 먼저 저장 (원자적 쓰기)
            temp_path = metadata_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(self.to_json())
            
            # 성공하면 원본 파일로 이동
            temp_path.replace(metadata_path)
            
        except Exception as e:
            raise IOError(f"메타데이터 저장 실패: {e}")
    
    @classmethod
    def load_from_file(cls, metadata_path: Path) -> 'ImageMetadata':
        """파일로부터 메타데이터 로드"""
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                json_str = f.read()
            return cls.from_json(json_str)
        except Exception as e:
            raise IOError(f"메타데이터 로드 실패: {e}")
    
    def is_duplicate(self, other: 'ImageMetadata') -> bool:
        """다른 메타데이터와 중복 여부 확인"""
        return (self.hash_md5 == other.hash_md5 and 
                self.hash_md5 != "" and 
                other.hash_md5 != "")
    
    def is_valid(self) -> bool:
        """메타데이터 유효성 검증"""
        return (
            bool(self.filename) and
            bool(self.source) and
            bool(self.genus) and
            bool(self.species) and
            self.file_size > 0 and
            self.resolution[0] > 0 and
            self.resolution[1] > 0 and
            bool(self.hash_md5)
        )
    
    def get_scientific_name(self) -> str:
        """학명 반환"""
        return f"{self.genus} {self.species}"
    
    def get_display_name(self) -> str:
        """표시용 이름 반환 (일반명이 있으면 일반명, 없으면 학명)"""
        if self.common_names:
            return self.common_names[0]
        return self.get_scientific_name()
    
    def update_quality_score(self) -> None:
        """품질 점수 재계산"""
        if self.file_path and Path(self.file_path).exists():
            try:
                with Image.open(self.file_path) as img:
                    self.quality_score = self._calculate_quality_score(img, self.file_size)
            except Exception:
                self.quality_score = 0.0
    
    def __str__(self) -> str:
        """문자열 표현"""
        return f"{self.get_scientific_name()} ({self.source}) - {self.filename}"
    
    def __repr__(self) -> str:
        """개발자용 문자열 표현"""
        return (f"ImageMetadata(filename='{self.filename}', "
                f"source='{self.source}', "
                f"species='{self.get_scientific_name()}', "
                f"quality={self.quality_score:.2f})")


class MetadataCollection:
    """메타데이터 컬렉션 관리 클래스"""
    
    def __init__(self):
        self.metadata_list: List[ImageMetadata] = []
        self._hash_index: Dict[str, ImageMetadata] = {}
    
    def add(self, metadata: ImageMetadata) -> bool:
        """메타데이터 추가 (중복 체크)"""
        if not metadata.is_valid():
            return False
        
        # 중복 체크
        if metadata.hash_md5 in self._hash_index:
            return False
        
        self.metadata_list.append(metadata)
        self._hash_index[metadata.hash_md5] = metadata
        return True
    
    def remove(self, metadata: ImageMetadata) -> bool:
        """메타데이터 제거"""
        if metadata in self.metadata_list:
            self.metadata_list.remove(metadata)
            if metadata.hash_md5 in self._hash_index:
                del self._hash_index[metadata.hash_md5]
            return True
        return False
    
    def find_duplicates(self) -> List[List[ImageMetadata]]:
        """중복 이미지 그룹 찾기"""
        hash_groups = {}
        for metadata in self.metadata_list:
            if metadata.hash_md5:
                if metadata.hash_md5 not in hash_groups:
                    hash_groups[metadata.hash_md5] = []
                hash_groups[metadata.hash_md5].append(metadata)
        
        return [group for group in hash_groups.values() if len(group) > 1]
    
    def get_by_species(self, genus: str, species: str) -> List[ImageMetadata]:
        """종별 메타데이터 조회"""
        return [m for m in self.metadata_list 
                if m.genus == genus and m.species == species]
    
    def get_by_source(self, source: str) -> List[ImageMetadata]:
        """소스별 메타데이터 조회"""
        return [m for m in self.metadata_list if m.source == source]
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        if not self.metadata_list:
            return {}
        
        total_count = len(self.metadata_list)
        total_size = sum(m.file_size for m in self.metadata_list)
        avg_quality = sum(m.quality_score for m in self.metadata_list) / total_count
        
        # 소스별 통계
        source_stats = {}
        for metadata in self.metadata_list:
            if metadata.source not in source_stats:
                source_stats[metadata.source] = 0
            source_stats[metadata.source] += 1
        
        # 종별 통계
        species_stats = {}
        for metadata in self.metadata_list:
            species_key = metadata.get_scientific_name()
            if species_key not in species_stats:
                species_stats[species_key] = 0
            species_stats[species_key] += 1
        
        return {
            'total_images': total_count,
            'total_size_mb': total_size / (1024 * 1024),
            'average_quality': avg_quality,
            'source_distribution': source_stats,
            'species_distribution': species_stats,
            'unique_species': len(species_stats),
            'duplicate_groups': len(self.find_duplicates())
        }
    
    def save_to_file(self, file_path: Path) -> None:
        """컬렉션을 파일로 저장"""
        data = {
            'metadata_list': [m.to_dict() for m in self.metadata_list],
            'saved_at': datetime.now().isoformat()
        }
        
        try:
            # 임시 파일에 먼저 저장
            temp_path = file_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 성공하면 원본 파일로 이동
            temp_path.replace(file_path)
            
        except Exception as e:
            raise IOError(f"컬렉션 저장 실패: {e}")
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> 'MetadataCollection':
        """파일로부터 컬렉션 로드"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            collection = cls()
            for metadata_dict in data.get('metadata_list', []):
                metadata = ImageMetadata.from_dict(metadata_dict)
                collection.add(metadata)
            
            return collection
            
        except Exception as e:
            raise IOError(f"컬렉션 로드 실패: {e}")
    
    def __len__(self) -> int:
        return len(self.metadata_list)
    
    def __iter__(self):
        return iter(self.metadata_list)
    
    def __getitem__(self, index):
        return self.metadata_list[index]