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
        
        # 완전한 분류학적 계층구조 (현재 유통되는 모든 관상용 해수어)
        self.fish_taxonomy = {
            "Chondrichthyes": {  # 연골어류
                "Carcharhiniformes": {  # 흉상어목
                    "Hemiscylliidae": {  # 대나무상어과
                        "Chiloscyllium": {
                            "punctatum": ["Brownbanded bamboo shark", "갈색줄무늬 대나무상어"],
                            "plagiosum": ["Whitespotted bamboo shark", "흰점 대나무상어"],
                            "griseum": ["Grey bamboo shark", "회색 대나무상어"],
                            "hasselti": ["Hasselt's bamboo shark", "하셀트 대나무상어"]
                        },
                        "Hemiscyllium": {
                            "ocellatum": ["Epaulette shark", "견장상어", "Walking shark"],
                            "freycineti": ["Indonesian walking shark", "인도네시아 견장상어"],
                            "hallstromi": ["Papuan epaulette shark", "파푸아 견장상어"],
                            "henryi": ["Henry's epaulette shark", "헨리 견장상어"]
                        }
                    }
                },
                "Rajiformes": {  # 가오리목
                    "Dasyatidae": {  # 참가오리과
                        "Taeniura": {
                            "lymma": ["Blue-spotted ribbontail ray", "파란점 리본꼬리가오리"]
                        }
                    },
                    "Potamotrygonidae": {  # 민물가오리과
                        "Potamotrygon": {
                            "motoro": ["Ocellate river stingray", "눈무늬 민물가오리"]
                        }
                    }
                }
            },
            "Osteichthyes": {  # 경골어류
                "Actinopterygii": {  # 조기어류
                    "Acanthuromorpha": {  # 가시고등어상목
                        "Acanthuriformes": {  # 가시고등어목
                            "Acanthuridae": {  # 쥐치과
                                "Paracanthurus": {
                                    "hepatus": ["Blue tang", "Regal tang", "Palette surgeonfish", "Hippo tang", "Dory fish", "파란탱", "리갈탱"]
                                },
                                "Zebrasoma": {
                                    "flavescens": ["Yellow tang", "Lemon sailfin", "옐로우탱", "노란탱"],
                                    "xanthurum": ["Purple tang", "Yellowtail surgeonfish", "퍼플탱", "보라탱"],
                                    "veliferum": ["Sailfin tang", "Pacific sailfin tang", "세일핀탱"],
                                    "desjardinii": ["Red Sea sailfin tang", "Desjardin's sailfin tang", "데자르딘 세일핀탱"],
                                    "scopas": ["Brown tang", "Twotone tang", "브라운탱"],
                                    "gemmatum": ["Spotted tang", "스팟티드탱"]
                                },
                                "Acanthurus": {
                                    "leucosternon": ["Powder blue tang", "Powder blue surgeonfish", "파우더블루탱"],
                                    "japonicus": ["White-faced surgeonfish", "Gold rim tang", "골드림탱"],
                                    "sohal": ["Sohal surgeonfish", "Sohal tang", "소할탱"],
                                    "lineatus": ["Lined surgeonfish", "Blue-lined surgeonfish", "라인드탱"],
                                    "achilles": ["Achilles tang", "Red-spotted surgeonfish", "아킬레스탱"],
                                    "nigrofuscus": ["Brown surgeonfish", "Lavender tang", "라벤더탱"]
                                },
                                "Naso": {
                                    "lituratus": ["Orangespine unicornfish", "Naso tang", "나소탱"],
                                    "elegans": ["Elegant unicornfish", "엘레간트 유니콘피쉬"],
                                    "lopezi": ["Lopez's unicornfish", "로페즈 유니콘피쉬"]
                                },
                                "Ctenochaetus": {
                                    "strigosus": ["Kole tang", "Yellow-eyed surgeonfish", "콜탱"],
                                    "hawaiiensis": ["Chevron tang", "쉐브론탱"]
                                }
                            },
                            "Pomacanthidae": {  # 엔젤피쉬과
                                "Centropyge": {  # 드워프엔젤
                                    "bicolor": ["Bicolor angelfish", "Two-colored angelfish", "바이컬러엔젤"],
                                    "loricula": ["Flame angelfish", "Flame angel", "플레임엔젤"],
                                    "argi": ["Cherub angelfish", "Pygmy angelfish", "체럽엔젤"],
                                    "eibli": ["Eibli angelfish", "Red stripe angelfish", "아이블리엔젤"],
                                    "bispinosus": ["Coral beauty", "Two-spined angelfish", "코랄뷰티"],
                                    "flavissima": ["Lemonpeel angelfish", "레몬필엔젤"],
                                    "heraldi": ["Herald's angelfish", "헤럴드엔젤"],
                                    "potteri": ["Potter's angelfish", "포터엔젤"],
                                    "resplendens": ["Resplendent angelfish", "레스플렌던트엔젤"],
                                    "tibicen": ["Keyhole angelfish", "키홀엔젤"]
                                },
                                "Pomacanthus": {  # 라지엔젤
                                    "imperator": ["Emperor angelfish", "Imperial angelfish", "엠페러엔젤"],
                                    "semicirculatus": ["Koran angelfish", "Semicircle angelfish", "코란엔젤"],
                                    "navarchus": ["Blue-girdled angelfish", "Majestic angelfish", "마제스틱엔젤"],
                                    "xanthometopon": ["Blueface angelfish", "블루페이스엔젤"],
                                    "annularis": ["Blue-ring angelfish", "블루링엔젤"]
                                },
                                "Holacanthus": {
                                    "ciliaris": ["Queen angelfish", "퀸엔젤"],
                                    "bermudensis": ["Blue angelfish", "블루엔젤"]
                                },
                                "Genicanthus": {
                                    "lamarck": ["Lamarck's angelfish", "라마르크엔젤"],
                                    "bellus": ["Ornate angelfish", "오네이트엔젤"],
                                    "melanospilos": ["Blackspot angelfish", "블랙스팟엔젤"]
                                }
                            },
                            "Pomacentridae": {  # 자리돔과
                                "Amphiprion": {  # 클라운피쉬
                                    "ocellaris": ["Ocellaris clownfish", "False percula clownfish", "Common clownfish", "오셀라리스", "니모"],
                                    "percula": ["Orange clownfish", "Percula clownfish", "True percula", "퍼큘라", "트루퍼큘라"],
                                    "clarkii": ["Clark's anemonefish", "Yellowtail clownfish", "클라키"],
                                    "frenatus": ["Tomato clownfish", "Red clownfish", "토마토클라운"],
                                    "melanopus": ["Red and black anemonefish", "Fire clownfish", "파이어클라운"],
                                    "polymnus": ["Saddleback clownfish", "White-bonnet anemonefish", "새들백클라운"],
                                    "sebae": ["Sebae clownfish", "세바에클라운"],
                                    "ephippium": ["Red saddleback anemonefish", "레드새들백"],
                                    "chrysopterus": ["Orange-fin anemonefish", "오렌지핀클라운"],
                                    "bicinctus": ["Two-band anemonefish", "투밴드클라운"]
                                },
                                "Premnas": {
                                    "biaculeatus": ["Maroon clownfish", "Spine-cheek anemonefish", "마룬클라운"]
                                },
                                "Chromis": {  # 크로미스
                                    "viridis": ["Blue-green chromis", "Green chromis", "그린크로미스"],
                                    "cyanea": ["Blue reef chromis", "Blue chromis", "블루크로미스"],
                                    "atripectoralis": ["Black-axil chromis", "Blackfin chromis", "블랙핀크로미스"],
                                    "vanderbilti": ["Vanderbilt's chromis", "반더빌트크로미스"],
                                    "dimidiata": ["Half and half chromis", "하프앤하프크로미스"]
                                },
                                "Dascyllus": {  # 댐셀피쉬
                                    "trimaculatus": ["Three-spot dascyllus", "Domino damsel", "도미노댐셀"],
                                    "aruanus": ["White-tailed dascyllus", "Humbug dascyllus", "험버그댐셀"],
                                    "melanurus": ["Four-stripe damselfish", "Blacktail dascyllus", "블랙테일댐셀"],
                                    "carneus": ["Cloudy damsel", "클라우디댐셀"]
                                },
                                "Chrysiptera": {
                                    "cyanea": ["Blue devil", "Sapphire devil", "블루데빌"],
                                    "parasema": ["Yellowtail blue damsel", "옐로우테일블루댐셀"],
                                    "hemicyanea": ["Azure damsel", "애저댐셀"]
                                }
                            },
                            "Chaetodontidae": {  # 나비고기과
                                "Chaetodon": {
                                    "auriga": ["Threadfin butterflyfish", "Cross-stripe butterfly", "쓰레드핀버터플라이"],
                                    "lunula": ["Raccoon butterflyfish", "Crescent-masked butterflyfish", "라쿤버터플라이"],
                                    "vagabundus": ["Vagabond butterflyfish", "Crisscross butterflyfish", "바가본드버터플라이"],
                                    "rafflesii": ["Latticed butterflyfish", "Raffle's butterflyfish", "래플스버터플라이"],
                                    "melannotus": ["Blackback butterflyfish", "Black-backed butterflyfish", "블랙백버터플라이"],
                                    "collare": ["Pakistani butterflyfish", "Redtail butterflyfish", "파키스탄버터플라이"],
                                    "semilarvatus": ["Golden butterflyfish", "Addis butterflyfish", "골든버터플라이"],
                                    "fasciatus": ["Diagonal butterflyfish", "Red Sea raccoon butterflyfish", "다이아고날버터플라이"],
                                    "lineolatus": ["Lined butterflyfish", "라인드버터플라이"],
                                    "miliaris": ["Lemon butterflyfish", "레몬버터플라이"]
                                },
                                "Heniochus": {
                                    "acuminatus": ["Pennant coralfish", "Longfin bannerfish", "페넌트코랄피쉬"],
                                    "diphreutes": ["Schooling bannerfish", "False moorish idol", "스쿨링배너피쉬"],
                                    "singularius": ["Singular bannerfish", "싱귤러배너피쉬"]
                                },
                                "Forcipiger": {
                                    "flavissimus": ["Yellow longnose butterflyfish", "Forceps fish", "옐로우롱노즈"],
                                    "longirostris": ["Longnose butterflyfish", "Big longnose butterflyfish", "빅롱노즈"]
                                },
                                "Chelmon": {
                                    "rostratus": ["Copperband butterflyfish", "Beaked butterflyfish", "코퍼밴드버터플라이"]
                                }
                            },
                            "Labridae": {  # 놀래기과
                                "Labroides": {
                                    "dimidiatus": ["Bluestreak cleaner wrasse", "블루스트릭클리너"],
                                    "bicolor": ["Bicolor cleaner wrasse", "바이컬러클리너"]
                                },
                                "Thalassoma": {
                                    "bifasciatum": ["Bluehead wrasse", "블루헤드놀래기"],
                                    "lunare": ["Moon wrasse", "Green moon wrasse", "문놀래기"],
                                    "lutescens": ["Sunset wrasse", "선셋놀래기"]
                                },
                                "Pseudocheilinus": {
                                    "hexataenia": ["Six-line wrasse", "식스라인놀래기"],
                                    "tetrataenia": ["Four-line wrasse", "포라인놀래기"]
                                },
                                "Cirrhilabrus": {
                                    "cyanopleura": ["Blueside fairy wrasse", "블루사이드페어리"],
                                    "scottorum": ["Scott's fairy wrasse", "스콧페어리"]
                                }
                            }
                        },
                        "Gobiiformes": {  # 망둑어목
                            "Gobiidae": {  # 망둑어과
                                "Gobiodon": {
                                    "okinawae": ["Yellow clown goby", "Okinawa goby", "옐로우클라운고비"],
                                    "atrangulatus": ["Green clown goby", "그린클라운고비"]
                                },
                                "Nemateleotris": {
                                    "magnifica": ["Fire goby", "Firefish", "파이어고비"],
                                    "decora": ["Purple firefish", "Decorated firefish", "퍼플파이어피쉬"]
                                },
                                "Valenciennea": {
                                    "puellaris": ["Orange-spotted goby", "Maiden goby", "오렌지스팟고비"],
                                    "strigata": ["Golden-head sleeper goby", "골든헤드슬리퍼"]
                                },
                                "Amblyeleotris": {
                                    "wheeleri": ["Wheeler's shrimp goby", "휠러쉬림프고비"],
                                    "steinitzi": ["Steinitz's shrimp goby", "스타이니츠쉬림프고비"]
                                }
                            }
                        },
                        "Blenniiformes": {  # 블레니목
                            "Blenniidae": {  # 블레니과
                                "Meiacanthus": {
                                    "grammistes": ["Striped poison-fang blenny", "스트라이프드포이즌블레니"],
                                    "smithi": ["Smith's fang blenny", "스미스팽블레니"]
                                },
                                "Ecsenius": {
                                    "bicolor": ["Bicolor blenny", "바이컬러블레니"],
                                    "midas": ["Midas blenny", "미다스블레니"]
                                },
                                "Salarias": {
                                    "fasciatus": ["Jewelled blenny", "Lawnmower blenny", "론모어블레니"]
                                }
                            }
                        }
                    },
                    "Tetraodontomorpha": {  # 복어상목
                        "Tetraodontiformes": {  # 복어목
                            "Tetraodontidae": {  # 복어과
                                "Arothron": {
                                    "nigropunctatus": ["Blackspotted puffer", "Dog-faced puffer", "도그페이스퍼퍼"],
                                    "meleagris": ["Guineafowl puffer", "Golden puffer", "기니파울퍼퍼"],
                                    "hispidus": ["White-spotted puffer", "Stars and stripes puffer", "화이트스팟퍼퍼"],
                                    "mappa": ["Map puffer", "Scribbled puffer", "맵퍼퍼"]
                                },
                                "Canthigaster": {
                                    "valentini": ["Valentini puffer", "Black-saddled toby", "발렌티니퍼퍼"],
                                    "solandri": ["Spotted sharpnose puffer", "Blue-spotted puffer", "블루스팟퍼퍼"],
                                    "coronata": ["Crowned puffer", "크라운드퍼퍼"],
                                    "janthinoptera": ["Honeycomb toby", "허니컴토비"]
                                }
                            },
                            "Balistidae": {  # 쥐치과 (트리거피쉬)
                                "Rhinecanthus": {
                                    "aculeatus": ["Lagoon triggerfish", "Blackbar triggerfish", "라군트리거"],
                                    "rectangulus": ["Wedgetail triggerfish", "Rectangle triggerfish", "웨지테일트리거"],
                                    "assasi": ["Picasso triggerfish", "피카소트리거"]
                                },
                                "Balistoides": {
                                    "conspicillum": ["Clown triggerfish", "Big-spotted triggerfish", "클라운트리거"]
                                },
                                "Odonus": {
                                    "niger": ["Red-toothed triggerfish", "Blue triggerfish", "블루트리거"]
                                },
                                "Sufflamen": {
                                    "bursa": ["Scythe triggerfish", "Boomerang triggerfish", "사이드트리거"]
                                }
                            },
                            "Monacanthidae": {  # 쥐치과 (파일피쉬)
                                "Oxymonacanthus": {
                                    "longirostris": ["Harlequin filefish", "Longnose filefish", "할리퀸파일피쉬"]
                                },
                                "Pervagor": {
                                    "spilosoma": ["Fantail filefish", "팬테일파일피쉬"],
                                    "janthinosoma": ["Blackbar filefish", "블랙바파일피쉬"]
                                }
                            },
                            "Ostraciidae": {  # 상자고기과
                                "Lactoria": {
                                    "cornuta": ["Longhorn cowfish", "롱혼카우피쉬"]
                                },
                                "Ostracion": {
                                    "cubicus": ["Yellow boxfish", "Polka-dot boxfish", "옐로우박스피쉬"],
                                    "meleagris": ["Spotted boxfish", "Blue boxfish", "스팟티드박스피쉬"]
                                }
                            }
                        }
                    },
                    "Percomorpha": {  # 농어상목
                        "Perciformes": {  # 농어목
                            "Serranidae": {  # 바리과
                                "Anthias": {
                                    "anthias": ["Swallowtail sea perch", "스왈로우테일안티아스"]
                                },
                                "Pseudanthias": {
                                    "squamipinnis": ["Lyretail anthias", "라이어테일안티아스"],
                                    "bicolor": ["Bicolor anthias", "바이컬러안티아스"],
                                    "tuka": ["Purple queen anthias", "퍼플퀸안티아스"]
                                },
                                "Cephalopholis": {
                                    "miniata": ["Coral hind", "Coral grouper", "코랄하인드"]
                                }
                            },
                            "Pseudochromidae": {  # 의돔과
                                "Pseudochromis": {
                                    "fridmani": ["Orchid dottyback", "Fridman's dottyback", "오키드도티백"],
                                    "paccagnellae": ["Royal dottyback", "Bicolor dottyback", "로얄도티백"],
                                    "aldabraensis": ["Neon dottyback", "네온도티백"]
                                }
                            },
                            "Apogonidae": {  # 천축어과
                                "Sphaeramia": {
                                    "nematoptera": ["Pajama cardinalfish", "파자마카디널"]
                                },
                                "Pterapogon": {
                                    "kauderni": ["Banggai cardinalfish", "방가이카디널"]
                                }
                            }
                        },
                        "Syngnathiformes": {  # 실고기목
                            "Syngnathidae": {  # 실고기과
                                "Hippocampus": {
                                    "kuda": ["Yellow seahorse", "Common seahorse", "옐로우씨호스"],
                                    "erectus": ["Lined seahorse", "Northern seahorse", "라인드씨호스"],
                                    "reidi": ["Longsnout seahorse", "Brazilian seahorse", "롱스나웃씨호스"]
                                },
                                "Doryrhamphus": {
                                    "excisus": ["Bluestripe pipefish", "블루스트라이프파이프피쉬"]
                                }
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
        """완전한 분류학적 계층에 따른 디렉토리 구조 생성"""
        base_dir.mkdir(exist_ok=True)
        
        def create_recursive_dirs(current_dict, current_path):
            """재귀적으로 디렉토리 구조 생성"""
            for key, value in current_dict.items():
                new_path = current_path / key
                new_path.mkdir(exist_ok=True)
                
                if isinstance(value, dict):
                    # 아직 더 깊은 계층이 있음
                    if any(isinstance(v, dict) for v in value.values()):
                        create_recursive_dirs(value, new_path)
                    else:
                        # 속(genus) 레벨에 도달 - 종별 폴더 생성
                        for genus_name, species_dict in value.items():
                            genus_path = new_path / genus_name
                            genus_path.mkdir(exist_ok=True)
                            
                            for species_name in species_dict.keys():
                                species_dir = genus_path / f"{genus_name}_{species_name}"
                                species_dir.mkdir(exist_ok=True)
        
        create_recursive_dirs(self.fish_taxonomy, base_dir)
        self.logger.info(f"완전한 분류학적 디렉토리 구조 생성 완료: {base_dir}")
    
    def get_taxonomy_statistics(self) -> Dict[str, Any]:
        """완전한 분류 체계 통계 반환"""
        total_species = 0
        total_genera = set()
        total_families = 0
        total_orders = 0
        class_stats = {}
        
        def count_recursive(current_dict, level=0):
            """재귀적으로 분류 체계 통계 계산"""
            nonlocal total_species, total_families, total_orders
            
            species_count = 0
            families_count = 0
            orders_count = 0
            
            for key, value in current_dict.items():
                if isinstance(value, dict):
                    if any(isinstance(v, dict) for v in value.values()):
                        # 더 깊은 계층이 있음
                        sub_stats = count_recursive(value, level + 1)
                        species_count += sub_stats['species']
                        families_count += sub_stats['families']
                        orders_count += sub_stats['orders']
                        
                        # 목(order) 레벨 카운트
                        if level == 1:  # Class -> Subclass/Superorder -> Order
                            orders_count += 1
                    else:
                        # 속(genus) 레벨에 도달
                        families_count += 1  # 현재 키가 과(family)
                        for genus_name, species_dict in value.items():
                            total_genera.add(genus_name)
                            species_count += len(species_dict)
            
            return {
                'species': species_count,
                'families': families_count,
                'orders': orders_count
            }
        
        for class_name, class_data in self.fish_taxonomy.items():
            class_result = count_recursive(class_data, 0)
            total_species += class_result['species']
            total_families += class_result['families']
            total_orders += class_result['orders']
            
            class_stats[class_name] = {
                'species': class_result['species'],
                'families': class_result['families'],
                'orders': class_result['orders']
            }
        
        return {
            'total_species': total_species,
            'total_genera': len(total_genera),
            'total_families': total_families,
            'total_orders': total_orders,
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