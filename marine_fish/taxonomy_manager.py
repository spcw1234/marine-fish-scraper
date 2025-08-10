"""
Taxonomic data management system for marine fish classification
Complete database of marine ornamental fish species
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
                                },
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
                                    "bispinosus": [
                                        "Coral beauty",
                                        "Two-spined angelfish",
                                        "코랄뷰티",
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
                                        "펄스케일엔젤",
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
                                },
                            },
                            "Pomacentridae": {  # 자리돔과 (클라운피쉬, 댐셀)
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
                                    "zoster": [
                                        "Zoster butterflyfish",
                                        "조스터버터플라이",
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
                                    "chrysurus": [
                                        "Pearlscale butterflyfish",
                                        "펄스케일버터플라이",
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
                                },
                                "Novaculichthys": {
                                    "taeniourus": [
                                        "Rockmover wrasse",
                                        "Dragon wrasse",
                                        "드래곤놀래기",
                                        "나오코래스",
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
                                },
                                "Macropharyngodon": {
                                    "meleagris": [
                                        "Leopard wrasse",
                                        "레오파드놀래기",
                                    ],
                                    "negrosensis": [
                                        "Yellow-spotted wrasse",
                                        "옐로우스팟놀래기",
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
                                "Apogon": {
                                    "maculatus": ["Flamefish", "플레임피쉬"],
                                    "cyanosoma": [
                                        "Yellow-striped cardinalfish",
                                        "옐로우스트라이프카디널",
                                    ],
                                    "leptacanthus": [
                                        "Threadfin cardinalfish",
                                        "쓰레드핀카디널",
                                    ],
                                    "compressus": [
                                        "Ochre-striped cardinalfish",
                                        "오커스트라이프카디널",
                                    ],
                                    "aureus": [
                                        "Ring-tailed cardinalfish",
                                        "링테일카디널",
                                    ],
                                    "angustatus": [
                                        "Broad-striped cardinalfish",
                                        "브로드스트라이프카디널",
                                    ],
                                    "cookii": [
                                        "Cook's cardinalfish",
                                        "쿡카디널",
                                    ],
                                    "doederleini": [
                                        "Doederlein's cardinalfish",
                                        "되덜라인카디널",
                                    ],
                                    "exostigma": [
                                        "Narrowstripe cardinalfish",
                                        "내로우스트라이프카디널",
                                    ],
                                    "fragilis": [
                                        "Fragile cardinalfish",
                                        "프래질카디널",
                                    ],
                                    "hartzfeldii": [
                                        "Hartzfeld's cardinalfish",
                                        "하츠펠드카디널",
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
                                    "apogonoides": [
                                        "Short-tooth cardinal",
                                        "쇼트투스카디널",
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
                                    ]
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
                                },
                                "Takifugu": {
                                    "niphobles": [
                                        "Starry puffer",
                                        "스타리퍼퍼",
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
                            },
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
                            },
                            "Gramma": {
                                "loreto": [
                                    "Royal gramma",
                                    "로얄그라마",
                                ],
                                "melacara": [
                                    "Blackcap basslet",
                                    "블랙캡바슬렛",
                                ],
                            },
                            "Liopropoma": {
                                "rubre": [
                                    "Peppermint basslet",
                                    "페퍼민트바슬렛",
                                ]
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
                                "zebra": [
                                    "Zebra moray",
                                    "제브라모레이",
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

        # 인덱스 생성
        self._build_indexes()

    def _build_indexes(self):
        """검색 성능을 위한 인덱스 생성"""
        self.species_index: Dict[str, SpeciesInfo] = {}
        self.genus_index: Dict[str, List[SpeciesInfo]] = {}
        self.family_index: Dict[str, List[SpeciesInfo]] = {}
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

            for superorder_name, superorder_data in actinopterygii.items():
                if not isinstance(superorder_data, dict):
                    continue
                for order_name, order_data in superorder_data.items():
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
                                        class_name="Osteichthyes",
                                    )
                                    self._add_to_indexes(species_info)
        except Exception as e:
            self.logger.error(f"Osteichthyes 인덱스 생성 오류: {e}")

        self.logger.info(f"분류 체계 인덱스 생성 완료: {len(self.species_index)}종")

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
        if species_info.family not in self.family_index:
            self.family_index[species_info.family] = []
        self.family_index[species_info.family].append(species_info)

        # 일반명 인덱스
        for common_name in species_info.common_names:
            common_lower = common_name.lower()
            if common_lower not in self.common_name_index:
                self.common_name_index[common_lower] = []
            self.common_name_index[common_lower].append(species_info)

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

    def get_all_families(self) -> List[Tuple[str, str, str]]:
        """모든 과 목록 반환 (class, order, family)"""
        families = []

        # Chondrichthyes 처리
        chondrichthyes = self.fish_taxonomy.get("Chondrichthyes", {})
        for order_name, order_data in chondrichthyes.items():
            if isinstance(order_data, dict):
                for family_name, family_data in order_data.items():
                    if isinstance(family_data, dict):
                        families.append(("Chondrichthyes", order_name, family_name))

        # Osteichthyes 처리
        osteichthyes = self.fish_taxonomy.get("Osteichthyes", {})
        actinopterygii = osteichthyes.get("Actinopterygii", {})

        for superorder_name, superorder_data in actinopterygii.items():
            if isinstance(superorder_data, dict):
                for order_name, order_data in superorder_data.items():
                    if isinstance(order_data, dict):
                        for family_name, family_data in order_data.items():
                            if isinstance(family_data, dict):
                                families.append(
                                    ("Osteichthyes", order_name, family_name)
                                )

        return families

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
