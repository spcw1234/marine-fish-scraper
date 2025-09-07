"""
Coral taxonomy management system for marine coral classification
Complete database of ornamental and reef-building coral species
"""
from typing import Dict, List, Optional, Tuple, Any
from .taxonomy_manager import TaxonomyManager, SpeciesInfo


class CoralTaxonomyManager(TaxonomyManager):
    """산호 분류학적 데이터 관리자"""

    def __init__(self, taxonomy_file: Optional[str] = None):
        # logger 초기화 (부모 클래스에서 필요)
        from .logger import get_logger
        from .error_handler import get_error_handler
        self.logger = get_logger("coral_taxonomy_manager")
        self.error_handler = get_error_handler()

        # 변이(트레이드 네임) 매핑
        # key: "Genus species" -> { variant_name: [aliases...] }
        self.variants_map: Dict[str, Dict[str, List[str]]] = {}

        # 산호 분류학적 계층구조 설정 (관상용 중심으로 확장)
        self.fish_taxonomy = {
            "Anthozoa": {  # 산호강
                "Scleractinia": {  # 경산호목 (석회질 골격)
                    "Caryophylliidae": {  # 정향산호과
                        "Euphyllia": {
                            "ancora": {
                                "__common__": [
                                    "Hammer coral",
                                    "Anchor coral",
                                    "해머코랄",
                                    "앵커코랄",
                                ],
                                "__variants__": {
                                    "Golden Hammer": [
                                        "Gold Hammer",
                                        "Golden Hammer",
                                    ],
                                    "Toxic Green Hammer": [
                                        "Toxic Green Hammer",
                                    ],
                                    "Orange Hammer": ["Orange Hammer"],
                                },
                            },
                            "glabrescens": {
                                "__common__": [
                                    "Torch coral",
                                    "토치코랄",
                                ],
                                "__variants__": {
                                    "Gold Torch": [
                                        "Gold Torch",
                                        "Indo Gold Torch",
                                    ],
                                    "Dragon Soul Torch": ["Dragon Soul Torch"],
                                    "Hellfire Torch": ["Hellfire Torch"],
                                    "NY Knicks Torch": ["NY Knicks Torch"],
                                },
                            },
                            "divisa": [
                                "Frogspawn coral",
                                "개구리알코랄",
                                "Octospawn",
                            ],
                            "paraancora": [
                                "Branching hammer coral",
                                "브랜칭해머코랄",
                            ],
                        },
                        "Catalaphyllia": {
                            "jardinei": [
                                "Elegance coral",
                                "엘레간스코랄",
                                "Ultra Elegance",
                            ],
                        },
                        "Plerogyra": {
                            "sinuosa": [
                                "Bubble coral",
                                "버블코랄",
                            ],
                        },
                    },
                    "Acroporidae": {  # 테이블산호과
                        "Acropora": {
                            "millepora": [
                                "Staghorn coral",
                                "스태그혼코랄",
                                "Rainbow Mille",
                                "Ultra Mille",
                            ],
                            "tenuis": {
                                "__common__": [
                                    "Acropora tenuis",
                                    "테누이스",
                                ],
                                "__variants__": {
                                    "Walt Disney": [
                                        "Walt Disney tenuis",
                                        "WD tenuis",
                                    ],
                                    "Homewrecker": ["Homewrecker tenuis"],
                                    "ASD Rainbow": ["ASD Rainbow tenuis"],
                                    "TGC Cherry Bomb": [
                                        "TGC Cherry Bomb tenuis",
                                    ],
                                    "Cotton Candy": ["Cotton Candy tenuis"],
                                },
                            },
                            "cervicornis": [
                                "Elkhorn coral",
                                "엘크혼코랄",
                            ],
                            "formosa": [
                                "Blue tip staghorn",
                                "블루팁스태그혼",
                            ],
                            "granulosa": [
                                "Granular table coral",
                                "그래뉼러테이블코랄",
                            ],
                            "valida": [
                                "Plate coral",
                                "플레이트코랄",
                            ],
                            "microclados": [
                                "Strawberry Shortcake",
                                "SSC",
                                "스트로베리 쇼트케이크",
                            ],
                            "echinata": [
                                "Blue bottlebrush",
                                "블루 보틀브러시",
                            ],
                            "loripes": [
                                "Loripes",
                            ],
                        },
                        "Montipora": {
                            "digitata": [
                                "Finger coral",
                                "핑거코랄",
                                "Forest Fire digitata",
                                "FF digitata",
                            ],
                            "capricornis": [
                                "Plating montipora",
                                "플레이팅몬티포라",
                                "Red Monti Cap",
                                "Green Monti Cap",
                            ],
                            "confusa": [
                                "Encrusting montipora",
                                "엔크러스팅몬티포라",
                            ],
                            "setosa": [
                                "Velvet finger coral",
                                "벨벳핑거코랄",
                            ],
                            "danae": [
                                "Sunset montipora",
                                "Superman montipora",
                                "Rainbow montipora",
                                "선셋 몬티",
                                "슈퍼맨 몬티",
                            ],
                            "spongodes": [
                                "Jedi Mind Trick",
                                "제다이 마인드 트릭",
                            ],
                        },
                    },
                    "Pocilloporidae": {  # 꽃산호과
                        "Pocillopora": {
                            "damicornis": [
                                "Cauliflower coral",
                                "콜리플라워코랄",
                            ],
                            "verrucosa": [
                                "Cauliflower coral",
                                "콜리플라워코랄",
                            ],
                        },
                        "Stylophora": {
                            "pistillata": [
                                "Cat's paw coral",
                                "캣츠포코랄",
                            ],
                        },
                        "Seriatopora": {
                            "hystrix": [
                                "Thin birdsnest coral",
                                "씬버드네스트코랄",
                                "Birdsnest coral",
                            ],
                            "caliendrum": [
                                "Green birdsnest coral",
                                "그린 버드네스트",
                            ],
                        },
                    },
                    "Poritidae": {  # 구멍산호과
                        "Porites": {
                            "lutea": [
                                "Yellow porites",
                                "옐로우포리테스",
                            ],
                            "cylindrica": [
                                "Finger porites",
                                "핑거포리테스",
                            ],
                        },
                        "Goniopora": {
                            "lobata": [
                                "Flower pot coral",
                                "플라워팟코랄",
                                "Rainbow goni",
                                "Long tentacle goni",
                                "Short tentacle goni",
                            ],
                            "stokesi": [
                                "Stokes flowerpot coral",
                                "스토크스플라워팟코랄",
                            ],
                        },
                        "Alveopora": {
                            "spongiosa": [
                                "Spongy flowerpot coral",
                                "스펀지플라워팟코랄",
                            ],
                        },
                    },
                    "Faviidae": {  # 꿀벌집산호과
                        "Favia": {
                            "favus": [
                                "Honeycomb coral",
                                "허니컴코랄",
                            ],
                        },
                        "Favites": {
                            "abdita": [
                                "Larger star coral",
                                "라지스타코랄",
                            ],
                        },
                        "Platygyra": {
                            "daedalea": [
                                "Lesser valley coral",
                                "레서밸리코랄",
                            ],
                        },
                    },
                    "Fungiidae": {  # 버섯산고과
                        "Fungia": {
                            "granulosa": [
                                "Plate coral",
                                "플레이트코랄",
                            ],
                        },
                        "Cycloseris": {
                            "cyclolites": [
                                "Disk coral",
                                "디스크코랄",
                            ],
                        },
                    },
                    "Dendrophylliidae": {  # 나무산호과
                        "Tubastrea": {
                            "coccinea": [
                                "Orange cup coral",
                                "오렌지컵코랄",
                            ],
                            "faulkneri": [
                                "Yellow sun coral",
                                "옐로우선코랄",
                            ],
                        },
                        "Dendrophyllia": {
                            "gracilis": [
                                "Yellow tree coral",
                                "옐로우트리코랄",
                            ],
                        },
                    },
                    "Agariciidae": {  # 레프토세리스/아가리키아과
                        "Leptoseris": {
                            "scabra": [
                                "Jack-o-Lantern leptoseris",
                                "JOL leptoseris",
                                "잭오랜턴 레프토세리스",
                            ],
                            "hawaiiensis": [
                                "Leptoseris hawaiiensis",
                                "Deepwater leptoseris",
                            ],
                        },
                    },
                    "Lobophylliidae": {  # 차리스/록코랄 계열
                        "Echinophyllia": {
                            "aspera": [
                                "Chalice coral",
                                "Hollywood Stunner",
                                "레인보우 차리스",
                            ],
                        },
                        "Homophyllia": {
                            "bowerbanki": [
                                "Acanthastrea bowerbanki",
                                "Bowerbanki",
                                "바워뱅키",
                            ],
                            "australis": [
                                "Aussie scoly",
                                "Scolymia australis",
                                "스콜리",
                            ],
                        },
                    },
                    "Merulinidae": {  # 메루리나과
                        "Merulina": {
                            "ampliata": [
                                "Lettuce coral",
                                "레터스코랄",
                            ],
                        },
                        "Hydnophora": {
                            "exesa": [
                                "Horn coral",
                                "혼코랄",
                            ],
                        },
                    },
                    "Mussidae": {  # 근육산호과
                        "Lobophyllia": {
                            "hemprichii": [
                                "Lobed brain coral",
                                "로브드브레인코랄",
                            ],
                        },
                        "Symphyllia": {
                            "radians": [
                                "Ridge coral",
                                "리지코랄",
                            ],
                        },
                        "Scolymia": {
                            "lacera": [
                                "Artichoke coral",
                                "아티초크코랄",
                            ],
                        },
                        "Cynarina": {
                            "lacrymalis": [
                                "Button coral",
                                "버튼코랄",
                            ],
                        },
                        "Acanthastrea": {
                            "lordhowensis": [
                                "Lord Howe acan",
                                "로드하우아칸",
                                "Acan lord",
                                "Rainbow acan",
                            ],
                            "echinata": [
                                "Starry cup coral",
                                "스타리컵코랄",
                            ],
                        },
                        "Micromussa": {
                            "lordhowensis": [
                                "Acan lord",
                                "아칸로드",
                                "Holy Grail micromussa",
                                "레인보우 마이크로무사",
                            ],
                        },
                    },
                    "Trachyphylliidae": {  # 트라키필리아과
                        "Trachyphyllia": {
                            "geoffroyi": [
                                "Open brain coral",
                                "오픈브레인코랄",
                                "Rainbow trachy",
                                "Ultra trachy",
                            ],
                        },
                    },
                },
                "Alcyonacea": {  # 연산호목 (유연한 조직)
                    "Alcyoniidae": {  # 연산호과
                        "Sinularia": {
                            "flexibilis": [
                                "Flexible leather coral",
                                "플렉시블레더코랄",
                            ],
                            "dura": [
                                "Cabbage leather coral",
                                "캐비지레더코랄",
                            ],
                        },
                        "Sarcophyton": {
                            "glaucum": [
                                "Yellow leather coral",
                                "옐로우레더코랄",
                            ],
                            "elegans": [
                                "Elegant leather coral",
                                "엘레간트레더코랄",
                            ],
                        },
                        "Lobophytum": {
                            "pauciflorum": [
                                "Devil's hand coral",
                                "데빌즈핸드코랄",
                            ],
                        },
                    },
                    "Nephtheidae": {  # 넵티아과
                        "Nephthea": {
                            "brassica": [
                                "Cabbage coral",
                                "캐비지코랄",
                            ],
                        },
                        "Dendronephthya": {
                            "gigantea": [
                                "Carnation coral",
                                "카네이션코랄",
                            ],
                        },
                    },
                    "Xeniidae": {  # 제니아과
                        "Xenia": {
                            "umbellata": [
                                "Pulsing xenia",
                                "펄싱제니아",
                            ],
                        },
                        "Anthelia": {
                            "glauca": [
                                "Waving hand coral",
                                "웨이빙핸드코랄",
                            ],
                        },
                    },
                },
                "Corallimorpharia": {  # 코랄리모르파리아(머슈룸)
                    "Discosomatidae": {
                        "Discosoma": {
                            "sp.": {
                                "__common__": [
                                    "Mushroom coral",
                                    "머슈룸",
                                ],
                                "__variants__": {
                                    "Panty Dropper": ["Panty Dropper"],
                                    "Jawbreaker": ["Jawbreaker"],
                                    "Sunkist": ["Sunkist"],
                                },
                            },
                        },
                        "Rhodactis": {
                            "indosinensis": [
                                "Bounce mushroom",
                                "Sunkist Bounce",
                                "바운스 머슈룸",
                            ],
                        },
                    },
                    "Ricordeidae": {
                        "Ricordea": {
                            "yuma": [
                                "Ricordea yuma",
                                "Rainbow yuma",
                                "레인보우 유마",
                            ],
                            "florida": [
                                "Ricordea florida",
                                "Neon green ricordea",
                                "리코디아 플로리다",
                            ],
                        },
                    },
                },
                "Zoantharia": {  # 조안토목 (단체 폴립)
                    "Zoanthidae": {  # 조안토과
                        "Zoanthus": {
                            "sociatus": [
                                "Green button polyps",
                                "그린버튼폴립",
                            ],
                            "gigantus": [
                                "Giant zoanthids",
                                "자이언트조안토",
                            ],
                            "sp.": [
                                "Rasta zoa",
                                "Sunny D zoa",
                                "Utter Chaos",
                                "Radioactive Dragon Eye",
                                "Eagle Eye",
                                "Armor of God",
                                "Scrambled Eggs",
                                "Fruit Loops",
                                "Bowser",
                                "LA Lakers",
                                "라스타 조아",
                                "써니디 조아",
                                "어터 카오스",
                            ],
                        },
                        "Palythoa": {
                            "caribaeorum": [
                                "Brown button polyps",
                                "브라운버튼폴립",
                            ],
                        },
                    },
                    "Parazoanthidae": {  # 파라조안토과
                        "Parazoanthus": {
                            "gracilis": [
                                "Yellow polyps",
                                "옐로우폴립",
                            ],
                        },
                    },
                },
            }
        }

        # 과(Family) 태그 지정 (산호 특화)
        self.family_tags: Dict[str, str] = {
            # 핵심 관상용 산고 (사육 용이/인기)
            "Caryophylliidae": "core",      # Euphyllia 등 LPS
            "Acroporidae": "core",          # SPS 대표
            "Pocilloporidae": "core",       # SPS 초보용
            "Mussidae": "core",             # Brain/Button 계열 LPS
            "Zoanthidae": "core",           # 버튼 폴립
            "Ricordeidae": "core",          # 리코디아 머슈룸
            "Discosomatidae": "core",       # 디스코소마/로드액티스 머슈룸
            "Agariciidae": "core",          # 레프토세리스 (조명 강도 주의)
            
            # 확장 (고급자/특수 관리)
            "Poritidae": "extended",        # Goniopora (어려움)
            "Fungiidae": "extended",        # 플레이트 코랄
            "Dendrophylliidae": "extended",  # NPS (먹이 공급 필요)
            "Alcyoniidae": "extended",      # 소프트 코랄 (수질 민감)
            "Nephtheidae": "extended",      # 고급 소프트
            "Xeniidae": "extended",         # 증식력 강함
            "Lobophylliidae": "extended",   # 차리스/바워뱅키/스콜리
            
            # 제외 (매우 어려움/특수 환경)
            "Trachyphylliidae": "exclude",  # 매우 예민
        }

        # 인덱스 생성 (산호 특화)
        self._build_indexes()
        
        total_species = len(self.species_index)
        self.logger.info(f"산호 분류 체계 인덱스 생성 완료: {total_species}종")
        
        # 부모 클래스의 taxonomy_file 처리만
        if taxonomy_file:
            self.load_taxonomy_from_file(taxonomy_file)

    def _process_family_data(
        self, family_data, family_name, order_name, class_name
    ):
        """과 데이터 처리 (variants 및 아과 구조 지원)"""
        for key, value in family_data.items():
            if not isinstance(value, dict):
                continue

            # 아과 감지
            if key.endswith('inae'):
                self._process_family_data(
                    value, family_name, order_name, class_name
                )
                continue

            # 속 처리
            genus_name = key
            genus_data = value
            if not isinstance(genus_data, dict):
                continue

            for species_name, node in genus_data.items():
                # 기본 리스트 형태: 기존 방식 유지
                if isinstance(node, list):
                    common_names = node
                    species_info = SpeciesInfo(
                        genus=genus_name,
                        species=species_name,
                        common_names=common_names,
                        family=family_name,
                        order=order_name,
                        class_name=class_name,
                    )
                    self._add_to_indexes(species_info)
                    continue

                # dict 형태: {"__common__": [...], "__variants__": {...}}
                if isinstance(node, dict):
                    common_names = node.get("__common__", [])
                    variants = node.get("__variants__", {})

                    species_info = SpeciesInfo(
                        genus=genus_name,
                        species=species_name,
                        common_names=common_names,
                        family=family_name,
                        order=order_name,
                        class_name=class_name,
                    )
                    self._add_to_indexes(species_info)

                    if variants:
                        self._register_variants(species_info, variants)

    def _register_variants(
        self, species_info: SpeciesInfo, variants: Dict[str, List[str]]
    ):
        """변이(트레이드 네임) 정보를 내부 맵과 공용명 인덱스에 등록"""
        key = species_info.scientific_name
        self.variants_map[key] = {}

        for variant_name, aliases in variants.items():
            alias_list = aliases or []
            self.variants_map[key][variant_name] = alias_list

            # 변이명과 별칭들을 공용명 인덱스에 추가 (검색 용이)
            for name in [variant_name] + alias_list:
                name_lower = name.lower()
                if name_lower not in self.common_name_index:
                    self.common_name_index[name_lower] = []
                self.common_name_index[name_lower].append(species_info)

    def get_variants(self, genus: str, species: str) -> List[str]:
        """해당 종의 변이(트레이드 네임) 목록 반환"""
        key = f"{genus} {species}"
        return list(self.variants_map.get(key, {}).keys())

    def get_variant_aliases(
        self, genus: str, species: str, variant: str
    ) -> List[str]:
        """특정 변이의 별칭 목록 반환"""
        key = f"{genus} {species}"
        return self.variants_map.get(key, {}).get(variant, [])

    def _build_indexes(self):
        """산호 전용 인덱스 생성 (Anthozoa 처리)"""
        self.species_index: Dict[str, SpeciesInfo] = {}
        self.genus_index: Dict[str, List[SpeciesInfo]] = {}
        self.family_index: Dict[Tuple[str, str, str], List[SpeciesInfo]] = {}
        self.common_name_index: Dict[str, List[SpeciesInfo]] = {}

        # Anthozoa 처리
        anthozoa_data = self.fish_taxonomy.get("Anthozoa", {})
        if anthozoa_data:
            self._process_coral_data(anthozoa_data, "Anthozoa")

        self.logger.info(f"분류 체계 인덱스 생성 완료: {len(self.species_index)}종")

    def _process_coral_data(self, data, class_name):
        """Anthozoa 데이터 재귀 처리"""
        def find_families_recursive(current_data: Dict[str, Any]):
            """재귀적으로 모든 과(Family) 찾기"""
            for key, value in current_data.items():
                if not isinstance(value, dict):
                    continue
                
                # 과(Family) 감지 - 'idae'로 끝나는 것
                if key.endswith('idae'):
                    # 과를 찾았으면 상위 목(order) 찾기
                    order_name = self._find_order_name(data, key)
                    self._process_family_data(
                        value,
                        key,
                        order_name,
                        class_name,
                    )
                else:
                    # 과가 아니면 더 깊이 탐색
                    find_families_recursive(value)
        
        # 재귀 탐색 시작
        find_families_recursive(data)

    def get_all_families(self, ornamental_only: bool = True):
        """산호(Anthozoa) 과 목록 반환 (class, order, family)

        기본 구현은 어류 중심이라 Anthozoa가 누락되어 빈 목록이 되어
        산호 메뉴에서 가족 선택 리스트가 보이지 않는 문제가 있어 오버라이드합니다.
        """
        families: List[Tuple[str, str, str]] = []

        def include_family(family_name: str) -> bool:
            if not ornamental_only:
                return True
            tag = self.family_tags.get(family_name, "core")
            return tag != "exclude"

        for (
            class_name, order_name, family_name
        ), _species in self.family_index.items():
            if class_name == "Anthozoa" and include_family(family_name):
                families.append((class_name, order_name, family_name))

        families.sort(key=lambda x: (x[1].lower(), x[2].lower()))
        return families

    def get_taxonomy_statistics(self) -> Dict[str, Any]:
        """산고 분류 체계 통계 반환"""
        stats = super().get_taxonomy_statistics()
        
        # 산호 특화 통계 추가
        coral_stats = {
            'scleractinia_species': 0,  # 경산호
            'alcyonacea_species': 0,    # 연산고
            'zoantharia_species': 0,    # 조안토
            'lps_families': 0,          # Large Polyp Stony
            'sps_families': 0,          # Small Polyp Stony
            'soft_coral_families': 0,   # Soft Coral
        }
        
        # 목별 종 수 계산
        for species_info in self.species_index.values():
            if species_info.order == "Scleractinia":
                coral_stats['scleractinia_species'] += 1
            elif species_info.order == "Alcyonacea":
                coral_stats['alcyonacea_species'] += 1
            elif species_info.order == "Zoantharia":
                coral_stats['zoantharia_species'] += 1
        
        # 과 타입별 계산
        lps_families = ["Caryophylliidae", "Mussidae", "Trachyphylliidae"]
        sps_families = ["Acroporidae", "Pocilloporidae"]
        soft_families = ["Alcyoniidae", "Nephtheidae", "Xeniidae"]
        
        for family_key in self.family_index.keys():
            family_name = family_key[2]  # (class, order, family)
            if family_name in lps_families:
                coral_stats['lps_families'] += 1
            elif family_name in sps_families:
                coral_stats['sps_families'] += 1
            elif family_name in soft_families:
                coral_stats['soft_coral_families'] += 1
        
        stats.update(coral_stats)
        return stats
