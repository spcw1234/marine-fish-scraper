"""
Taxonomic data management system for marine fish classification
Complete database of marine ornamental fish species
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from .logger import get_logger
from .error_handler import get_error_handler, handle_gracefully


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
        return (
            self.common_names[0]
            if self.common_names
            else self.scientific_name
        )

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "genus": self.genus,
            "species": self.species,
            "common_names": self.common_names,
            "family": self.family,
            "order": self.order,
            "class": self.class_name,
        }


class TaxonomyManager:
    """분류학적 데이터 관리자"""

    def __init__(self, taxonomy_file: Optional[str] = None):
        self.logger = get_logger("taxonomy_manager")
        self.error_handler = get_error_handler()

        # 완전한 분류학적 계층구조 (현재 유통되는 모든 관상용 해수어)
        self.fish_taxonomy = {
            "Chondrichthyes": {  # 연골어강
                "Carcharhiniformes": {  # 흉상어목
                    "Hemiscylliidae": {  # 대나무상어과
                        "Chiloscyllium": {
                            "punctatum": [
                                "Brownbanded bamboo shark",
                                "갈색줄무늬 대나무상어",
                            ],
                            "plagiosum": [
                                "Whitespotted bamboo shark",
                                "흰점 대나무상어",
                            ],
                            "griseum": ["Grey bamboo shark", "회색 대나무상어"],
                            "hasselti": [
                                "Hasselt's bamboo shark",
                                "하셀트 대나무상어",
                            ],
                            "arabicum": [
                                "Arabian bamboo shark",
                                "아라비안 대나무상어",
                            ],
                            "burmensis": [
                                "Burmese bamboo shark",
                                "버마 대나무상어",
                            ],
                        },
                        "Hemiscyllium": {
                            "ocellatum": [
                                "Epaulette shark",
                                "견장상어",
                                "Walking shark",
                            ],
                            "freycineti": [
                                "Indonesian walking shark",
                                "인도네시아 견장상어",
                            ],
                            "hallstromi": [
                                "Papuan epaulette shark",
                                "파푸아 견장상어",
                            ],
                            "henryi": [
                                "Henry's epaulette shark",
                                "헨리 견장상어",
                            ],
                            "strahani": [
                                "Hooded carpet shark",
                                "후드 카펫상어",
                            ],
                            "trispeculare": [
                                "Speckled carpet shark",
                                "스펙클드 카펫상어",
                            ],
                        },
                    },
                    "Scyliorhinidae": {  # 고양이상어과
                        "Atelomycterus": {
                            "marmoratus": [
                                "Coral catshark",
                                "Marbled catshark",
                                "마블 캣샤크",
                            ],
                            "macleayi": [
                                "Australian marbled catshark",
                                "오스트레일리안 마블 캣샤크",
                            ],
                        },
                        "Halaelurus": {
                            "natalensis": [
                                "Tiger catshark",
                                "타이거 캣샤크",
                            ],
                        },
                        "Scyliorhinus": {
                            "retifer": [
                                "Chain catshark",
                                "체인 캣샤크",
                            ],
                            "torazame": [
                                "Cloudy catshark",
                                "클라우디 캣샤크",
                            ],
                        },
                    },
                    "Ginglymostomatidae": {  # 간호상어과
                        "Ginglymostoma": {
                            "cirratum": [
                                "Nurse shark",
                                "간호상어",
                            ],
                        },
                        "Nebrius": {
                            "ferrugineus": [
                                "Tawny nurse shark",
                                "토니 간호상어",
                            ],
                        },
                    },
                },
                "Rajiformes": {  # 가오리목
                    "Dasyatidae": {  # 참가오리과
                        "Taeniura": {
                            "lymma": [
                                "Blue-spotted stingray",
                                "Bluespotted ribbontail ray",
                                "블루스팟가오리",
                            ],
                            "grabata": [
                                "Round ribbontail ray",
                                "라운드 리본테일 가오리",
                            ],
                        },
                        "Dasyatis": {
                            "pastinaca": [
                                "Common stingray",
                                "커먼 스팅레이",
                            ],
                            "americana": [
                                "Southern stingray",
                                "서던 스팅레이",
                            ],
                        },
                        "Himantura": {
                            "uarnak": [
                                "Honeycomb stingray",
                                "허니콤 스팅레이",
                            ],
                            "gerrardi": [
                                "Sharpnose stingray",
                                "샤프노즈 스팅레이",
                            ],
                        },
                    },
                    "Rhinobatidae": {  # 기타가오리과
                        "Rhinobatos": {
                            "productus": [
                                "Shovelnose guitarfish",
                                "쇼블노즈 기타피쉬",
                            ],
                        },
                    },
                    "Torpedinidae": {  # 전기가오리과
                        "Torpedo": {
                            "marmorata": [
                                "Marbled electric ray",
                                "마블 일렉트릭 레이",
                            ],
                        },
                    },
                },
            },
            "Osteichthyes": {  # 경골어강
                "Actinopterygii": {  # 조기어강
                    "Acanthuromorpha": {  # 가시기상목
                        "Acanthuriformes": {  # 가시기목
                            "Acanthuridae": {  # 쥐치과 (탱류)
                                "Paracanthurus": {
                                    "hepatus": [
                                        "Blue tang",
                                        "Regal tang",
                                        "Palette surgeonfish",
                                        "Hippo tang",
                                        "Dory fish",
                                        "파란탱",
                                        "리갈탱",
                                    ]
                                },
                                "Zebrasoma": {
                                    "flavescens": [
                                        "Yellow tang",
                                        "Lemon sailfin",
                                        "옐로우탱",
                                        "노란탱",
                                    ],
                                    "xanthurum": [
                                        "Purple tang",
                                        "Yellowtail surgeonfish",
                                        "퍼플탱",
                                        "보라탱",
                                    ],
                                    "veliferum": [
                                        "Sailfin tang",
                                        "Pacific sailfin tang",
                                        "세일핀탱",
                                    ],
                                    "desjardinii": [
                                        "Red Sea sailfin tang",
                                        "Desjardin's sailfin tang",
                                        "데자르딘 세일핀탱",
                                    ],
                                    "scopas": [
                                        "Brown tang",
                                        "Twotone tang",
                                        "브라운탱",
                                    ],
                                    "gemmatum": ["Spotted tang", "스팟티드탱"],
                                    "rostratum": [
                                        "Longnose surgeonfish",
                                        "롱노즈탱",
                                    ],
                                    "xanthurus": [
                                        "Purple tang",
                                        "Yellowtail tang",
                                        "옐로우테일탱",
                                    ],
                                },
                                "Acanthurus": {
                                    "leucosternon": [
                                        "Powder blue tang",
                                        "Powder blue surgeonfish",
                                        "파우더블루탱",
                                    ],
                                    "japonicus": [
                                        "White-faced surgeonfish",
                                        "Gold rim tang",
                                        "골드림탱",
                                    ],
                                    "sohal": [
                                        "Sohal surgeonfish",
                                        "Sohal tang",
                                        "소할탱",
                                    ],
                                    "lineatus": [
                                        "Lined surgeonfish",
                                        "Blue-lined surgeonfish",
                                        "라인드탱",
                                    ],
                                    "achilles": [
                                        "Achilles tang",
                                        "Red-spotted surgeonfish",
                                        "아킬레스탱",
                                    ],
                                    "nigrofuscus": [
                                        "Brown surgeonfish",
                                        "Lavender tang",
                                        "라벤더탱",
                                    ],
                                    "pyroferus": [
                                        "Chocolate surgeonfish",
                                        "초콜릿탱",
                                    ],
                                    "tennentii": [
                                        "Lieutenant tang",
                                        "리우테넌트탱",
                                    ],
                                    "tristis": [
                                        "Indian Ocean mimic surgeonfish",
                                        "인디언오션미믹탱",
                                    ],
                                    "coeruleus": [
                                        "Blue tang surgeonfish",
                                        "블루탱서전피쉬",
                                    ],
                                    "bahianus": [
                                        "Ocean surgeonfish",
                                        "오션서전피쉬",
                                    ],
                                    "chirurgus": ["Doctorfish", "닥터피쉬"],
                                    "olivaceus": [
                                        "Orange-shoulder surgeonfish",
                                        "오렌지숄더탱",
                                    ],
                                    "mata": [
                                        "Elongate surgeonfish",
                                        "일롱게이트탱",
                                    ],
                                    "fowleri": [
                                        "Fowler's surgeonfish",
                                        "파울러탱",
                                    ],
                                    "dussumieri": [
                                        "Eyestripe surgeonfish",
                                        "아이스트라이프탱",
                                    ],
                                    "bariene": [
                                        "Black-spot surgeonfish",
                                        "블랙스팟탱",
                                    ],
                                    "blochii": [
                                        "Ringtail surgeonfish",
                                        "링테일탱",
                                    ],
                                    "chronixis": [
                                        "Chronixis surgeonfish",
                                        "크로닉시스탱",
                                    ],
                                    "guttatus": [
                                        "Whitespotted surgeonfish",
                                        "화이트스팟탱",
                                    ],
                                    "maculiceps": [
                                        "White-freckled surgeonfish",
                                        "화이트프레클드탱",
                                    ],
                                    "nigricans": [
                                        "Whitecheek surgeonfish",
                                        "화이트치크탱",
                                    ],
                                    "nigricauda": [
                                        "Epaulette surgeonfish",
                                        "에폴렛탱",
                                    ],
                                    "nubilus": [
                                        "Bluelined surgeonfish",
                                        "블루라인드탱",
                                    ],
                                    "reversus": [
                                        "Reversed surgeonfish",
                                        "리버스드탱",
                                    ],
                                    "sandvicensis": [
                                        "Thompson's surgeonfish",
                                        "톰슨탱",
                                    ],
                                    "thompsoni": [
                                        "Thompson's surgeonfish",
                                        "톰슨서전피쉬",
                                    ],
                                    "triostegus": [
                                        "Convict surgeonfish",
                                        "컨빅트탱",
                                    ],
                                    "xanthopterus": [
                                        "Yellowfin surgeonfish",
                                        "옐로우핀탱",
                                    ],
                                },
                                "Naso": {
                                    "lituratus": [
                                        "Orangespine unicornfish",
                                        "Naso tang",
                                        "나소탱",
                                    ],
                                    "elegans": [
                                        "Elegant unicornfish",
                                        "엘레간트 유니콘피쉬",
                                    ],
                                    "lopezi": [
                                        "Lopez's unicornfish",
                                        "로페즈 유니콘피쉬",
                                    ],
                                    "vlamingi": [
                                        "Vlaming's unicornfish",
                                        "블라밍기탱",
                                        "블라밍 유니콘피쉬",
                                    ],
                                    "unicornis": [
                                        "Bluespine unicornfish",
                                        "블루스파인 유니콘피쉬",
                                    ],
                                    "brevirostris": [
                                        "Spotted unicornfish",
                                        "스팟티드 유니콘피쉬",
                                    ],
                                    "annulatus": [
                                        "Whitemargin unicornfish",
                                        "화이트마진 유니콘피쉬",
                                    ],
                                    "caesius": [
                                        "Gray unicornfish",
                                        "그레이 유니콘피쉬",
                                    ],
                                    "hexacanthus": [
                                        "Sleek unicornfish",
                                        "슬릭 유니콘피쉬",
                                    ],
                                    "minor": [
                                        "Blackspine unicornfish",
                                        "블랙스파인 유니콘피쉬",
                                    ],
                                    "reticulatus": [
                                        "Reticulated unicornfish",
                                        "레티큘레이티드 유니콘피쉬",
                                    ],
                                    "thynnoides": [
                                        "Oneknife unicornfish",
                                        "원나이프 유니콘피쉬",
                                    ],
                                },
                                "Ctenochaetus": {
                                    "strigosus": [
                                        "Kole tang",
                                        "Yellow-eyed surgeonfish",
                                        "콜탱",
                                    ],
                                    "hawaiiensis": [
                                        "Chevron tang",
                                        "쉐브론탱",
                                    ],
                                    "tominiensis": ["Tomini tang", "토미니탱"],
                                    "binotatus": [
                                        "Two-spot bristletooth",
                                        "투스팟브리슬투스",
                                    ],
                                    "cyanocheilus": [
                                        "Bluelip bristletooth",
                                        "블루립브리슬투스",
                                    ],
                                    "marginatus": [
                                        "Blue-spotted bristletooth",
                                        "블루스팟브리슬투스",
                                    ],
                                    "striatus": [
                                        "Striated surgeonfish",
                                        "스트라이에이티드브리슬투스",
                                    ],
                                    "truncatus": [
                                        "Indian gold-ring bristletooth",
                                        "인디언골드링브리슬투스",
                                    ],
                                    "flavicauda": [
                                        "Yellowtail bristletooth",
                                        "옐로우테일브리슬투스",
                                    ],
                                },
                                "Prionurus": {
                                    "laticlavius": [
                                        "Yellowtail surgeonfish",
                                        "옐로우테일서전피쉬",
                                    ],
                                    "punctatus": [
                                        "Yellowtail surgeonfish",
                                        "옐로우테일서전피쉬",
                                    ],
                                    "scalprum": [
                                        "Scalpel sawtail",
                                        "스칼펠소테일",
                                    ],
                                },
                            },
                            "Siganidae": {  # 래빗피쉬과 (토끼물고기류)
                                "Siganus": {
                                    "vulpinus": [
                                        "Foxface rabbitfish",
                                        "Vulpine rabbitfish",
                                        "복숭아 토끼피쉬",
                                    ],
                                    "unimaculatus": [
                                        "Blotched foxface",
                                        "One-spot foxface",
                                        "블로치드 폭스페이스",
                                    ],
                                    "puellus": [
                                        "Masked rabbitfish",
                                        "Masked spinefoot",
                                        "마스크드 래빗피쉬",
                                    ],
                                    "corallinus": [
                                        "Twospot rabbitfish",
                                        "코랄린러스 래빗피쉬",
                                    ],
                                }
                            },
                            "Pomacanthidae": {  # 엔젤피쉬과
                                "Centropyge": {
                                    "bicolor": [
                                        "Bicolor angelfish",
                                        "Two-colored angelfish",
                                        "바이컬러엔젤",
                                    ],
                                    "loricula": [
                                        "Flame angelfish",
                                        "Flame angel",
                                        "플레임엔젤",
                                        "플레임",
                                    ],
                                    "argi": [
                                        "Cherub angelfish",
                                        "Pygmy angelfish",
                                        "체럽엔젤",
                                    ],
                                    "eibli": [
                                        "Eibli angelfish",
                                        "Red stripe angelfish",
                                        "아이블리엔젤",
                                    ],
                                    "bispinosa": [
                                        "Coral beauty",
                                        "Two-spined angelfish",
                                        "코랄뷰티",
                                        "코랄뷰티엔젤",
                                    ],
                                    "fisheri": [
                                        "Fisher's angelfish",
                                        "피셔엔젤",
                                    ],
                                    "flavissima": [
                                        "Lemonpeel angelfish",
                                        "레몬필엔젤",
                                    ],
                                    "heraldi": [
                                        "Herald's angelfish",
                                        "헤럴드엔젤",
                                    ],
                                    "interruptus": [
                                        "Japanese angelfish",
                                        "재패니즈엔젤",
                                    ],
                                    "multicolor": [
                                        "Multicolor angelfish",
                                        "멀티컬러엔젤",
                                    ],
                                    "nox": ["Midnight angelfish", "미드나잇엔젤"],
                                    "potteri": [
                                        "Potter's angelfish",
                                        "포터엔젤",
                                    ],
                                    "resplendens": [
                                        "Resplendent angelfish",
                                        "레스플렌던트엔젤",
                                    ],
                                    "tibicen": [
                                        "Keyhole angelfish",
                                        "키홀엔젤",
                                    ],
                                    "vrolikii": [
                                        "Pearlscale angelfish",
                                        "Half-black angelfish",
                                        "펄스케일엔젤",
                                        "하프블랙엔젤",
                                    ],
                                    "acanthops": [
                                        "African flameback angelfish",
                                        "아프리칸플레임백엔젤",
                                    ],
                                    "aurantonotus": [
                                        "Flameback angelfish",
                                        "플레임백엔젤",
                                    ],

                                    "colini": [
                                        "Colin's angelfish",
                                        "콜린엔젤",
                                    ],
                                    "debelius": [
                                        "Debelius angelfish",
                                        "데벨리우스엔젤",
                                    ],
                                    "ferrugata": [
                                        "Rusty angelfish",
                                        "러스티엔젤",
                                    ],
                                    "hotumatua": [
                                        "Easter Island angelfish",
                                        "이스터아일랜드엔젤",
                                    ],
                                    "joculator": [
                                        "Yellowface angelfish",
                                        "옐로우페이스엔젤",
                                    ],

                                    "nahackyi": [
                                        "Nahacky's angelfish",
                                        "나하키엔젤",
                                    ],
                                    "narcosis": [
                                        "Narc angelfish",
                                        "나크엔젤",
                                    ],
                                    "shepardi": [
                                        "Shepard's angelfish",
                                        "셰파드엔젤",
                                    ],
                                    "venusta": [
                                        "Purple-masked angelfish",
                                        "퍼플마스크드엔젤",
                                    ],
                                    "boylei": [
                                        "Peppermint angelfish",
                                        "페퍼민트엔젤",
                                    ],
                                    "multibarbus": [
                                        "Multibar angelfish",
                                        "멀티바엔젤",
                                    ],
                                    "multispinis": [
                                        "Dusky angelfish",
                                        "더스키엔젤",
                                    ],
                                    "nigriocellus": [
                                        "Blackspot angelfish",
                                        "블랙스팟엔젤",
                                    ],
                                    "woodheadi": [
                                        "Woodhead's angelfish",
                                        "우드헤드엔젤",
                                    ],
                                    "abei": [
                                        "Abe's angelfish",
                                        "아베엔젤",
                                    ],
                                    "aurantia": [
                                        "Golden angelfish",
                                        "골든엔젤",
                                    ],
                                },
                                "Pomacanthus": {
                                    "imperator": [
                                        "Emperor angelfish",
                                        "Imperial angelfish",
                                        "엠페러엔젤",
                                    ],
                                    "semicirculatus": [
                                        "Koran angelfish",
                                        "Semicircle angelfish",
                                        "코란엔젤",
                                    ],
                                    "navarchus": [
                                        "Blue-girdled angelfish",
                                        "Majestic angelfish",
                                        "마제스틱엔젤",
                                    ],
                                    "annularis": [
                                        "Blue-ring angelfish",
                                        "블루링엔젤",
                                    ],
                                    "asfur": [
                                        "Arabian angelfish",
                                        "아라비안엔젤",
                                    ],
                                    "chrysurus": [
                                        "Goldtail angelfish",
                                        "골드테일엔젤",
                                    ],
                                    "maculosus": [
                                        "Yellowbar angelfish",
                                        "옐로우바엔젤",
                                    ],
                                    "paru": [
                                        "French angelfish",
                                        "프렌치엔젤",
                                    ],
                                    "sexstriatus": [
                                        "Six-banded angelfish",
                                        "식스밴드엔젤",
                                    ],
                                    "xanthometopon": [
                                        "Blueface angelfish",
                                        "블루페이스엔젤",
                                    ],
                                    "zonipectus": [
                                        "Cortez angelfish",
                                        "코테즈엔젤",
                                    ],
                                    "arcuatus": [
                                        "Gray angelfish",
                                        "그레이엔젤",
                                    ],

                                    "altus": [
                                        "Deep angelfish",
                                        "딥엔젤",
                                    ],
                                    "griffithsi": [
                                        "Griffith's angelfish",
                                        "그리피스엔젤",
                                    ],
                                    # rhomboides 항목 중복 제거 (위 정의 삭제)
                                    "griseus": [
                                        "Gray angelfish",
                                        "그레이포마엔젤",
                                    ],
                                    "personifer": [
                                        "Personifer angelfish",
                                        "퍼소나이퍼엔젤",
                                    ],

                                },
                                "Holacanthus": {
                                    "ciliaris": [
                                        "Queen angelfish",
                                        "퀸엔젤",
                                    ],
                                    "tricolor": [
                                        "Rock beauty",
                                        "록뷰티",
                                    ],
                                    "bermudensis": [
                                        "Blue angelfish",
                                        "블루엔젤",
                                    ],
                                    "passer": [
                                        "King angelfish",
                                        "킹엔젤",
                                    ],
                                    "clarionensis": [
                                        "Clarion angelfish",
                                        "클라리온엔젤",
                                    ],
                                    "limbatus": [
                                        "Clipperton angelfish",
                                        "클리퍼톤엔젤",
                                    ],
                                },
                                "Genicanthus": {
                                    "lamarck": [
                                        "Lamarck's angelfish",
                                        "라마크엔젤",
                                    ],
                                    "melanospilos": [
                                        "Blackspot angelfish",
                                        "블랙스팟엔젤",
                                    ],
                                    "semifasciatus": [
                                        "Japanese swallow",
                                        "재패니즈스왈로우",
                                    ],
                                    "watanabei": [
                                        "Watanabe's angelfish",
                                        "와타나베엔젤",
                                    ],
                                    "bellus": [
                                        "Ornate angelfish",
                                        "오네이트엔젤",
                                    ],
                                    "caudovittatus": [
                                        "Zebra angelfish",
                                        "제브라엔젤",
                                    ],
                                    "personatus": [
                                        "Masked angelfish",
                                        "마스크드엔젤",
                                    ],
                                    "takeuchii": [
                                        "Takeuchi's angelfish",
                                        "타케우치엔젤",
                                    ],
                                },
                                "Apolemichthys": {
                                    "trimaculatus": [
                                        "Three-spot angelfish",
                                        "쓰리스팟엔젤",
                                    ],
                                    "xanthotis": [
                                        "Indian yellowtail angelfish",
                                        "인디언옐로우테일엔젤",
                                    ],
                                    "arcuatus": [
                                        "Banded angelfish",
                                        "밴디드엔젤",
                                    ],
                                    "griffisi": [
                                        "Griffis angelfish",
                                        "그리피스엔젤",
                                    ],
                                    "kingi": [
                                        "Tiger angelfish",
                                        "타이거엔젤",
                                    ],
                                    "xanthurus": [
                                        "Indian smoke angelfish",
                                        "인디언스모크엔젤",
                                    ],
                                },
                                "Pygoplites": {
                                    "diacanthus": [
                                        "Regal angelfish",
                                        "Royal angelfish",
                                        "리갈엔젤",
                                    ],
                                },
                                "Chaetodontoplus": {
                                    "septentrionalis": [
                                        "Blue-striped angelfish",
                                        "블루스트라이프엔젤",
                                    ],
                                    "mesoleucus": [
                                        "Vermiculated angelfish",
                                        "버미큘레이티드엔젤",
                                    ],
                                    "melanosoma": [
                                        "Black-velvet angelfish",
                                        "블랙벨벳엔젤",
                                    ],
                                    "duboulayi": [
                                        "Scribbled angelfish",
                                        "스크리블드엔젤",
                                    ],
                                    "chrysocephalus": [
                                        "Orangeface angelfish",
                                        "오렌지페이스엔젤",
                                    ],
                                    "caeruleopunctatus": [
                                        "Blue-spotted angelfish",
                                        "블루스팟엔젤",
                                    ],
                                    "conspicillatus": [
                                        "Conspicuous angelfish",
                                        "컨스피큐어스엔젤",
                                        "컨스피큘러스엔젤",
                                    ],
                                },
                            },
                            "Pomacentridae": {  # 자리돔과
                                "Amphiprioninae": {  # 흰동가리아과 (클라운피쉬)
                                    "Amphiprion": {
                                        "ocellaris": [
                                            "Ocellaris clownfish",
                                            "False percula clownfish",
                                            "Common clownfish",
                                            "오셀라리스",
                                            "니모",
                                        ],
                                        "percula": [
                                            "Orange clownfish",
                                            "Percula clownfish",
                                            "True percula",
                                            "퍼큘라",
                                            "트루퍼큘라",
                                        ],
                                        "clarkii": [
                                            "Clark's anemonefish",
                                            "Yellowtail clownfish",
                                            "클라키",
                                        ],
                                        "frenatus": [
                                            "Tomato clownfish",
                                            "Red clownfish",
                                            "토마토클라운",
                                        ],
                                        "melanopus": [
                                            "Red and black anemonefish",
                                            "Fire clownfish",
                                            "파이어클라운",
                                        ],
                                        "polymnus": [
                                            "Saddleback clownfish",
                                            "White-bonnet anemonefish",
                                            "새들백클라운",
                                        ],
                                        "sebae": ["Sebae clownfish", "세바에클라운"],
                                        "ephippium": [
                                            "Red saddleback anemonefish",
                                            "레드새들백",
                                        ],
                                        "chrysopterus": [
                                            "Orange-fin anemonefish",
                                            "오렌지핀클라운",
                                        ],
                                        "bicinctus": [
                                            "Two-band anemonefish",
                                            "투밴드클라운",
                                        ],
                                        "akallopisos": [
                                            "Skunk clownfish",
                                            "스컹크클라운",
                                        ],
                                        "sandaracinos": [
                                            "Orange skunk clownfish",
                                            "오렌지스컹크클라운",
                                        ],
                                        "nigripes": [
                                            "Maldive anemonefish",
                                            "몰디브클라운",
                                        ],
                                        "allardi": [
                                            "Allard's clownfish",
                                            "알라드클라운",
                                        ],
                                        "chrysogaster": [
                                            "Mauritian anemonefish",
                                            "모리셔스클라운",
                                        ],
                                        "latifasciatus": [
                                            "Wide-band anemonefish",
                                            "와이드밴드클라운",
                                        ],
                                        "leucokranos": [
                                            "White-bonnet anemonefish",
                                            "화이트보넷클라운",
                                        ],
                                        "mccullochi": [
                                            "McCulloch's anemonefish",
                                            "맥컬록클라운",
                                        ],
                                        "omanensis": [
                                            "Oman anemonefish",
                                            "오만클라운",
                                        ],
                                        "pacificus": [
                                            "Pacific anemonefish",
                                            "퍼시픽클라운",
                                        ],
                                        "rubrocinctus": [
                                            "Australian anemonefish",
                                            "오스트레일리안클라운",
                                        ],
                                        "thiellei": [
                                            "Thielle's anemonefish",
                                            "티엘레클라운",
                                        ],
                                        "tricinctus": [
                                            "Three-band anemonefish",
                                            "쓰리밴드클라운",
                                        ],
                                    },
                                    "Premnas": {
                                        "biaculeatus": [
                                            "Maroon clownfish",
                                            "Spine-cheek anemonefish",
                                            "마룬클라운",
                                        ]
                                    },
                                },
                                "Pomacentrinae": {  # 자리돔아과 (댐셀피쉬, 크로미스)
                                    "Chromis": {
                                        "viridis": [
                                            "Blue-green chromis",
                                            "Green chromis",
                                            "그린크로미스",
                                        ],
                                        "cyanea": [
                                            "Blue reef chromis",
                                            "Blue chromis",
                                            "블루크로미스",
                                        ],
                                        "atripectoralis": [
                                            "Black-axil chromis",
                                            "Blackfin chromis",
                                            "블랙핀크로미스",
                                        ],
                                        "vanderbilti": [
                                            "Vanderbilt's chromis",
                                            "반더빌트크로미스",
                                        ],
                                        "margaritifer": [
                                            "Bicolor chromis",
                                            "바이컬러크로미스",
                                        ],
                                        "dimidiata": [
                                            "Half and half chromis",
                                            "하프앤하프크로미스",
                                        ],
                                        "iomelas": [
                                            "Half and half chromis",
                                            "하프앤하프크로미스",
                                        ],
                                        "lepidolepis": [
                                            "Scaly chromis",
                                            "스케일리크로미스",
                                        ],
                                        "retrofasciata": [
                                            "Black-bar chromis",
                                            "블랙바크로미스",
                                        ],
                                        "weberi": [
                                            "Weber's chromis",
                                            "웨버크로미스",
                                        ],
                                    },
                                    "Dascyllus": {
                                        "trimaculatus": [
                                            "Three-spot dascyllus",
                                            "Domino damsel",
                                            "도미노댐셀",
                                        ],
                                        "aruanus": [
                                            "White-tailed dascyllus",
                                            "Humbug dascyllus",
                                            "험버그댐셀",
                                        ],
                                        "melanurus": [
                                            "Four-stripe damselfish",
                                            "Blacktail dascyllus",
                                            "블랙테일댐셀",
                                        ],
                                        "carneus": [
                                            "Cloudy dascyllus",
                                            "클라우디댐셀",
                                        ],
                                        "reticulatus": [
                                            "Reticulate dascyllus",
                                            "레티큘레이트댐셀",
                                        ],
                                    },
                                    "Chrysiptera": {
                                        "cyanea": [
                                            "Blue devil",
                                            "Sapphire devil",
                                            "블루데빌",
                                        ],
                                        "parasema": [
                                            "Yellowtail blue damsel",
                                            "옐로우테일블루댐셀",
                                        ],
                                        "hemicyanea": [
                                            "Azure damselfish",
                                            "애저댐셀",
                                        ],
                                        "springeri": [
                                            "Springer's demoiselle",
                                            "스프링거댐셀",
                                        ],
                                        "talboti": [
                                            "Talbot's demoiselle",
                                            "탈봇댐셀",
                                        ],
                                    },
                                    "Amblyglyphidodon": {
                                        "curacao": [
                                            "Staghorn damselfish",
                                            "스태그혼댐셀",
                                        ],
                                        "leucogaster": [
                                            "Yellowbelly damselfish",
                                            "옐로우벨리댐셀",
                                        ],
                                    },
                                    "Neoglyphidodon": {
                                        "oxyodon": [
                                            "Neon velvet damsel",
                                            "네온벨벳댐셀",
                                        ],
                                        "melas": [
                                            "Bowtie damselfish",
                                            "보우타이댐셀",
                                        ],
                                    },
                                    "Pomacentrus": {
                                        "coelestis": [
                                            "Neon damselfish",
                                            "네온댐셀",
                                        ],
                                        "pavo": [
                                            "Sapphire damsel",
                                            "사파이어댐셀",
                                        ],
                                        "alleni": [
                                            "Andaman damsel",
                                            "안다만댐셀",
                                        ],
                                    },
                                },
                            },
                            "Chaetodontidae": {  # 나비고기과
                                "Chaetodon": {
                                    "auriga": [
                                        "Threadfin butterflyfish",
                                        "Cross-stripe butterfly",
                                        "쓰레드핀버터플라이",
                                    ],
                                    "lunula": [
                                        "Raccoon butterflyfish",
                                        "Crescent-masked butterflyfish",
                                        "라쿤버터플라이",
                                    ],
                                    "vagabundus": [
                                        "Vagabond butterflyfish",
                                        "Crisscross butterflyfish",
                                        "바가본드버터플라이",
                                    ],
                                    "rafflesii": [
                                        "Latticed butterflyfish",
                                        "Raffle's butterflyfish",
                                        "래플스버터플라이",
                                    ],
                                    "collare": [
                                        "Pakistani butterflyfish",
                                        "파키스탄버터플라이",
                                    ],
                                    "fasciatus": [
                                        "Diagonal butterflyfish",
                                        "Pyramid butterflyfish",
                                        "파리미드버터플라이",
                                        "다이아고날버터플라이",
                                    ],
                                    "kleini": [
                                        "Klein's butterflyfish",
                                        "클라인버터플라이",
                                    ],
                                    "melannotus": [
                                        "Blackback butterflyfish",
                                        "블랙백버터플라이",
                                    ],
                                    "miliaris": [
                                        "Lemon butterflyfish",
                                        "레몬버터플라이",
                                    ],
                                    "punctatofasciatus": [
                                        "Spot-band butterflyfish",
                                        "스팟밴드버터플라이",
                                    ],
                                    "semilarvatus": [
                                        "Golden butterflyfish",
                                        "골든버터플라이",
                                    ],
                                    "triangulum": [
                                        "Triangle butterflyfish",
                                        "트라이앵글버터플라이",
                                    ],
                                    "ulietensis": [
                                        "Pacific double-saddle butterflyfish",
                                        "퍼시픽더블새들버터플라이",
                                    ],
                                    "xanthocephalus": [
                                        "Yellowhead butterflyfish",
                                        "옐로우헤드버터플라이",
                                    ],
                                    "baronessa": [
                                        "Eastern triangular butterflyfish",
                                        "바로네사버터플라이",
                                    ],
                                    "burgessi": [
                                        "Burgess' butterflyfish",
                                        "버지스버터플라이",
                                    ],
                                    "citrinellus": [
                                        "Speckled butterflyfish",
                                        "스펙클드버터플라이",
                                    ],
                                    "decussatus": [
                                        "Indian vagabond butterflyfish",
                                        "인디언바가본드버터플라이",
                                    ],
                                    "ephippium": [
                                        "Saddle butterflyfish",
                                        "새들버터플라이",
                                    ],
                                    "falcula": [
                                        "Blackwedged butterflyfish",
                                        "블랙웨지드버터플라이",
                                    ],
                                    "flavirostris": [
                                        "Black butterflyfish",
                                        "블랙버터플라이",
                                    ],
                                    "lineolatus": [
                                        "Lined butterflyfish",
                                        "라인드버터플라이",
                                    ],
                                    "madagaskariensis": [
                                        "Malagasy butterflyfish",
                                        "말라가시버터플라이",
                                    ],
                                    "meyeri": [
                                        "Meyer's butterflyfish",
                                        "마이어버터플라이",
                                    ],
                                    "multicinctus": [
                                        "Multiband butterflyfish",
                                        "멀티밴드버터플라이",
                                    ],
                                    "ornatissimus": [
                                        "Ornate butterflyfish",
                                        "오네이트버터플라이",
                                    ],
                                    "pelewensis": [
                                        "Sunset butterflyfish",
                                        "선셋버터플라이",
                                    ],
                                    "plebeius": [
                                        "Blue-blotch butterflyfish",
                                        "블루블롯치버터플라이",
                                    ],
                                    "reticulatus": [
                                        "Mailed butterflyfish",
                                        "메일드버터플라이",
                                    ],
                                    "speculum": [
                                        "Mirror butterflyfish",
                                        "미러버터플라이",
                                    ],
                                    "tinkeri": [
                                        "Tinker's butterflyfish",
                                        "팅커버터플라이",
                                    ],
                                    "trifascialis": [
                                        "Chevron butterflyfish",
                                        "쉐브론버터플라이",
                                    ],
                                    "trifasciatus": [
                                        "Melon butterflyfish",
                                        "멜론버터플라이",
                                    ],
                                    "unimaculatus": [
                                        "Teardrop butterflyfish",
                                        "티어드롭버터플라이",
                                    ],
                                    "wiebeli": [
                                        "Hong Kong butterflyfish",
                                        "홍콩버터플라이",
                                    ],
                                    "xanthurus": [
                                        "Pearlscale butterflyfish",
                                        "펄스케일버터플라이",
                                    ],
                                    "zanzibarensis": [
                                        "Zanzibar butterflyfish",
                                        "잔지바르버터플라이",
                                    ],
                                    "larvatus": [
                                        "Hooded butterflyfish",
                                        "후드버터플라이",
                                    ],
                                    "paucifasciatus": [
                                        "Red Sea raccoon butterflyfish",
                                        "레드씨라쿤버터플라이",
                                    ],
                                    "pictus": [
                                        "Horseshoe butterflyfish",
                                        "호스슈버터플라이",
                                    ],
                                    "quadrimaculatus": [
                                        "Four-spot butterflyfish",
                                        "포스팟버터플라이",
                                    ],
                                    "rainfordi": [
                                        "Rainford's butterflyfish",
                                        "레인포드버터플라이",
                                    ],
                                    "semeion": [
                                        "Dotted butterflyfish",
                                        "도티드버터플라이",
                                    ],
                                    "smithi": [
                                        "Smith's butterflyfish",
                                        "스미스버터플라이",
                                    ],
                                    "striatus": [
                                        "Banded butterflyfish",
                                        "밴디드버터플라이",
                                    ],
                                    "trichrous": [
                                        "Tahitian butterflyfish",
                                        "타히티안버터플라이",
                                    ],
                                    "fremblii": [
                                        "Bluelashed butterflyfish",
                                        "블루래쉬드버터플라이",
                                    ],
                                    "gardineri": [
                                        "Gardner's butterflyfish",
                                        "가드너버터플라이",
                                    ],
                                    "guttatissimus": [
                                        "Peppered butterflyfish",
                                        "페퍼드버터플라이",
                                    ],
                                    "hoefleri": [
                                        "Four-banded butterflyfish",
                                        "포밴드버터플라이",
                                    ],
                                    "interruptus": [
                                        "Yellow butterflyfish",
                                        "옐로우버터플라이",
                                    ],
                                    "litus": [
                                        "Speckled butterflyfish",
                                        "스펙클드버터플라이",
                                    ],
                                    "marleyi": [
                                        "Marley's butterflyfish",
                                        "말리버터플라이",
                                    ],
                                    "nigropunctatus": [
                                        "Black-spotted butterflyfish",
                                        "블랙스팟버터플라이",
                                    ],
                                    "declivis": [
                                        "Marquesas butterflyfish",
                                        "데클라비스버터플라이",
                                        "마르케사스버터플라이",
                                    ],
                                    "argentatus": [
                                        "Asian butterflyfish",
                                        "아시안버터플라이",
                                    ],
                                    "aureofasciatus": [
                                        "Golden butterflyfish",
                                        "골든버터플라이",
                                    ],
                                    "bennetti": [
                                        "Bennett's butterflyfish",
                                        "베넷버터플라이",
                                    ],
                                    "capistratus": [
                                        "Foureye butterflyfish",
                                        "포아이버터플라이",
                                    ],
                                    "daedalma": [
                                        "Wrought iron butterflyfish",
                                        "로트아이언버터플라이",
                                    ],
                                    "flavocoronatus": [
                                        "Yellow-crowned butterflyfish",
                                        "옐로우크라운드버터플라이",
                                    ],
                                    "guentheri": [
                                        "Gunther's butterflyfish",
                                        "군터버터플라이",
                                    ],
                                    "hemichrysus": [
                                        "Threeband butterflyfish",
                                        "쓰리밴드버터플라이",
                                    ],
                                    "humeralis": [
                                        "Three-banded butterflyfish",
                                        "쓰리밴디드버터플라이",
                                    ],
                                    "jayakari": [
                                        "Jayakar's butterflyfish",
                                        "자야카르버터플라이",
                                    ],
                                    "leucopleura": [
                                        "Somali butterflyfish",
                                        "소말리버터플라이",
                                    ],
                                    "lunulatus": [
                                        "Oval butterflyfish",
                                        "오발버터플라이",
                                    ],
                                    "melapterus": [
                                        "Arabian butterflyfish",
                                        "아라비안버터플라이",
                                    ],
                                    "mitratus": [
                                        "Indian butterflyfish",
                                        "인디언버터플라이",
                                    ],
                                    "nippon": [
                                        "Japanese butterflyfish",
                                        "재패니즈버터플라이",
                                    ],
                                    "ocellicaudus": [
                                        "Spot-tail butterflyfish",
                                        "스팟테일버터플라이",
                                    ],
                                    "octofasciatus": [
                                        "Eightband butterflyfish",
                                        "에잇밴드버터플라이",
                                    ],
                                    "oxycephalus": [
                                        "Spot-nape butterflyfish",
                                        "스팟네이프버터플라이",
                                    ],
                                },
                                "Parachaetodon": {
                                    "ocellatus": [
                                        "Sixspine butterflyfish",
                                        "식스스파인버터플라이",
                                    ],
                                },
                                "Prognathodes": {
                                    "aculeatus": [
                                        "Longsnout butterflyfish",
                                        "롱스나웃버터플라이",
                                    ],
                                    "basabei": [
                                        "Basabe's butterflyfish",
                                        "바사베버터플라이",
                                    ],
                                    "dichrous": [
                                        "Bicolor butterflyfish",
                                        "바이컬러버터플라이",
                                    ],
                                    "falcifer": [
                                        "Scythe butterflyfish",
                                        "사이드버터플라이",
                                    ],
                                    "guyanensis": [
                                        "French butterflyfish",
                                        "프렌치버터플라이",
                                    ],
                                },
                                "Heniochus": {
                                    "acuminatus": [
                                        "Pennant coralfish",
                                        "Longfin bannerfish",
                                        "페넌트코랄피쉬",
                                    ],
                                    "diphreutes": [
                                        "Schooling bannerfish",
                                        "False moorish idol",
                                        "스쿨링배너피쉬",
                                    ],
                                    "intermedius": [
                                        "Red Sea bannerfish",
                                        "레드씨배너피쉬",
                                    ],
                                    "singularius": [
                                        "Singular bannerfish",
                                        "싱귤러배너피쉬",
                                    ],
                                    "varius": [
                                        "Horned bannerfish",
                                        "혼드배너피쉬",
                                    ],
                                },
                                "Hemitaurichthys": {
                                    "polylepis": [
                                        "Pyramid butterflyfish",
                                        "피라미드버터플라이",
                                    ],
                                    "zoster": [
                                        "Brown-and-white butterflyfish",
                                        "브라운앤화이트버터플라이",
                                    ],
                                },
                                "Forcipiger": {
                                    "flavissimus": [
                                        "Yellow longnose butterflyfish",
                                        "Forceps fish",
                                        "옐로우롱노즈",
                                    ],
                                    "longirostris": [
                                        "Longnose butterflyfish",
                                        "Big longnose butterflyfish",
                                        "빅롱노즈",
                                    ],
                                },
                                "Chelmon": {
                                    "rostratus": [
                                        "Copperband butterflyfish",
                                        "Beaked coralfish",
                                        "코퍼밴드버터플라이",
                                    ]
                                },
                            },
                            "Labridae": {  # 놀래기과 (Wrasse)
                                "Labroides": {
                                    "dimidiatus": [
                                        "Bluestreak cleaner wrasse",
                                        "블루스트릭클리너",
                                    ],
                                    "bicolor": [
                                        "Bicolor cleaner wrasse",
                                        "바이컬러클리너",
                                    ],
                                    "pectoralis": [
                                        "Blackspot cleaner wrasse",
                                        "블랙스팟클리너",
                                    ],
                                    "phthirophagus": [
                                        "Hawaiian cleaner wrasse",
                                        "하와이안클리너",
                                    ],
                                    # 자주 수입되는 추가 클리너랩스 (필요 시 확장 가능)
                                    # "terralabroides": [
                                    #     "Red Sea cleaner wrasse",
                                    #     "레드씨클리너",
                                    # ],  # 확인 후 활성화
                                },
                                "Thalassoma": {
                                    "bifasciatum": [
                                        "Bluehead wrasse",
                                        "블루헤드놀래기",
                                    ],
                                    "lunare": [
                                        "Moon wrasse",
                                        "Green moon wrasse",
                                        "문놀래기",
                                    ],
                                    "lutescens": [
                                        "Sunset wrasse",
                                        "선셋놀래기",
                                    ],
                                    "hardwicke": [
                                        "Hardwick's wrasse",
                                        "하드윅놀래기",
                                    ],
                                    "klunzingeri": [
                                        "Klunzinger's wrasse",
                                        "클룬징거놀래기",
                                    ],
                                    "quinquevittatum": [
                                        "Five-stripe wrasse",
                                        "파이브스트라이프놀래기",
                                    ],
                                    # 추가로 수입되는 종류
                                    "purpureum": [
                                        "Surge wrasse",
                                        "서지놀래기",
                                    ],
                                    "rueppellii": [
                                        "Red Sea wrasse",
                                        "레드씨놀래기",
                                    ],
                                },
                                "Pseudocheilinus": {
                                    "hexataenia": [
                                        "Six-line wrasse",
                                        "식스라인놀래기",
                                    ],
                                    "tetrataenia": [
                                        "Four-line wrasse",
                                        "포라인놀래기",
                                    ],
                                    "evanidus": [
                                        "Striated wrasse",
                                        "스트라이에이티드놀래기",
                                    ],
                                    "ocellatus": [
                                        "Mystery wrasse",
                                        "미스터리놀래기",
                                    ],
                                    "dispar": [
                                        "Dispar wrasse",
                                        "디스파놀래기",
                                    ],
                                },
                                "Cirrhilabrus": {
                                    "cyanopleura": [
                                        "Blueside fairy wrasse",
                                        "블루사이드페어리",
                                    ],
                                    "scottorum": [
                                        "Scott's fairy wrasse",
                                        "스콧페어리",
                                    ],
                                    "exquisitus": [
                                        "Exquisite fairy wrasse",
                                        "엑스퀴지트페어리",
                                    ],
                                    "lineatus": [
                                        "Lined fairy wrasse",
                                        "라인드페어리",
                                    ],
                                    "lubbocki": [
                                        "Lubbock's fairy wrasse",
                                        "루복페어리",
                                    ],
                                    "rubriventralis": [
                                        "Social fairy wrasse",
                                        "소셜페어리",
                                    ],
                                    "rubeus": [
                                        "Red velvet fairy wrasse",
                                        "Ruby fairy wrasse",
                                        "레드벨벳페어리",
                                        "루비페어리",
                                    ],
                                    "lanceolatus": [
                                        "Lanceolate fairy wrasse",
                                        "랜스올레이트페어리",
                                    ],
                                    "solorensis": [
                                        "Red-headed fairy wrasse",
                                        "레드헤드페어리",
                                    ],
                                    "jordani": [
                                        "Jordan's fairy wrasse",
                                        "조던페어리",
                                    ],
                                    "temminckii": [
                                        "Temminck's fairy wrasse",
                                        "템민크페어리",
                                    ],
                                    "punctatus": [
                                        "Fine-spotted fairy wrasse",
                                        "파인스팟페어리",
                                    ],
                                    "rhomboidalis": [
                                        "Rhomboid fairy wrasse",
                                        "롬보이드페어리",
                                    ],
                                    "katherinae": [
                                        "Katherine's fairy wrasse",
                                        "캐서린페어리",
                                    ],
                                    # 추가 인기 페어리 래스
                                    "naokoae": [
                                        "Naoko's fairy wrasse",
                                        "나오코페어리",
                                    ],
                                    "rubrisquamis": [
                                        "Red velvet scaled fairy wrasse",
                                        "레드벨벳스케일드페어리",
                                    ],
                                    "condei": [
                                        "Conde's fairy wrasse",
                                        "콘데이페어리",
                                    ],
                                    "finifenmaa": [
                                        "Rose-veiled fairy wrasse",
                                        "로즈베일드페어리",
                                    ],
                                },
                                "Paracheilinus": {
                                    "carpenteri": [
                                        "Carpenter's flasher wrasse",
                                        "카펜터플래셔",
                                    ],
                                    "filamentosus": [
                                        "Filament flasher wrasse",
                                        "필라멘트플래셔",
                                    ],
                                    "mccoskeri": [
                                        "McCosker's flasher wrasse",
                                        "맥코스커플래셔",
                                    ],
                                    "angulatus": [
                                        "Angular flasher wrasse",
                                        "앵귤러플래셔",
                                    ],
                                    "attenuatus": [
                                        "Attenuate flasher wrasse",
                                        "어테뉴에이트플래셔",
                                    ],
                                    "octotaenia": [
                                        "Eight-line flasher wrasse",
                                        "에잇라인플래셔",
                                    ],
                                    # 추가 플래셔 래스
                                    "flavianalis": [
                                        "Yellowfin flasher wrasse",
                                        "옐로우핀플래셔",
                                    ],
                                    "lineopunctatus": [
                                        "Linespot flasher wrasse",
                                        "라인스팟플래셔",
                                    ],
                                    "rubricaudalis": [
                                        "Red-tailed flasher wrasse",
                                        "레드테일플래셔",
                                    ],
                                    "cyaneus": [
                                        "Blue flasher wrasse",
                                        "블루플래셔",
                                    ],
                                },
                                "Halichoeres": {
                                    "chrysus": [
                                        "Canary wrasse",
                                        "카나리놀래기",
                                    ],
                                    "marginatus": [
                                        "Dusky wrasse",
                                        "더스키놀래기",
                                    ],
                                    "melanurus": [
                                        "Hoeven's wrasse",
                                        "호벤놀래기",
                                    ],
                                    "ornatissimus": [
                                        "Ornate wrasse",
                                        "오네이트놀래기",
                                    ],
                                    "iridis": [
                                        "Radiant wrasse",
                                        "래디언트놀래기",
                                    ],
                                    "leucoxanthus": [
                                        "Canarytop wrasse",
                                        "카나리탑놀래기",
                                    ],
                                    "trispilus": [
                                        "Three-spot wrasse",
                                        "쓰리스팟놀래기",
                                    ],
                                    # 추가로 자주 유통되는 할리코에레스
                                    "hortulanus": [
                                        "Checkerboard wrasse",
                                        "체커보드놀래기",
                                    ],
                                    "biocellatus": [
                                        "Red-lined wrasse",
                                        "레드라인드놀래기",
                                    ],
                                    "cosmetus": [
                                        "Adorned wrasse",
                                        "어도른드놀래기",
                                    ],
                                },
                                "Coris": {
                                    "gaimard": [
                                        "Yellowtail coris",
                                        "옐로우테일코리스",
                                    ],
                                    "formosa": [
                                        "Formosa coris",
                                        "포모사코리스",
                                    ],
                                    "aygula": [
                                        "Clown coris",
                                        "클라운코리스",
                                    ],
                                    "julis": [
                                        "Mediterranean rainbow wrasse",
                                        "메디터레니안레인보우",
                                    ],
                                    # 추가 Coris 속
                                    "picta": [
                                        "African coris",
                                        "아프리칸코리스",
                                    ],
                                    "vexillifer": [
                                        "Bicolor coris",
                                        "바이컬러코리스",
                                    ],
                                },
                                "Novaculichthys": {
                                    "taeniourus": [
                                        "Rockmover wrasse",
                                        "Dragon wrasse",
                                        "드래곤놀래기",
                                    ],
                                },
                                "Pseudojuloides": {
                                    # Cirrhilabrus naokoae 가 올바른 분류
                                    # Pseudojuloides 속에 naokoae 없음. (중복/오류 제거)
                                    "severnsi": [
                                        "Severn's wrasse",
                                        "서번스놀래기",
                                    ],
                                },
                                # Macropharyngodon 중복 블록 통합 및 확장
                                "Macropharyngodon": {
                                    "meleagris": [
                                        "Leopard wrasse",
                                        "레오파드놀래기",
                                    ],
                                    "bipartitus": [
                                        "Divided wrasse",
                                        "디바이디드놀래기",
                                    ],
                                    "ornatus": [
                                        "Ornate leopard wrasse",
                                        "오네이트레오파드놀래기",
                                    ],
                                    "negrosensis": [
                                        "Yellow-spotted leopard wrasse",
                                        "옐로우스팟레오파드놀래기",
                                    ],
                                    "choati": [
                                        "Choat's leopard wrasse",
                                        "초아티레오파드놀래기",
                                    ],
                                    "kuiteri": [
                                        "Kuiter's leopard wrasse",
                                        "쿠이테리레오파드놀래기",
                                    ],
                                },
                                "Cirrihilabrus": {
                                    "solorensis": [
                                        "Red head solon fairy wrasse",
                                        "솔론페어리",
                                    ],
                                    "cyanopleura": [
                                        "Blue-sided fairy wrasse",
                                        "블루사이드페어리",
                                    ],
                                    "lineatus": [
                                        "Lineatus fairy wrasse",
                                        "리네이투스페어리",
                                    ],
                                    "lubbocki": [
                                        "Lubbock's fairy wrasse",
                                        "러벅페어리",
                                    ],
                                    "exquisitus": [
                                        "Exquisite fairy wrasse",
                                        "엑스퀴짓페어리",
                                    ],
                                    "jordani": [
                                        "Flame fairy wrasse",
                                        "플레임페어리",
                                    ],
                                    "lunatus": [
                                        "Lunate fairy wrasse",
                                        "루네이트페어리",
                                    ],
                                    "rubrofuscus": [
                                        "Ruby-head fairy wrasse",
                                        "루비헤드페어리",
                                    ],
                                    "naokoae": [
                                        "Naoko fairy wrasse",
                                        "나오코페어리",
                                    ],
                                    "rubrimarginatus": [
                                        "Red margin fairy wrasse",
                                        "레드마진페어리",
                                    ],
                                },
                                "Bodianus": {
                                    "rufus": [
                                        "Spanish hogfish",
                                        "스패니쉬호그피쉬",
                                    ],
                                    "diana": [
                                        "Diana's hogfish",
                                        "다이아나호그피쉬",
                                    ],
                                    "anthioides": [
                                        "Lyretail hogfish",
                                        "라이어테일호그피쉬",
                                    ],
                                    "axillaris": [
                                        "Coral hogfish",
                                        "코랄호그피쉬",
                                    ],
                                    # 추가 호그피쉬
                                    "mesothorax": [
                                        "Split-level hogfish",
                                        "스플릿레벨호그피쉬",
                                    ],
                                    "bimaculatus": [
                                        "Twinspot hogfish",
                                        "트윈스팟호그피쉬",
                                    ],
                                    "sepiacaudus": [
                                        "Candy cane hogfish",
                                        "캔디케인호그피쉬",
                                    ],
                                },
                                "Anampses": {
                                    "meleagrides": [
                                        "Spotted wrasse",
                                        "스팟티드놀래기",
                                    ],
                                    "chrysocephalus": [
                                        "Psychedelic wrasse",
                                        "사이키델릭놀래기",
                                    ],
                                    # 추가 타마린 래스
                                    "femininus": [
                                        "Blue-stripe tamarin wrasse",
                                        "블루스트라이프타마린",
                                    ],
                                    "lennardi": [
                                        "Lennard's wrasse",
                                        "레나드놀래기",
                                    ],
                                },
                                "Stethojulis": {
                                    "bandanensis": [
                                        "Red shoulder wrasse",
                                        "레드숄더놀래기",
                                    ],
                                    "strigiventer": [
                                        "Three-ribbon wrasse",
                                        "쓰리리본놀래기",
                                    ],
                                    # 필요시 추가 가능
                                },
                            },
                            "Apogonidae": {  # 천축어과 (카디널피쉬)
                                "Sphaeramia": {
                                    "nematoptera": [
                                        "Pajama cardinalfish",
                                        "파자마카디널",
                                    ],
                                    "orbicularis": [
                                        "Orbiculate cardinalfish",
                                        "오비큘레이트카디널",
                                    ],
                                },
                                "Pterapogon": {
                                    "kauderni": [
                                        "Banggai cardinalfish",
                                        "방가이카디널",
                                    ]
                                },
                                # 재분류 참고: 과거 다수 종이
                                # Ostorhinchus / Zoramia / Taeniamia 로 이동
                                # Apogon 는 유통상 Flamefish (A. maculatus) 위주
                                "Apogon": {
                                    "maculatus": [
                                        "Flamefish",
                                        "플레임피쉬",
                                    ],
                                },
                                "Cheilodipterus": {
                                    "macrodon": [
                                        "Large-toothed cardinalfish",
                                        "라지투스카디널",
                                    ],
                                    "quinquelineatus": [
                                        "Five-lined cardinalfish",
                                        "파이브라인드카디널",
                                    ],
                                    "artus": [
                                        "Wolf cardinalfish",
                                        "울프카디널",
                                    ],
                                    "intermedius": [
                                        "Intermediate cardinalfish",
                                        "인터미디어트카디널",
                                    ],
                                },
                                "Ostorhinchus": {
                                    "angustatus": [
                                        "Broad-striped cardinalfish",
                                        "브로드스트라이프카디널",
                                    ],
                                    "aureus": [
                                        "Ring-tailed cardinalfish",
                                        "링테일카디널",
                                    ],
                                    "capricornis": [
                                        "Capricorn cardinalfish",
                                        "카프리콘카디널",
                                    ],
                                    "chrysopomus": [
                                        "Yellow-fin cardinalfish",
                                        "옐로우핀카디널",
                                    ],
                                    "cyanosoma": [
                                        "Yellow-striped cardinalfish",
                                        "옐로우스트라이프카디널",
                                    ],
                                    "doederleini": [
                                        "Doederlein's cardinalfish",
                                        "되덜라인카디널",
                                    ],
                                    "compressus": [
                                        "Ochre-striped cardinalfish",
                                        "오커스트라이프카디널",
                                    ],
                                    "cookii": [
                                        "Cook's cardinalfish",
                                        "쿡카디널",
                                    ],
                                    "exostigma": [
                                        "Narrowstripe cardinalfish",
                                        "내로우스트라이프카디널",
                                    ],
                                    "hartzfeldii": [
                                        "Hartzfeld's cardinalfish",
                                        "하츠펠드카디널",
                                    ],
                                    "parvulus": [
                                        "Redspot cardinalfish",
                                        "레드스팟카디널",
                                    ],
                                    "apogonoides": [
                                        "Short-tooth cardinal",
                                        "쇼트투스카디널",
                                    ],
                                    "fleurieu": [
                                        "Cardinalfish",
                                        "카디널피쉬",
                                    ],
                                    "hoevenii": [
                                        "Frosted cardinalfish",
                                        "프로스티드카디널",
                                    ],
                                },
                                "Zoramia": {
                                    "leptacantha": [
                                        "Threadfin cardinalfish",
                                        "쓰레드핀카디널",
                                    ],
                                    "fragilis": [
                                        "Fragile cardinalfish",
                                        "프래질카디널",
                                    ],
                                },
                                "Taeniamia": {
                                    "zosterophora": [
                                        "Zoster cardinalfish",
                                        "조스터카디널",
                                    ],
                                },
                                "Rhabdamia": {
                                    "gracilis": [
                                        "Longspine cardinalfish",
                                        "롱스파인카디널",
                                    ],
                                },
                                "Pristiapogon": {
                                    "fraenatus": [
                                        "Bridled cardinalfish",
                                        "브라이들드카디널",
                                    ],
                                },
                                # 선택적(드물게 유통) - 필요 시 주석 해제
                                # "Apogonichthyoides": {
                                #     "melas": [
                                #         "Black cardinalfish",
                                #         "블랙카디널",
                                #     ],
                                # },
                            },
                        },
                        "Blenniiformes": {  # 블레니목
                            "Blenniidae": {  # 블레니과
                                "Meiacanthus": {
                                    "grammistes": [
                                        "Striped poison-fang blenny",
                                        "스트라이프드포이즌블레니",
                                    ],
                                    "smithi": [
                                        "Smith's fang blenny",
                                        "스미스팽블레니",
                                    ],
                                    "atrodorsalis": [
                                        "Forktail blenny",
                                        "포크테일블레니",
                                    ],
                                    "bundoon": [
                                        "Bundoon blenny",
                                        "분둔블레니",
                                    ],
                                    "ditrema": [
                                        "One-stripe poison-fang blenny",
                                        "원스트라이프포이즌블레니",
                                    ],
                                    "kamoharai": [
                                        "Kamohara blenny",
                                        "카모하라블레니",
                                    ],
                                    "lineatus": [
                                        "Lined fangblenny",
                                        "라인드팽블레니",
                                    ],
                                    "luteus": [
                                        "Yellow poison-fang blenny",
                                        "옐로우포이즌블레니",
                                    ],
                                    "nigrolineatus": [
                                        "Blackline fangblenny",
                                        "블랙라인팽블레니",
                                    ],
                                    "oualanensis": [
                                        "Oualan fangblenny",
                                        "오우알란팽블레니",
                                    ],
                                },
                                "Ecsenius": {
                                    "bicolor": [
                                        "Bicolor blenny",
                                        "바이컬러블레니",
                                    ],
                                    "midas": [
                                        "Midas blenny",
                                        "미다스블레니",
                                    ],
                                    "axelrodi": [
                                        "Axelrod's combtooth blenny",
                                        "액셀로드블레니",
                                    ],
                                    "bandanus": [
                                        "Banda combtooth blenny",
                                        "반다블레니",
                                    ],
                                    "bathi": [
                                        "Bath's combtooth blenny",
                                        "바스블레니",
                                    ],
                                    "dentex": [
                                        "Fiji combtooth blenny",
                                        "피지블레니",
                                    ],
                                    "frontalis": [
                                        "Smooth-fin blenny",
                                        "스무스핀블레니",
                                    ],
                                    "gravieri": [
                                        "Red Sea mimic blenny",
                                        "레드씨미믹블레니",
                                    ],
                                    "lineatus": [
                                        "Linear blenny",
                                        "리니어블레니",
                                    ],
                                    "mandibularis": [
                                        "Queensland blenny",
                                        "퀸즐랜드블레니",
                                    ],
                                    "namiyei": [
                                        "Black comb-tooth",
                                        "블랙콤투스",
                                    ],
                                    "pictus": [
                                        "White-lined comb-tooth",
                                        "화이트라인드콤투스",
                                    ],
                                    "stigmatura": [
                                        "Tail-spot combtooth blenny",
                                        "테일스팟블레니",
                                    ],
                                    # 추가 자주 유통
                                    "springeri": [
                                        "Springer's combtooth blenny",
                                        "스프링거블레니",
                                    ],
                                    "tricolor": [
                                        "Tricolor blenny",
                                        "트라이컬러블레니",
                                    ],
                                    "prosopotaenia": [
                                        "Banded blenny",
                                        "밴디드블레니",
                                    ],
                                },
                                "Salarias": {
                                    "fasciatus": [
                                        "Jewelled blenny",
                                        "Lawnmower blenny",
                                        "론모어블레니",
                                    ],
                                    "guttatus": [
                                        "Breast-spot blenny",
                                        "브레스트스팟블레니",
                                    ],
                                    "patzneri": [
                                        "Patzner's blenny",
                                        "패츠너블레니",
                                    ],
                                    "ramosus": [
                                        "Starry blenny",
                                        "스타리블레니",
                                    ],
                                    "segmentatus": [
                                        "Segmented blenny",
                                        "세그먼티드블레니",
                                    ],
                                },
                                "Atrosalarias": {
                                    "fuscus": [
                                        "Brown coral blenny",
                                        "브라운코랄블레니",
                                    ],
                                    # Added
                                    "holomelas": [
                                        "Black blenny",
                                        "블랙블레니",
                                    ],
                                },
                                "Blenniella": {
                                    "bilitonensis": [
                                        "Billiton combtooth blenny",
                                        "빌리톤블레니",
                                    ],
                                    "chrysospilos": [
                                        "Red-spotted blenny",
                                        "레드스팟블레니",
                                    ],
                                    "cyanostigma": [
                                        "Bluespotted blenny",
                                        "블루스팟블레니",
                                    ],
                                    "gibbifrons": [
                                        "Hump-head blenny",
                                        "험프헤드블레니",
                                    ],
                                },
                                "Cirripectes": {
                                    "castaneus": [
                                        "Chestnut eyelash-blenny",
                                        "체스넛아이래쉬블레니",
                                    ],
                                    "filamentosus": [
                                        "Filamentous blenny",
                                        "필라멘토스블레니",
                                    ],
                                    "fuscoguttatus": [
                                        "Spotted eyelash blenny",
                                        "스팟티드아이래쉬블레니",
                                    ],
                                    "polyzona": [
                                        "Barred blenny",
                                        "바드블레니",
                                    ],
                                    "springeri": [
                                        "Springer's blenny",
                                        "스프링거블레니",
                                    ],
                                    "stigmaticus": [
                                        "Red-streaked blenny",
                                        "레드스트릭드블레니",
                                    ],
                                    "variolosus": [
                                        "Red-speckled blenny",
                                        "레드스펙클드블레니",
                                    ],
                                },
                                # 산호 식해 위험, 주의 필요
                                "Exallias": {
                                    "brevis": [
                                        "Leopard blenny",
                                        "레오파드블레니",
                                    ]
                                },
                                # 모방/물기 이슈, 주의
                                "Plagiotremus": {
                                    "rhinorhynchos": [
                                        "Bluestriped fangblenny",
                                        "블루스트라이프팽블레니",
                                    ]
                                },
                            },
                            "Chaenopsidae": {  # 파이크블레니과
                                "Acanthemblemaria": {
                                    "maria": [
                                        "Secretary blenny",
                                        "세크레터리블레니",
                                    ],
                                    "spinosa": [
                                        "Spinyhead blenny",
                                        "스파이니헤드블레니",
                                    ],
                                }
                            },
                            "Clinidae": {  # 클라이니드과
                                "Labrisomus": {
                                    "nuchipinnis": [
                                        "Hairy blenny",
                                        "헤어리블레니",
                                    ]
                                }
                            },
                        },
                        "Ephippiformes": {  # 뱃피쉬목
                            "Ephippidae": {  # 뱃피쉬과
                                "Platax": {
                                    "orbicularis": [
                                        "Orbicular batfish",
                                        "Circular batfish",
                                        "오비큘러뱃피쉬",
                                    ],
                                    "teira": [
                                        "Longfin batfish",
                                        "Teira batfish",
                                        "롱핀뱃피쉬",
                                    ],
                                    "pinnatus": [
                                        "Pinnate batfish",
                                        "Dusky batfish",
                                        "피네이트뱃피쉬",
                                    ],
                                    "batavianus": [
                                        "Batavia batfish",
                                        "바타비아뱃피쉬",
                                    ],
                                    "boersii": [
                                        "Golden spadefish",
                                        "Boers' batfish",
                                        "골든스페이드피쉬",
                                    ],
                                },
                                "Zabidius": {
                                    "novemaculeatus": [
                                        "Nine-spotted batfish",
                                        "나인스팟뱃피쉬",
                                    ]
                                },
                            },
                            "Drepaneidae": {  # 초승달고기과
                                "Drepane": {
                                    "punctata": [
                                        "Spotted sicklefish",
                                        "스팟티드시클피쉬",
                                    ]
                                }
                            },
                        },
                        "Zancliformes": {  # 무어리쉬아이돌목
                            "Zanclidae": {  # 무어리쉬아이돌과
                                "Zanclus": {
                                    "cornutus": [
                                        "Moorish idol",
                                        "무어리쉬아이돌",
                                        "모리셔스우상",
                                    ]
                                }
                            }
                        },
                    },
                    "Tetraodontomorpha": {  # 복어상목
                        "Tetraodontiformes": {  # 복어목
                            "Tetraodontidae": {  # 복어과
                                "Arothron": {
                                    "nigropunctatus": [
                                        "Blackspotted puffer",
                                        "Dog-faced puffer",
                                        "도그페이스퍼퍼",
                                    ],
                                    "meleagris": [
                                        "Guineafowl puffer",
                                        "Golden puffer",
                                        "기니파울퍼퍼",
                                    ],
                                    "hispidus": [
                                        "White-spotted puffer",
                                        "화이트스팟퍼퍼",
                                    ],
                                    "mappa": [
                                        "Map puffer",
                                        "맵퍼퍼",
                                    ],
                                    "stellatus": [
                                        "Starry puffer",
                                        "스타리퍼퍼",
                                        # Takifugu niphobles 도 같은 통칭 사용 → 주의
                                    ],
                                    "reticularis": [
                                        "Reticulated puffer",
                                        "레티큘레이티드퍼퍼",
                                    ],
                                    "manilensis": [
                                        "Narrow-lined puffer",
                                        "내로우라인드퍼퍼",
                                    ],
                                },
                                "Canthigaster": {
                                    "valentini": [
                                        "Valentini puffer",
                                        "Black-saddled toby",
                                        "발렌티니퍼퍼",
                                    ],
                                    "solandri": [
                                        "Spotted sharpnose puffer",
                                        "Blue-spotted puffer",
                                        "블루스팟퍼퍼",
                                    ],
                                    "coronata": [
                                        "Crowned puffer",
                                        "크라운드퍼퍼",
                                    ],
                                    "janthinoptera": [
                                        "Honeycomb toby",
                                        "허니콤토비",
                                    ],
                                    "margaritata": [
                                        "Pearl toby",
                                        "펄토비",
                                    ],
                                    "rostrata": [
                                        "Caribbean sharpnose-puffer",
                                        "카리비안샤프노즈퍼퍼",
                                    ],
                                    # 자주 유통 추가
                                    "amboinensis": [
                                        "Ambon toby",
                                        "암본토비",
                                    ],
                                    "epilampra": [
                                        "Lantern toby",
                                        "랜턴토비",
                                    ],
                                },
                                "Takifugu": {
                                    "niphobles": [
                                        "Starry puffer",
                                        "스타리퍼퍼",
                                        # Arothron stellatus 와 공명
                                    ]
                                },
                            },
                            "Balistidae": {  # 쥐치과 (트리거피쉬)
                                "Rhinecanthus": {
                                    "aculeatus": [
                                        "Lagoon triggerfish",
                                        "Blackbar triggerfish",
                                        "라군트리거",
                                    ],
                                    "rectangulus": [
                                        "Wedgetail triggerfish",
                                        "Rectangle triggerfish",
                                        "웨지테일트리거",
                                    ],
                                    "assasi": [
                                        "Picasso triggerfish",
                                        "피카소트리거",
                                    ],
                                },
                                "Balistoides": {
                                    "conspicillum": [
                                        "Clown triggerfish",
                                        "Big-spotted triggerfish",
                                        "클라운트리거",
                                    ],
                                    "viridescens": [
                                        "Titan triggerfish",
                                        "타이탄트리거",
                                    ],
                                },
                                "Balistes": {
                                    "vetula": [
                                        "Queen triggerfish",
                                        "퀸트리거",
                                    ]
                                },
                                "Odonus": {
                                    "niger": [
                                        "Red-toothed triggerfish",
                                        "레드투스트리거",
                                    ]
                                },
                                "Sufflamen": {
                                    "bursa": [
                                        "Scythe triggerfish",
                                        "사이드트리거",
                                    ],
                                    "chrysopterum": [
                                        "Halfmoon triggerfish",
                                        "하프문트리거",
                                    ],
                                },
                                "Xanthichthys": {
                                    "auromarginatus": [
                                        "Gilded triggerfish",
                                        "길디드트리거",
                                    ],
                                    "mento": [
                                        "Redtail triggerfish",
                                        "레드테일트리거",
                                    ],
                                    "ringens": [
                                        "Sargassum triggerfish",
                                        "사가섬트리거",
                                    ],
                                },
                                "Pseudobalistes": {
                                    "fuscus": [
                                        "Blue triggerfish",
                                        "Blueface triggerfish",
                                        "블루페이스트리거",
                                    ],
                                    "flavimarginatus": [
                                        "Yellowmargin triggerfish",
                                        "옐로우마진트리거",
                                    ],
                                },
                                "Melichthys": {
                                    "niger": [
                                        "Black triggerfish",
                                        "블랙트리거",
                                    ],
                                    "vidua": [
                                        "Pinktail triggerfish",
                                        "핑크테일트리거",
                                    ],
                                },
                                "Abalistes": {
                                    "stellaris": [
                                        "Starry triggerfish",
                                        "스타리트리거",
                                    ],
                                },
                            },
                            "Monacanthidae": {  # 쥐치과 (파일피쉬)
                                "Oxymonacanthus": {
                                    "longirostris": [
                                        "Harlequin filefish",
                                        "Longnose filefish",
                                        "할리퀸파일피쉬",
                                    ]
                                },
                                "Pervagor": {
                                    "spilosoma": [
                                        "Fantail filefish",
                                        "팬테일파일피쉬",
                                    ],
                                    "janthinosoma": [
                                        "Blackbar filefish",
                                        "블랙바파일피쉬",
                                    ],
                                },
                                "Cantherhines": {
                                    "dumerilii": [
                                        "Whitespotted filefish",
                                        "화이트스팟파일피쉬",
                                    ],
                                    "pardalis": [
                                        "Honeycomb filefish",
                                        "허니콤파일피쉬",
                                    ],
                                    "macrocerus": [
                                        "Orange filefish",
                                        "오렌지파일피쉬",
                                    ],
                                },
                            },
                            "Ostraciidae": {  # 상자고기과 (박스피쉬)
                                "Ostracion": {
                                    "cubicus": [
                                        "Yellow boxfish",
                                        "옐로우박스피쉬",
                                    ],
                                    "meleagris": [
                                        "Whitespotted boxfish",
                                        "화이트스팟박스피쉬",
                                    ],
                                },
                                "Lactoria": {
                                    "cornuta": [
                                        "Longhorn cowfish",
                                        "롱혼카우피쉬",
                                    ],
                                    "fornasini": [
                                        "Thornback cowfish",
                                        "쏜백카우피쉬",
                                    ],
                                },
                                "Lactophrys": {
                                    "bicaudalis": [
                                        "Spotted trunkfish",
                                        "스팟티드트렁크피쉬",
                                    ],
                                    "trigonus": [
                                        "Trunkfish",
                                        "트렁크피쉬",
                                    ],
                                },
                            },
                            "Diodontidae": {  # 성게복과 (포큐파인피쉬)
                                "Diodon": {
                                    "holocanthus": [
                                        "Longspined porcupinefish",
                                        "롱스파인포큐파인피쉬",
                                    ],
                                    "hystrix": [
                                        "Spot-fin porcupinefish",
                                        "스팟핀포큐파인피쉬",
                                    ],
                                    "liturosus": [
                                        "Black-blotched porcupinefish",
                                        "블랙블롯치드포큐파인피쉬",
                                    ],
                                },
                                "Chilomycterus": {
                                    "schoepfii": [
                                        "Striped burrfish",
                                        "스트라이프드버피쉬",
                                    ]
                                },
                            },
                        }
                    },
                    "Gobiiformes": {  # 망둑어목
                        "Gobiidae": {  # 망둑어과 (고비)
                            "Gobiodon": {
                                "okinawae": [
                                    "Yellow coral goby",
                                    "옐로우코랄고비",
                                ],
                                "atrangulatus": [
                                    "Earspot coral goby",
                                    "이어스팟코랄고비",
                                ],
                                "citrinus": [
                                    "Citron goby",
                                    "시트론고비",
                                ],
                            },
                            "Nemateleotris": {
                                "magnifica": [
                                    "Fire goby",
                                    "Firefish",
                                    "파이어고비",
                                ],
                                "decora": [
                                    "Purple firefish",
                                    "퍼플파이어피쉬",
                                ],
                                "helfrichi": [
                                    "Helfrich's firefish",
                                    "헬프리치파이어피쉬",
                                ],
                            },
                            "Valenciennea": {
                                "puellaris": [
                                    "Orange-spotted goby",
                                    "오렌지스팟고비",
                                ],
                                "strigata": [
                                    "Golden-head sleeper goby",
                                    "골든헤드슬리퍼고비",
                                ],
                                "sexguttata": [
                                    "Sixspot goby",
                                    "식스스팟고비",
                                ],
                                "wardi": [
                                    "Ward's sleeper goby",
                                    "워즈슬리퍼고비",
                                ],
                            },
                            "Cryptocentrus": {
                                "cinctus": [
                                    "Yellow watchman goby",
                                    "옐로우와치맨고비",
                                ],
                                "pavoninoides": [
                                    "Blue-spotted watchman goby",
                                    "블루스팟와치맨고비",
                                ],
                                "leptocephalus": [
                                    "Pink-speckled watchman goby",
                                    "핑크스페클드와치맨",
                                ],
                            },
                            "Amblyeleotris": {
                                "steinitzi": [
                                    "Magnus goby",
                                    "마그누스고비",
                                ],
                                "wheeleri": [
                                    "Wheeler's shrimp goby",
                                    "휠러쉬림프고비",
                                ],
                                "randalli": [
                                    "Randall's shrimp goby",
                                    "랜달쉬림프고비",
                                ],
                                "aurora": [
                                    "Pinkbar goby",
                                    "핑크바고비",
                                ],
                            },
                            "Elacatinus": {
                                "oceanops": [
                                    "Neon goby",
                                    "네온고비",
                                ]
                            },
                            "Gobiosoma": {
                                "evelynae": [
                                    "Sharknose goby",
                                    "샤크노즈고비",
                                ]
                            },
                            "Stonogobiops": {
                                "nematodes": [
                                    "Hi-fin red banded goby",
                                    "하이핀레드밴디드고비",
                                ],
                                "yasha": [
                                    "Yasha goby",
                                    "야샤고비",
                                ],
                            },
                            "Koumansetta": {
                                "rainfordi": [
                                    "Rainford's goby",
                                    "레인포드고비",
                                ],
                                "hectori": [
                                    "Hector's goby",
                                    "헥터고비",
                                ],
                            },
                        },
                        "Callionymidae": {  # 드래고넷과
                            "Synchiropus": {
                                "splendidus": [
                                    "Mandarin fish",
                                    "Mandarin dragonet",
                                    "만다린피쉬",
                                ],
                                "picturatus": [
                                    "Spotted mandarin",
                                    "Psychedelic mandarin",
                                    "스팟티드만다린",
                                ],
                                "ocellatus": [
                                    "Scooter blenny",
                                    "Ocellated dragonet",
                                    "스쿠터블레니",
                                ],
                                "stellatus": [
                                    "Starry dragonet",
                                    "스타리드래고넷",
                                ],
                                "morrisoni": [
                                    "Morrison's dragonet",
                                    "모리슨드래고넷",
                                ],
                                "rameus": [
                                    "Orangespotted dragonet",
                                    "오렌지스팟드래고넷",
                                ],
                                "circularis": [
                                    "Circular dragonet",
                                    "서큘러드래고넷",
                                ],
                                "moyeri": [
                                    "Moyer's dragonet",
                                    "모이어드래고넷",
                                ],
                                "rosulentus": [
                                    "Rosy dragonet",
                                    "로지드래고넷",
                                ],
                            },
                            "Callionymus": {
                                "lyra": [
                                    "Common dragonet",
                                    "커먼드래고넷",
                                ],
                                "bairdi": [
                                    "Lancer dragonet",
                                    "랜서드래고넷",
                                ],
                                "pusillus": [
                                    "Small dragonet",
                                    "스몰드래고넷",
                                ],
                                "reticulatus": [
                                    "Reticulated dragonet",
                                    "레티큘레이티드드래고넷",
                                ],
                            },
                            "Dactylopus": {
                                "dactylopus": [
                                    "Fingered dragonet",
                                    "핑거드래고넷",
                                ],
                            },
                            "Diplogrammus": {
                                "pauciradiatus": [
                                    "Spotted dragonet",
                                    "스팟티드드래고넷",
                                ],
                                "goramensis": [
                                    "Goram dragonet",
                                    "고람드래고넷",
                                ],
                            },
                            "Neosynchiropus": {
                                "ocellatus": [
                                    "Ocellated dragonet",
                                    "오셀레이티드드래고넷",
                                ],
                            },
                            "Pterosynchiropus": {
                                "splendidus": [
                                    "Splendid dragonet",
                                    "스플렌디드드래고넷",
                                ],
                            },
                        },
                        "Microdesmidae": {  # 실고기과
                            "Ptereleotris": {
                                "evides": [
                                    "Blackfin dartfish",
                                    "블랙핀다트피쉬",
                                ],
                                "zebra": [
                                    "Zebra dartfish",
                                    "제브라다트피쉬",
                                ],
                                "hanae": [
                                    "Blue hana goby",
                                    "블루하나고비",
                                ],
                            }
                        },
                    },
                    "Syngnathiformes": {  # 실고기목
                        "Syngnathidae": {  # 해마과
                            "Hippocampus": {
                                "kuda": [
                                    "Yellow seahorse",
                                    "옐로우해마",
                                ],
                                "erectus": [
                                    "Lined seahorse",
                                    "라인드해마",
                                ],
                                "reidi": [
                                    "Longsnout seahorse",
                                    "롱스나웃해마",
                                ],
                                "barbouri": [
                                    "Barbour's seahorse",
                                    "바버해마",
                                ],
                                "comes": [
                                    "Tiger tail seahorse",
                                    "타이거테일해마",
                                ],
                                "zosterae": [
                                    "Dwarf seahorse",
                                    "드워프해마",
                                ],
                            },
                            "Syngnathus": {
                                "scovelli": [
                                    "Gulf pipefish",
                                    "걸프파이프피쉬",
                                ]
                            },
                            "Doryrhamphus": {
                                "excisus": [
                                    "Bluestripe pipefish",
                                    "블루스트라이프파이프피쉬",
                                ],
                                "dactyliophorus": [
                                    "Banded pipefish",
                                    "밴디드파이프피쉬",
                                ],
                                "baliensis": [
                                    "Bali bluestripe pipefish",
                                    "발리블루스트라이프",
                                ],
                            },
                            "Corythoichthys": {
                                "haematopterus": [
                                    "Messmate pipefish",
                                    "메스메이트파이프피쉬",
                                ],
                                "intestinalis": [
                                    "Broad-banded pipefish",
                                    "브로드밴디드파이프피쉬",
                                ],
                            },
                        },
                        "Nemateleotridae": {  # 다트피쉬과 (Firefish / Dartfish)
                            "Nemateleotris": {
                                "decora": [
                                    "Purple firefish",
                                    "퍼플파이어피쉬",
                                ],
                                "magnifica": [
                                    "Firefish goby",
                                    "파이어피쉬고비",
                                ],
                                "helfrichi": [
                                    "Helfrich's firefish",
                                    "헬프리치파이어피쉬",
                                ],
                            },
                            "Ptereleotris": {
                                "zebra": [
                                    "Zebra dartfish",
                                    "제브라다트피쉬",
                                ],
                                "hanae": [
                                    "Blue gudgeon dartfish",
                                    "블루구전다트피쉬",
                                ]
                            }
                        }
                    },
                    "Scorpaeniformes": {  # 쏨뱅이목
                        "Scorpaenidae": {  # 쏨뱅이과 (라이언피쉬)
                            "Pterois": {
                                "volitans": [
                                    "Red lionfish",
                                    "레드라이언피쉬",
                                ],
                                "miles": [
                                    "Devil firefish",
                                    "데빌파이어피쉬",
                                ],
                                "antennata": [
                                    "Antennata lionfish",
                                    "안테나타라이언피쉬",
                                ],
                                "radiata": [
                                    "Radial firefish",
                                    "래디얼파이어피쉬",
                                ],
                                "russelli": [
                                    "Russell's lionfish",
                                    "러셀라이언피쉬",
                                ],
                            },
                            "Dendrochirus": {
                                "zebra": [
                                    "Zebra lionfish",
                                    "제브라라이언피쉬",
                                ],
                                "biocellatus": [
                                    "Fu manchu lionfish",
                                    "푸만추라이언피쉬",
                                ],
                                "brachypterus": [
                                    "Dwarf lionfish",
                                    "드워프라이언피쉬",
                                ],
                            },
                        },
                    },
                    "Perciformes": {  # 농어목
                        "Serranidae": {  # 바리과 (그루퍼, 바슬렛)
                            "Cephalopholis": {
                                "miniata": [
                                    "Coral hind",
                                    "코랄하인드",
                                ],
                                "argus": [
                                    "Peacock hind",
                                    "피콕하인드",
                                ],
                                "leopardus": [
                                    "Leopard hind",
                                    "레오파드하인드",
                                ],
                            },
                            "Epinephelus": {
                                "fasciatus": [
                                    "Blacktip grouper",
                                    "블랙팁그루퍼",
                                ],
                                "merra": [
                                    "Honeycomb grouper",
                                    "허니콤그루퍼",
                                ],
                                "polyphekadion": [
                                    "Camouflage grouper",
                                    "카모플라쥬그루퍼",
                                ],
                            },
                            "Cromileptes": {
                                "altivelis": [
                                    "Panda grouper",
                                    "Humpback grouper",
                                    "Humpback seabass",
                                    "팬더그루퍼",
                                    "험프백그루퍼",
                                ],
                            },
                            "Pseudanthias": {
                                "squamipinnis": [
                                    "Anthias",
                                    "Sea goldie",
                                    "안티아스",
                                ],
                                "tuka": [
                                    "Purple queen",
                                    "퍼플퀸",
                                ],
                                "bicolor": [
                                    "Bicolor anthias",
                                    "바이컬러안티아스",
                                ],
                                "dispar": [
                                    "Peach anthias",
                                    "피치안티아스",
                                ],
                                "pleurotaenia": [
                                    "Square-spot anthias",
                                    "스퀘어스팟안티아스",
                                ],
                                "pictilis": [
                                    "Pictilis anthias",
                                    "픽틸리스안티아스",
                                ],
                                "smithvanizi": [
                                    "Resplendent anthias",
                                    "레스플렌던트안티아스",
                                ],
                                "ignitus": [
                                    "Flame anthias",
                                    "플레임안티아스",
                                ],
                                "evansi": [
                                    "Evan's anthias",
                                    "에반스안티아스",
                                ],
                                "bartlettorum": [
                                    "Bartlett's anthias",
                                    "바틀렛안티아스",
                                ],
                                "randalli": [
                                    "Randall's anthias",
                                    "랜달안티아스",
                                ],
                                "lori": [
                                    "Lori anthias",
                                    "로리안티아스",
                                ],
                                "fluorescens": [
                                    "Sunset anthias",
                                    "선셋안티아스",
                                ],
                                # 'parvati'는 현재 유효하지 않고 'bimaculatus'로 통용
                                "bimaculatus": [
                                    "Twospot anthias",
                                    "Two-spot anthias",
                                    "Bimaculatus anthias",
                                    "트윈스팟안티아스",
                                    "투스팟안티아스",
                                ],
                            },
                            "Nemanthias": {
                                "carberryi": [
                                    "Threadfin anthias",
                                    "캐리베리안티아스",
                                ],
                            },
                            "Odontanthias": {
                                "borbonius": [
                                    "Borbonius anthias",
                                    "보르보니우스안티아스",
                                ],
                            },
                            "Tosanoides": {
                                "flavofasciatus": [
                                    "Yellow striped anthias",
                                    "옐로우스트라이프안티아스",
                                ],
                            },
                            "Plectranthias": {
                                "inermis": [
                                    "Geometric pygmy perchlet",
                                    "지오메트릭피그미퍼치렛",
                                ],
                                "kelloggi": [
                                    "Kellogg's perchlet",
                                    "켈로그퍼치렛",
                                ],
                            },
                            "Liopropoma": {
                                "rubre": [
                                    "Peppermint basslet",
                                    "페퍼민트바슬렛",
                                ],
                                "swalesi": [
                                    "Swales' basslet",
                                    "스웨일스바슬렛",
                                ],
                                "carmabi": [
                                    "Candy basslet",
                                    "캔디바슬렛",
                                ],
                                # 'suscitatum'는 유효한 학명이 아니므로 제거함
                                "aberrans": [
                                    "Aberrant basslet",
                                    "어버런트바슬렛",
                                ],
                            },
                            "Variola": {
                                "louti": [
                                    "Louti grouper",
                                    "루티그루퍼",
                                ],
                            },
                            "Aethaloperca": {
                                "rogaa": [
                                    "Redmouth grouper",
                                    "레드마우스그루퍼",
                                ],
                            },
                        },
                        "Lutjanidae": {  # 도미과 (스내퍼)
                            "Lutjanus": {
                                "sebae": [
                                    "Emperor red snapper",
                                    "엠페러레드스내퍼",
                                ],
                                "kasmira": [
                                    "Common bluestripe snapper",
                                    "커먼블루스트라이프스내퍼",
                                ],
                            }
                        },
                        "Caesionidae": {  # 전갱이과
                            "Caesio": {
                                "teres": [
                                    "Yellow and blueback fusilier",
                                    "옐로우앤블루백퓨질리어",
                                ]
                            }
                        },
                        "Haemulidae": {  # 석태과 (그런트)
                            "Plectorhinchus": {
                                "chaetodonoides": [
                                    "Harlequin sweetlips",
                                    "할리퀸스위트립스",
                                ],
                                "orientalis": [
                                    "Oriental sweetlips",
                                    "오리엔탈스위트립스",
                                ],
                            }
                        },
                        "Grammatidae": {  # 그라마과
                            "Gramma": {
                                "loreto": [
                                    "Royal gramma",
                                    "Fairy basslet",
                                    "로얄그라마",
                                ],
                                "melacara": [
                                    "Blackcap basslet",
                                    "블랙캡바슬렛",
                                ],
                                "brasiliensis": [
                                    "Brazilian gramma",
                                    "브라질리언그라마",
                                ],
                            }
                        },
                        "Pseudochromidae": {  # 닷백과 (데빌피쉬)
                            "Pseudochromis": {
                                "fridmani": [
                                    "Orchid dottyback",
                                    "Fridman's dottyback",
                                    "오키드닷백",
                                ],
                                "aldabraensis": [
                                    "Neon dottyback",
                                    "네온닷백",
                                ],
                                "paccagnellae": [
                                    "False gramma",
                                    "Royal dottyback",
                                    "로얄닷백",
                                ],
                                "springeri": [
                                    "Springer's dottyback",
                                    "스프링거닷백",
                                ],
                                "flavivertex": [
                                    "Sunrise dottyback",
                                    "선라이즈닷백",
                                ],
                            },
                            "Labracinus": {
                                "cyclophthalmus": [
                                    "Firetail devil",
                                    "파이어테일데빌",
                                ],
                            },
                        },
                        "Plesiopidae": {  # 롱핀과 (어세서)
                            "Plesiops": {
                                "coeruleolineatus": [
                                    "Crikey fish",
                                    "Longfin fish",
                                    "크리키피쉬",
                                ],
                                "oxycephalus": [
                                    "Sharp-headed longfin",
                                    "샤프헤드롱핀",
                                ],
                            },
                            "Assessor": {
                                "macneilli": [
                                    "Blue assessor",
                                    "Macneill's assessor",
                                    "블루어세서",
                                ],
                                "flavissimus": [
                                    "Yellow assessor",
                                    "옐로우어세서",
                                ],
                                "randalli": [
                                    "Randall's assessor",
                                    "랜달어세서",
                                ],
                            },
                        },
                        "Holocentridae": {
                            # 다이얼새우고기과 (Squirrelfish / Soldierfish)
                            "Sargocentron": {
                                "diadema": [
                                    "Crown squirrelfish",
                                    "크라운스쿼럴피쉬",
                                ],
                                "spiniferum": [
                                    "Sabre squirrelfish",
                                    "세이버스쿼럴피쉬",
                                ],
                            },
                            "Holocentrus": {
                                "adscensionis": [
                                    "Squirrelfish",
                                    "레드스쿼럴피쉬",
                                ]
                            },
                            "Myripristis": {
                                # 대표적인 Soldierfish / Bigeye 계열 - 사용자 요청으로 추가
                                "berndti": [
                                    "Bigeye soldierfish",
                                    "빅아이 솔져피쉬",
                                ],
                                "murdjan": [
                                    "Pinecone soldierfish",
                                    "파인콘 솔져피쉬",
                                ],
                            }
                        },
                        "Mullidae": {  # 염소고기과 (Goatfish)
                            "Parupeneus": {
                                "multifasciatus": [
                                    "Manybar goatfish",
                                    "메니바르고트피쉬",
                                ],
                                "porphyreus": [
                                    "Red goatfish",
                                    "레드고트피쉬",
                                ],
                            },
                            "Upeneus": {
                                "tragula": [
                                    "Freckled goatfish",
                                    "프레클드고트피쉬",
                                ]
                            }
                        },
                        "Malacanthidae": {  # 타일피쉬과 (Tilefish)
                            "Hoplolatilus": {
                                "chlupatyi": [
                                    "Flashing tilefish",
                                    "플래싱타일피쉬",
                                ],
                                "fourmanoiri": [
                                    "Purple tilefish",
                                    "퍼플타일피쉬",
                                ],
                            }
                        },
                        "Sphyraenidae": {  # 바라쿠다과 (소형 juvenile 제한적 관상)
                            "Sphyraena": {
                                "barras": [
                                    "Barracuda (juvenile)",
                                    "주니어바라쿠다",
                                ]
                            }
                        },
                        "Aulostomidae": {  # 트럼펫피쉬과
                            "Aulostomus": {
                                "chinensis": [
                                    "Chinese trumpetfish",
                                    "차이니스트럼펫피쉬",
                                ],
                                "strigosus": [
                                    "Atlantic trumpetfish",
                                    "애틀랜틱트럼펫피쉬",
                                ]
                            }
                        },
                        "Fistulariidae": {  # 코르넷피쉬과
                            "Fistularia": {
                                "commersonii": [
                                    "Bluespotted cornetfish",
                                    "블루스팟코넷피쉬",
                                ]
                            }
                        },
                    },
                    "Anguilliformes": {  # 뱀장어목
                        "Muraenidae": {  # 곰치과 (모레이일)
                            "Gymnothorax": {
                                "tesselata": [
                                    "Honeycomb moray",
                                    "허니콤모레이",
                                ],
                                "flavimarginatus": [
                                    "Yellow-edged moray",
                                    "옐로우에지드모레이",
                                ],
                                "undulatus": [
                                    "Undulated moray",
                                    "언둘레이티드모레이",
                                ],
                                "javanicus": [
                                    "Giant moray",
                                    "자이언트모레이",
                                ],
                                "melatremus": [
                                    "Golden dwarf moray",
                                    "골든드워프모레이",
                                ],
                            },
                            "Rhinomuraena": {
                                "quaesita": [
                                    "Ribbon eel",
                                    "리본일",
                                ]
                            },
                            "Echidna": {
                                "nebulosa": [
                                    "Snowflake moray",
                                    "스노우플레이크모레이",
                                ]
                            },
                            # Gymnomuraena zebra 유지 (Gymnothorax 중복 제거)
                            "Gymnomuraena": {
                                "zebra": [
                                    "Zebra moray",
                                    "제브라모레이",
                                ]
                            },
                        },
                        "Ophichthidae": {  # 뱀장어과
                            "Myrichthys": {
                                "colubrinus": [
                                    "Harlequin snake eel",
                                    "할리퀸스네이크일",
                                ]
                            }
                        },
                    },
                    "Pleuronectiformes": {  # 가자미목 (일부 관상용 플랫피쉬)
                        "Bothidae": {  # 넙치과 (Left-eyed flounders)
                            "Bothus": {
                                "lunatus": [
                                    "Peacock flounder",
                                    "피콕플라운더",
                                ]
                            }
                        },
                        "Paralichthyidae": {  # 넙칫과 (Sand flounders)
                            "Paralichthys": {
                                "olivaceus": [
                                    "Olive flounder",
                                    "올리브플라운더",
                                ]
                            }
                        },
                        "Soleidae": {  # 넙치목 솔레
                            "Zebrias": {
                                "fasciatus": [
                                    "Zebra sole",
                                    "제브라솔",
                                ]
                            }
                        },
                        # 주의: 다수 가자미류는 대형/식용 위주이므로 최소 대표종만 포함
                    },
                    "Lophiiformes": {  # 아귀목
                        "Antennariidae": {  # 아귀과 (프로그피쉬)
                            "Antennarius": {
                                "maculatus": [
                                    "Warty frogfish",
                                    "워티프로그피쉬",
                                ],
                                "striatus": [
                                    "Striated frogfish",
                                    "스트라이에이티드프로그피쉬",
                                ],
                                "pictus": [
                                    "Painted frogfish",
                                    "페인티드프로그피쉬",
                                ],
                            }
                        }
                    },
                }
            },
        }

        # 외부 파일에서 분류 체계 로드 (있는 경우)
        if taxonomy_file:
            self.load_taxonomy_from_file(taxonomy_file)

    # 과(Family) 태그 지정:
    # 'core'     : 핵심 관상어
    # 'extended' : 확장/드물게 사육
    # 'exclude'  : 비관상/제외
        # 기본적으로 지정되지 않은 과는 'core'로 간주
        self.family_tags: Dict[str, str] = {
            # 제외 (사육 부적합 / 대형 포식자)
            "Sphyraenidae": "exclude",  # 바라쿠다 - 대형 포식성, 일반 관상용 제외
            # 확장 (특수 수조/대형 수조에서 제한적으로 사육)
            "Hemiscylliidae": "extended",  # 대나무상어
            "Scyliorhinidae": "extended",  # 고양이상어
            "Holocentridae": "extended",  # 다소 크고 야행성 (사육은 가능)
            "Mullidae": "extended",       # 활동성 높음
            "Malacanthidae": "extended",  # 타일피쉬 (점프 위험)
            "Aulostomidae": "extended",   # 트럼펫피쉬 (대형 수조)
            "Fistulariidae": "extended",  # 코넷피쉬 (매우 길어 공간 요구)
        }

        # 인덱스 생성
        self._build_indexes()

    def _build_indexes(self):
        """검색 성능을 위한 인덱스 생성"""
        self.species_index: Dict[str, SpeciesInfo] = {}
        self.genus_index: Dict[str, List[SpeciesInfo]] = {}
        self.family_index: Dict[Tuple[str, str, str], List[SpeciesInfo]] = {}
        self.common_name_index: Dict[str, List[SpeciesInfo]] = {}

        # Chondrichthyes 처리
        try:
            chondrichthyes = self.fish_taxonomy.get("Chondrichthyes", {})
            for order_name, order_data in chondrichthyes.items():
                if not isinstance(order_data, dict):
                    continue
                for family_name, family_data in order_data.items():
                    if not isinstance(family_data, dict):
                        continue
                    for genus_name, genus_data in family_data.items():
                        if not isinstance(genus_data, dict):
                            continue
                        for species_name, common_names in genus_data.items():
                            if isinstance(common_names, list):
                                species_info = SpeciesInfo(
                                    genus=genus_name,
                                    species=species_name,
                                    common_names=common_names,
                                    family=family_name,
                                    order=order_name,
                                    class_name="Chondrichthyes",
                                )
                                self._add_to_indexes(species_info)
        except Exception as e:
            self.logger.error(f"Chondrichthyes 인덱스 생성 오류: {e}")

        # Osteichthyes 처리
        try:
            osteichthyes = self.fish_taxonomy.get("Osteichthyes", {})
            actinopterygii = osteichthyes.get("Actinopterygii", {})

            # 재귀적으로 모든 레벨 처리
            self._process_osteichthyes_data(actinopterygii, "Osteichthyes")
            
        except Exception as e:
            self.logger.error(f"Osteichthyes 인덱스 생성 오류: {e}")

        self.logger.info(f"분류 체계 인덱스 생성 완료: {len(self.species_index)}종")

    def _process_osteichthyes_data(self, data, class_name):
        """Osteichthyes 데이터 재귀 처리"""
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
    
    def _find_order_name(
        self, root_data: Dict[str, Any], family_name: str
    ) -> str:
        """특정 과가 속한 목(order) 이름 찾기"""
        def search_order(
            data: Dict[str, Any], path: List[str] = []
        ) -> Optional[str]:
            for key, value in data.items():
                if not isinstance(value, dict):
                    continue
                
                current_path = path + [key]
                
                # 현재 레벨에서 찾는 과를 발견
                if family_name in value:
                    # 경로에서 'formes'로 끝나는 목 찾기
                    for p in reversed(current_path):
                        if p.endswith('formes'):
                            return p
                    # 'formes'가 없으면 마지막 레벨을 목으로 간주
                    return current_path[-1] if current_path else "Unknown"
                
                # 재귀 탐색
                result = search_order(value, current_path)
                if result:
                    return result
            
            return None
        
        result = search_order(root_data)
        return result or "Unknown"
    
    def _is_family_with_genera(self, family_data):
        """과 데이터가 직접 속을 포함하는지 확인"""
        for key, value in family_data.items():
            if isinstance(value, dict):
                # 속 데이터인지 확인 (종 데이터를 포함하는지)
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, list):  # 종의 일반명 리스트
                        return True
        return False

    def _process_family_data(
        self, family_data, family_name, order_name, class_name
    ):
        """과 데이터 처리 (아과 구조 지원)"""
        for key, value in family_data.items():
            if not isinstance(value, dict):
                continue
            
            # 아과인지 속인지 판단
            # 아과는 보통 'inae'로 끝나고, 그 안에 속들이 있음
            if key.endswith('inae'):
                # 아과 구조 - 재귀적으로 처리
                self._process_family_data(
                    value, family_name, order_name, class_name
                )
            else:
                # 속 구조 - 직접 처리
                genus_name = key
                genus_data = value
                if isinstance(genus_data, dict):
                    for species_name, common_names in genus_data.items():
                        if isinstance(common_names, list):
                            species_info = SpeciesInfo(
                                genus=genus_name,
                                species=species_name,
                                common_names=common_names,
                                family=family_name,
                                order=order_name,
                                class_name=class_name,
                            )
                            self._add_to_indexes(species_info)

    def _add_to_indexes(self, species_info: SpeciesInfo):
        """종 정보를 인덱스에 추가"""
        # 학명 인덱스
        scientific_name = species_info.scientific_name
        self.species_index[scientific_name] = species_info

        # 속 인덱스
        if species_info.genus not in self.genus_index:
            self.genus_index[species_info.genus] = []
        self.genus_index[species_info.genus].append(species_info)

        # 과 인덱스
        family_key = (
            species_info.class_name,
            species_info.order,
            species_info.family,
        )
        if family_key not in self.family_index:
            self.family_index[family_key] = []
        self.family_index[family_key].append(species_info)

        # 일반명 인덱스
        for common_name in species_info.common_names:
            common_lower = common_name.lower()
            if common_lower not in self.common_name_index:
                self.common_name_index[common_lower] = []
            self.common_name_index[common_lower].append(species_info)

    def get_species_info(
        self, genus: str, species: str
    ) -> Optional[SpeciesInfo]:
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

    def get_species_by_family(
        self, class_name: str, order_name: str, family_name: str
    ) -> List[Tuple[str, str]]:
        """특정 과의 모든 종 반환 (genus, species)"""
        species_list = []

        # 해당 과의 모든 종 찾기
        for species_info in self.species_index.values():
            if (
                species_info.class_name == class_name
                and species_info.order == order_name
                and species_info.family == family_name
            ):
                species_list.append((species_info.genus, species_info.species))

        return species_list

    def get_species_by_genus(self, genus_name: str) -> List[SpeciesInfo]:
        """속명으로 종 목록 반환"""
        return self.genus_index.get(genus_name, [])

    def get_all_families(
        self, ornamental_only: bool = True
    ) -> List[Tuple[str, str, str]]:
        """과 목록 반환 (class, order, family)

        ornamental_only=True 이면 family_tags 에서 'exclude' 로 표시된 과는 제외.
        확장(ex. extended) 과도 포함(일반적으로 사육 가능). 향후 필요 시 파라미터 추가 가능.
        """
        families: List[Tuple[str, str, str]] = []

        def include_family(family_name: str) -> bool:
            if not ornamental_only:
                return True
            tag = self.family_tags.get(family_name, "core")
            return tag != "exclude"

        # Chondrichthyes 처리
        chondrichthyes = self.fish_taxonomy.get("Chondrichthyes", {})
        for order_name, order_data in chondrichthyes.items():
            if isinstance(order_data, dict):
                for family_name, family_data in order_data.items():
                    if (
                        isinstance(family_data, dict)
                        and include_family(family_name)
                    ):
                        families.append(
                            ("Chondrichthyes", order_name, family_name)
                        )

        # Osteichthyes 처리 - family_index 사용 (이미 인덱스에 존재하는 것만)
        for family_key, _species_list in self.family_index.items():
            class_name, order_name, family_name = family_key
            if class_name == "Osteichthyes" and include_family(family_name):
                families.append((class_name, order_name, family_name))

        # 목(Order) 우선 정렬, 같은 목 내에서는 과(Family) 알파벳 순
        families.sort(key=lambda x: (x[1].lower(), x[2].lower()))
        return families

    def is_family_excluded(self, family_name: str) -> bool:
        """관상어 필터에서 제외되는 과인지 여부"""
        return self.family_tags.get(family_name, "core") == "exclude"

    def set_family_tag(self, family_name: str, tag: str) -> None:
        """과 태그 동적 설정 (core/extended/exclude)"""
        if tag not in ("core", "extended", "exclude"):
            raise ValueError("tag must be one of: core, extended, exclude")
        self.family_tags[family_name] = tag
        self.logger.info(f"과 태그 변경: {family_name} -> {tag}")

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
                                species_dir = (
                                    genus_path / f"{genus_name}_{species_name}"
                                )
                                species_dir.mkdir(exist_ok=True)

        create_recursive_dirs(self.fish_taxonomy, base_dir)
        self.logger.info(f"완전한 분류학적 디렉토리 구조 생성 완료: {base_dir}")

    def get_taxonomy_statistics(self) -> Dict[str, Any]:
        """완전한 분류 체계 통계 반환"""
        total_species = len(self.species_index)
        total_genera = len(self.genus_index)
        total_families = len(self.family_index)

        class_stats = {}
        for species_info in self.species_index.values():
            class_name = species_info.class_name
            if class_name not in class_stats:
                class_stats[class_name] = 0
            class_stats[class_name] += 1

        return {
            "total_species": total_species,
            "total_genera": total_genera,
            "total_families": total_families,
            "total_classes": len(class_stats),
            "class_distribution": class_stats,
        }

    def export_taxonomy(self, file_path: str) -> bool:
        """분류 체계를 파일로 내보내기"""
        try:
            export_data = {
                "export_date": datetime.now().isoformat(),
                "statistics": self.get_taxonomy_statistics(),
                "taxonomy": self.fish_taxonomy,
            }

            with open(file_path, "w", encoding="utf-8") as f:
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
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 분류 체계 데이터 추출
            if "taxonomy" in data:
                external_taxonomy = data["taxonomy"]
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
        # 간단한 병합 로직 (실제로는 더 복잡할 수 있음)
        for class_name, class_data in external_taxonomy.items():
            if class_name not in self.fish_taxonomy:
                self.fish_taxonomy[class_name] = class_data
            # 더 세밀한 병합 로직은 필요에 따라 구현
