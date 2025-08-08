"""
Taxonomic data management system for marine fish classification
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from logger import get_logger
from error_handler import get_error_handler, handle_gracefully

@dataclass
class SpeciesInfo:
    """종 정보 클래스"""
    genus: str
    species: str
    common_names: List[str]
    family: str
    order: str
    class_name: str
    
    @property
    def scientific_name(self) -> str:
        """학명 반환"""
        return f"{self.genus} {self.species}"
    
    @property
    def primary_common_name(self) -> str:
        """주요 일반명 반환"""
        return self.common_names[0] if self.common_names else self.scientific_name
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'genus': self.genus,
            'species': self.species,
            'common_names': self.common_names,
            'family': self.family,
            'order': self.order,
            'class': self.class_name
        }

class TaxonomyManager:
    """분류학적 데이터 관리자"""
    
    def __init__(self, taxonomy_file: Optional[str] = None):
        self.logger = get_logger("taxonomy_manager")
        self.error_handler = get_error_handler()
        
        # 기본 분류 체계 (대폭 확장된 관상용 해수어)
        self.fish_taxonomy = {
            "Chondrichthyes": {
                "Carcharhiniformes": {
                    "Hemiscylliidae": {
                        "Chiloscyllium": {
                            "punctatum": ["Brownbanded bamboo shark", "Brown-banded bamboo shark"],
                            "plagiosum": ["Whitespotted bamboo shark", "White-spotted bamboo shark"],
                            "griseum": ["Grey bamboo shark", "Gray bamboo shark"],
                            "hasselti": ["Hasselt's bamboo shark", "Indonesian bamboo shark"]
                        },
                        "Hemiscyllium": {
                            "ocellatum": ["Epaulette shark", "Walking shark"],
                            "freycineti": ["Indonesian walking shark", "Freycinet epaulette shark"],
                            "hallstromi": ["Papuan epaulette shark", "Hallstrom's epaulette shark"],
                            "henryi": ["Henry's epaulette shark"]
                        }
                    }
                }
            },
            "Osteichthyes": {
                "Acanthuriformes": {
                    "Acanthuridae": {
                        "Paracanthurus": {
                            "hepatus": ["Blue tang", "Regal tang", "Palette surgeonfish", "Hippo tang", "Dory fish"]
                        },
                        "Zebrasoma": {
                            "flavescens": ["Yellow tang", "Lemon sailfin"],
                            "xanthurum": ["Purple tang", "Yellowtail surgeonfish"],
                            "veliferum": ["Sailfin tang", "Pacific sailfin tang"],
                            "desjardinii": ["Red Sea sailfin tang", "Desjardin's sailfin tang"]
                        },
                        "Acanthurus": {
                            "leucosternon": ["Powder blue tang", "Powder blue surgeonfish"],
                            "japonicus": ["White-faced surgeonfish", "Gold rim tang"],
                            "sohal": ["Sohal surgeonfish", "Sohal tang"],
                            "lineatus": ["Lined surgeonfish", "Blue-lined surgeonfish"]
                        }
                    },
                    "Pomacanthidae": {
                        "Centropyge": {
                            "bicolor": ["Bicolor angelfish", "Two-colored angelfish"],
                            "loricula": ["Flame angelfish", "Flame angel"],
                            "argi": ["Cherub angelfish", "Pygmy angelfish"],
                            "eibli": ["Eibli angelfish", "Red stripe angelfish"],
                            "bispinosus": ["Coral beauty", "Two-spined angelfish"]
                        },
                        "Pomacanthus": {
                            "imperator": ["Emperor angelfish", "Imperial angelfish"],
                            "semicirculatus": ["Koran angelfish", "Semicircle angelfish"],
                            "navarchus": ["Blue-girdled angelfish", "Majestic angelfish"]
                        }
                    },
                    "Pomacentridae": {
                        "Amphiprion": {
                            "ocellaris": ["Ocellaris clownfish", "False percula clownfish", "Common clownfish"],
                            "percula": ["Orange clownfish", "Percula clownfish", "True percula"],
                            "clarkii": ["Clark's anemonefish", "Yellowtail clownfish"],
                            "frenatus": ["Tomato clownfish", "Red clownfish", "Bridled anemonefish"],
                            "melanopus": ["Red and black anemonefish", "Fire clownfish"],
                            "polymnus": ["Saddleback clownfish", "White-bonnet anemonefish"]
                        },
                        "Chromis": {
                            "viridis": ["Blue-green chromis", "Green chromis"],
                            "cyanea": ["Blue reef chromis", "Blue chromis"],
                            "atripectoralis": ["Black-axil chromis", "Blackfin chromis"]
                        },
                        "Dascyllus": {
                            "trimaculatus": ["Three-spot dascyllus", "Domino damsel"],
                            "aruanus": ["White-tailed dascyllus", "Humbug dascyllus"],
                            "melanurus": ["Four-stripe damselfish", "Blacktail dascyllus"]
                        }
                    },
                    "Chaetodontidae": {
                        "Chaetodon": {
                            "auriga": ["Threadfin butterflyfish", "Cross-stripe butterfly"],
                            "lunula": ["Raccoon butterflyfish", "Crescent-masked butterflyfish"],
                            "vagabundus": ["Vagabond butterflyfish", "Crisscross butterflyfish"],
                            "rafflesii": ["Latticed butterflyfish", "Raffle's butterflyfish"],
                            "melannotus": ["Blackback butterflyfish", "Black-backed butterflyfish"],
                            "collare": ["Pakistani butterflyfish", "Redtail butterflyfish"]
                        },
                        "Heniochus": {
                            "acuminatus": ["Pennant coralfish", "Longfin bannerfish"],
                            "diphreutes": ["Schooling bannerfish", "False moorish idol"]
                        },
                        "Forcipiger": {
                            "flavissimus": ["Yellow longnose butterflyfish", "Forceps fish"],
                            "longirostris": ["Longnose butterflyfish", "Big longnose butterflyfish"]
                        }
                    }
                },
                "Tetraodontiformes": {
                    "Tetraodontidae": {
                        "Arothron": {
                            "nigropunctatus": ["Blackspotted puffer", "Dog-faced puffer"],
                            "meleagris": ["Guineafowl puffer", "Golden puffer"]
                        },
                        "Canthigaster": {
                            "valentini": ["Valentini puffer", "Black-saddled toby"],
                            "solandri": ["Spotted sharpnose puffer", "Blue-spotted puffer"]
                        }
                    },
                    "Balistidae": {
                        "Rhinecanthus": {
                            "aculeatus": ["Lagoon triggerfish", "Blackbar triggerfish"],
                            "rectangulus": ["Wedgetail triggerfish", "Rectangle triggerfish"]
                        },
                        "Balistoides": {
                            "conspicillum": ["Clown triggerfish", "Big-spotted triggerfish"]
                        }
                    }
                }
            }
        }
        
        # 외부 파일에서 분류 체계 로드 (있는 경우)
        if taxonomy_file:
            self.load_taxonomy_from_file(taxonomy_file)
        
        # 인덱스 생성
        self._build_indexes()
    
    def _build_indexes(self):
        """검색 성능을 위한 인덱스 생성"""
        self.species_index: Dict[str, SpeciesInfo] = {}
        self.genus_index: Dict[str, List[SpeciesInfo]] = {}
        self.family_index: Dict[str, List[SpeciesInfo]] = {}
        self.common_name_index: Dict[str, List[SpeciesInfo]] = {}
        
        for class_name, orders in self.fish_taxonomy.items():
            for order_name, families in orders.items():
                for family_name, genera in families.items():
                    for genus_name, species_dict in genera.items():
                        for species_name, common_names in species_dict.items():
                            species_info = SpeciesInfo(
                                genus=genus_name,
                                species=species_name,
                                common_names=common_names,
                                family=family_name,
                                order=order_name,
                                class_name=class_name
                            )
                            
                            # 학명 인덱스
                            scientific_name = species_info.scientific_name
                            self.species_index[scientific_name] = species_info
                            
                            # 속 인덱스
                            if genus_name not in self.genus_index:
                                self.genus_index[genus_name] = []
                            self.genus_index[genus_name].append(species_info)
                            
                            # 과 인덱스
                            if family_name not in self.family_index:
                                self.family_index[family_name] = []
                            self.family_index[family_name].append(species_info)
                            
                            # 일반명 인덱스
                            for common_name in common_names:
                                common_lower = common_name.lower()
                                if common_lower not in self.common_name_index:
                                    self.common_name_index[common_lower] = []
                                self.common_name_index[common_lower].append(species_info)
        
        self.logger.info(f"분류 체계 인덱스 생성 완료: {len(self.species_index)}종")
    
    def get_species_info(self, genus: str, species: str) -> Optional[SpeciesInfo]:
        """종 정보 조회"""
        scientific_name = f"{genus} {species}"
        return self.species_index.get(scientific_name)
    
    def get_common_names(self, genus: str, species: str) -> List[str]:
        """일반명 목록 반환"""
        species_info = self.get_species_info(genus, species)
        return species_info.common_names if species_info else []
    
    def search_by_common_name(self, common_name: str) -> List[SpeciesInfo]:
        """일반명으로 종 검색"""
        common_lower = common_name.lower()
        return self.common_name_index.get(common_lower, [])
    
    def get_all_families(self) -> List[Tuple[str, str, str]]:
        """모든 과 목록 반환 (class, order, family)"""
        families = []
        for class_name, orders in self.fish_taxonomy.items():
            for order_name, family_dict in orders.items():
                for family_name in family_dict.keys():
                    families.append((class_name, order_name, family_name))
        return families
    
    def get_species_by_family(self, class_name: str, order_name: str, family_name: str) -> List[Tuple[str, str]]:
        """특정 과의 모든 종 반환 (genus, species)"""
        species_list = []
        try:
            family_data = self.fish_taxonomy[class_name][order_name][family_name]
            for genus_name, species_dict in family_data.items():
                for species_name in species_dict.keys():
                    species_list.append((genus_name, species_name))
        except KeyError:
            pass
        return species_list
    
    def get_all_species(self) -> List[SpeciesInfo]:
        """모든 종 정보 반환"""
        return list(self.species_index.values())
    
    def create_directory_structure(self, base_dir: Path) -> None:
        """분류학적 계층에 따른 디렉토리 구조 생성"""
        base_dir.mkdir(exist_ok=True)
        
        for class_name, orders in self.fish_taxonomy.items():
            class_dir = base_dir / class_name
            class_dir.mkdir(exist_ok=True)
            
            for order_name, families in orders.items():
                order_dir = class_dir / order_name
                order_dir.mkdir(exist_ok=True)
                
                for family_name, genera in families.items():
                    family_dir = order_dir / family_name
                    family_dir.mkdir(exist_ok=True)
                    
                    for genus_name, species_dict in genera.items():
                        for species_name in species_dict.keys():
                            species_dir = family_dir / f"{genus_name}_{species_name}"
                            species_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"디렉토리 구조 생성 완료: {base_dir}")
    
    def get_taxonomy_statistics(self) -> Dict[str, Any]:
        """분류 체계 통계 반환"""
        total_species = 0
        total_genera = set()
        total_families = 0
        class_stats = {}
        
        for class_name, orders in self.fish_taxonomy.items():
            class_species = 0
            class_families = 0
            
            for order_name, families in orders.items():
                class_families += len(families)
                for family_name, genera in families.items():
                    for genus_name, species_dict in genera.items():
                        total_genera.add(genus_name)
                        species_count = len(species_dict)
                        class_species += species_count
                        total_species += species_count
            
            total_families += class_families
            class_stats[class_name] = {
                'species': class_species,
                'families': class_families
            }
        
        return {
            'total_species': total_species,
            'total_genera': len(total_genera),
            'total_families': total_families,
            'total_classes': len(self.fish_taxonomy),
            'class_distribution': class_stats
        }
    
    def export_taxonomy(self, file_path: str) -> bool:
        """분류 체계를 파일로 내보내기"""
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'statistics': self.get_taxonomy_statistics(),
                'taxonomy': self.fish_taxonomy
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"분류 체계 내보내기 완료: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"분류 체계 내보내기 실패: {e}")
            return False
    
    @handle_gracefully(default_return=False)
    def load_taxonomy_from_file(self, file_path: str) -> bool:
        """외부 파일에서 분류 체계 로드"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 분류 체계 데이터 추출
            if 'taxonomy' in data:
                external_taxonomy = data['taxonomy']
            else:
                external_taxonomy = data
            
            # 기존 분류 체계와 병합
            self._merge_taxonomy(external_taxonomy)
            self._build_indexes()
            
            self.logger.info(f"외부 분류 체계 로드 완료: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"분류 체계 파일 로드 실패: {e}")
            return False
    
    def _merge_taxonomy(self, external_taxonomy: Dict):
        """외부 분류 체계를 기존 체계와 병합"""
        for class_name, orders in external_taxonomy.items():
            if class_name not in self.fish_taxonomy:
                self.fish_taxonomy[class_name] = {}
            
            for order_name, families in orders.items():
                if order_name not in self.fish_taxonomy[class_name]:
                    self.fish_taxonomy[class_name][order_name] = {}
                
                for family_name, genera in families.items():
                    if family_name not in self.fish_taxonomy[class_name][order_name]:
                        self.fish_taxonomy[class_name][order_name][family_name] = {}
                    
                    for genus_name, species_dict in genera.items():
                        if genus_name not in self.fish_taxonomy[class_name][order_name][family_name]:
                            self.fish_taxonomy[class_name][order_name][family_name][genus_name] = {}
                        
                        # 종 정보 병합
                        for species_name, common_names in species_dict.items():
                            existing_names = self.fish_taxonomy[class_name][order_name][family_name][genus_name].get(species_name, [])
                            # 중복 제거하면서 병합
                            merged_names = list(set(existing_names + common_names))
                            self.fish_taxonomy[class_name][order_name][family_name][genus_name][species_name] = merged_names