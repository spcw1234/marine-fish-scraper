#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marine Fish Scraper - Main Entry Point
해양어류 이미지 스크래핑 시스템의 메인 진입점
"""

import sys
import argparse
from pathlib import Path

# 로컬 모듈 임포트
from .config_manager import ConfigManager
from .logger import setup_logging
from .taxonomy_manager import TaxonomyManager


def parse_arguments():
    """명령행 인수 파싱"""
    parser = argparse.ArgumentParser(
        description="Marine Fish Image Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main.py --species "Amphiprion ocellaris" --count 50
  python main.py --family Pomacentridae --count 100
  python main.py --config custom_config.json --resume session_123
        """
    )
        description="Marine Fish Image Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main.py --species "Amphiprion ocellaris" --count 50
  python main.py --family Pomacentridae --count 100
  python main.py --config custom_config.json --resume session_123
        """
    )
    
    # 스크래핑 대상 설정
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument(
        "--species",
        help="특정 종 스크래핑 (예: 'Amphiprion ocellaris')"
    )
    target_group.add_argument(
        "--genus",
        help="특정 속의 모든 종 스크래핑 (예: 'Amphiprion')"
    )
    target_group.add_argument(
        "--family",
        help="특정 과의 모든 종 스크래핑 (예: 'Pomacentridae')"
    )
    target_group.add_argument(
        "--all",
        action="store_true",
        help="모든 종 스크래핑"
    )
    
    # 스크래핑 설정
    parser.add_argument(
        "--count",
        type=int,
        default=20,
        help="종당 다운로드할 이미지 수 (기본값: 20)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="출력 디렉토리 (기본값: config에서 설정)"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="설정 파일 경로 (기본값: config.json)"
    )
    
    # 생물 종류 선택
    parser.add_argument(
        "--type",
        choices=["fish", "coral"],
        default="fish",
        help="스크래핑 대상 (fish: 해수어, coral: 산호) (기본값: fish)"
    )
    parser.add_argument(
        "--variant",
        type=str,
        help="산호 트레이드 네임/변이명 (예: 'Golden Hammer', 'Walt Disney')"
    )
    
    # 세션 관리
    parser.add_argument(
        "--resume",
        type=str,
        help="중단된 세션 ID로 재시작"
    )
    parser.add_argument(
        "--list-sessions",
        action="store_true",
        help="저장된 세션 목록 표시"
    )
    
    # 기타 옵션
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 다운로드 없이 시뮬레이션만 실행"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="상세 로그 출력"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="최소한의 로그만 출력"
    )
    
    return parser.parse_args()


def setup_environment(args):
    """환경 설정"""
    # 로깅 설정 (레벨 결정은 setup_logging 내부 핸들러 기준 사용)
    logger = setup_logging("marine_scraper")
    
    # 설정 파일 로드
    config_path = args.config if args.config else "config.json"
    config = ConfigManager(config_path)
    
    # 출력 디렉토리 설정
    if args.output:
        config.output_dir = args.output
    
    return logger, config


def get_target_species(args, taxonomy_manager):
    """스크래핑 대상 종 목록 생성 (해수어/산고 공통)"""
    if args.species:
        # 특정 종
        parts = args.species.split()
        if len(parts) != 2:
            raise ValueError(
                "종명은 '속명 종명' 형식이어야 합니다 (예: 'Amphiprion ocellaris')"
            )
        genus, species = parts
        species_info = taxonomy_manager.get_species_info(genus, species)
        if not species_info:
            raise ValueError(f"알 수 없는 종: {args.species}")
        return [species_info]
    
    elif args.genus:
        # 특정 속의 모든 종
        species_list = taxonomy_manager.genus_index.get(args.genus, [])
        if not species_list:
            raise ValueError(f"알 수 없는 속: {args.genus}")
        return species_list
    
    elif args.family:
        # 특정 과의 모든 종
        species_list = taxonomy_manager.family_index.get(args.family, [])
        if not species_list:
            raise ValueError(f"알 수 없는 과: {args.family}")
        return species_list
    
    elif args.all:
        # 모든 종
        return taxonomy_manager.get_all_species()
    
    else:
        # 기본값: 종류별 인기 종
        if args.type == "coral":
            popular_species = [
                "Euphyllia ancora",
                "Acropora millepora",
                "Zoanthus sociatus",
                "Sarcophyton glaucum"
            ]
        else:  # fish
            popular_species = [
                "Amphiprion ocellaris",
                "Paracanthurus hepatus",
                "Zebrasoma flavescens",
                "Centropyge bicolor"
            ]
        species_list = []
        for species_name in popular_species:
            genus, species = species_name.split()
            species_info = taxonomy_manager.get_species_info(genus, species)
            if species_info:
                species_list.append(species_info)
    return species_list


def list_saved_sessions(config: ConfigManager):
    """저장된 세션 목록 표시"""
    sessions_dir = Path(config.paths.sessions_dir)
    if not sessions_dir.exists():
        print("저장된 세션이 없습니다.")
        return
    
    session_files = list(sessions_dir.glob("session_*.json"))
    if not session_files:
        print("저장된 세션이 없습니다.")
        return
    
    print(f"\n저장된 세션 목록 ({len(session_files)}개):")
    print("-" * 60)
    
    for session_file in sorted(session_files):
        try:
            import json
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            session_id = session_data.get('session_id', 'Unknown')
            created_at = session_data.get('created_at', 'Unknown')
            total_species = session_data.get('total_species', 0)
            completed_species = session_data.get('completed_species', 0)
            
            status = (
                "완료"
                if completed_species >= total_species
                else f"{completed_species}/{total_species}"
            )
            
            print(f"ID: {session_id}")
            print(f"생성일: {created_at}")
            print(f"진행상황: {status}")
            print("-" * 60)
            
        except Exception as e:
            print(f"세션 파일 읽기 오류: {session_file.name} - {e}")


def print_banner():
    """프로그램 배너 출력"""
    banner = (
        "\n"
        "╔══════════════════════════════════════════════════════════════╗\n"
        "║                                                              ║\n"
        "║    🐠 Marine Scraper v2.0.0 🪸                               ║\n"
        "║    해수어 & 산호 이미지 스크래핑 시스템                           ║\n"
        "║                                                              ║\n"
        "║    • 해수어 (688종) + 산고 (72종) 통합 지원                     ║\n"
        "║    • 산고 변이/트레이드 네임 하위 폴더 지원                       ║\n"
        "║    • 다중 소스 이미지 수집 (FishBase, Google, Reef2Reef, Flickr) ║\n"
        "║    • 원자적 파일 작업으로 손상 방지                              ║\n"
        "║    • 세션 관리 및 중단된 작업 재개                               ║\n"
        "║    • 고급 품질 검증 및 중복 제거                                ║\n"
        "║    • 머신러닝 훈련용 데이터셋 생성                               ║\n"
        "║                                                              ║\n"
        "╚══════════════════════════════════════════════════════════════╝\n"
    )
    print(banner)


def print_main_menu():
    """메인 메뉴 출력"""
    menu = (
        "\n"
        "┌─────────────────────────────────────────────────────────────┐\n"
        "│                        메인 메뉴                              │\n"
        "├─────────────────────────────────────────────────────────────┤\n"
        "│  1. 🐠 해수어 모드                                           │\n"
        "│  2. 🪸 산고 모드                                            │\n"
        "│  3. 중단된 세션 재개                                         │\n"
        "│  4. 훈련용 데이터셋 생성                                      │\n"
        "│  5. 데이터셋 분석 및 통계                                     │\n"
        "│  6. 오토 라벨링 작업공간 설정                                 │\n"
        "│  7. 설정 관리                                               │\n"
        "│  8. 시스템 상태 확인                                         │\n"
        "│  9. 종료                                                    │\n"
        "└─────────────────────────────────────────────────────────────┘\n"
    )
    print(menu)


def ask_yes_no(prompt: str, default: str = 'n') -> bool:
    """y/n 입력을 받아 불리언 반환 (기본값 지원)"""
    default = (default or 'n').lower()
    suffix = ' [Y/n]: ' if default == 'y' else ' [y/N]: '
    ans = input(f"{prompt}{suffix}").strip().lower()
    if ans == '':
        return default == 'y'
    return ans in ('y', 'yes')


def show_family_selection_menu(taxonomy_manager: TaxonomyManager):
    """과 선택 메뉴 표시"""
    families = taxonomy_manager.get_all_families()

    print("\n📋 사용 가능한 과(Family) 목록:")
    print("─" * 60)

    for i, (class_name, order_name, family_name) in enumerate(families, 1):
        print(f"{i:2d}. {family_name}")
        print(f"    └─ {class_name} > {order_name}")
        if i % 5 == 0:
            print()

    try:
        choice = int(input(f"\n과를 선택하세요 (1-{len(families)}): "))
        if 1 <= choice <= len(families):
            return families[choice - 1]
        print("❌ 잘못된 선택입니다.")
        return None
    except ValueError:
        print("❌ 올바른 숫자를 입력해주세요.")
    return None


def show_genus_selection_menu(taxonomy_manager: TaxonomyManager, family_info):
    """속 선택 메뉴 표시"""
    class_name, order_name, family_name = family_info
    species_list = taxonomy_manager.get_species_by_family(
        class_name, order_name, family_name
    )
    
    # 속별로 그룹화
    genera = {}
    for genus, species in species_list:
        if genus not in genera:
            genera[genus] = []
        genera[genus].append(species)
    
    genus_list = list(genera.keys())
    
    print(f"\n📋 {family_name} 과의 속(Genus) 목록:")
    print("─" * 60)
    
    for i, genus in enumerate(genus_list, 1):
        species_count = len(genera[genus])
        print(f"{i:2d}. {genus} ({species_count}종)")
        if i % 8 == 0:
            print()
    
    try:
        choice = int(input(f"\n속을 선택하세요 (1-{len(genus_list)}): "))
        if 1 <= choice <= len(genus_list):
            selected_genus = genus_list[choice - 1]
            return selected_genus, genera[selected_genus]
        print("❌ 잘못된 선택입니다.")
        return None, None
    except ValueError:
        print("❌ 올바른 숫자를 입력해주세요.")
    return None, None


def show_species_selection_menu(
    taxonomy_manager: TaxonomyManager, genus, species_list
):
    """종 선택 메뉴 표시"""
    print(f"\n📋 {genus} 속의 종(Species) 목록:")
    print("─" * 60)
    
    for i, species in enumerate(species_list, 1):
        common_names = taxonomy_manager.get_common_names(genus, species)
        primary_name = common_names[0] if common_names else "Unknown"
        print(f"{i:2d}. {genus} {species}")
        print(f"    └─ {primary_name}")
        if i % 5 == 0:
            print()
    
    try:
        choice = int(input(f"\n종을 선택하세요 (1-{len(species_list)}): "))
        if 1 <= choice <= len(species_list):
            return species_list[choice - 1]
        print("❌ 잘못된 선택입니다.")
        return None
    except ValueError:
        print("❌ 올바른 숫자를 입력해주세요.")
    return None


def interactive_menu():
    """인터랙티브 메뉴 시스템 (해수어/산고 통합)"""
    print_banner()
    
    # 시스템 초기화
    config = ConfigManager()
    setup_logging("marine_scraper", "logs")
    
    print("✅ 시스템 초기화 완료")
    
    while True:
        print_main_menu()
        choice = input("선택하세요 (1-9): ").strip()
        
        if choice == '1':
            # 해수어 모드
            print("\n🐠 해수어 모드 선택됨")
            taxonomy_manager = TaxonomyManager()
            config.output_dir = "dataset"
            scraper_submenu("fish", taxonomy_manager, config)
        
        elif choice == '2':
            # 산고 모드
            print("\n🪸 산고 모드 선택됨")
            from .coral_taxonomy_manager import CoralTaxonomyManager
            taxonomy_manager = CoralTaxonomyManager()
            config.output_dir = "coral_images"
            scraper_submenu("coral", taxonomy_manager, config)
        
        elif choice == '3':
            print("🔄 중단된 세션 재개 기능 (구현 예정)")
        
        elif choice == '4':
            print("📊 훈련용 데이터셋 생성 기능 (구현 예정)")
        
        elif choice == '5':
            print("� 데이터셋 분석 및 통계 기능 (구현 예정)")
        
        elif choice == '6':
            print("🏷️ 오토 라벨링 작업공간 설정 (구현 예정)")
        
        elif choice == '7':
            print("⚙️ 설정 관리 기능 (구현 예정)")
        
        elif choice == '8':
            print("🔍 시스템 상태 확인")
            print("기능 구현 예정")
        
        elif choice == '9':
            print("\n👋 Marine Scraper를 종료합니다.")
            print("🙏 이용해 주셔서 감사합니다!")
            break
        
        else:
            print("❌ 잘못된 선택입니다. 1-9 사이의 숫자를 입력해주세요.")
        
        # 메뉴 선택 후 잠시 대기
        if choice in ['1', '2']:
            input("\n계속하려면 Enter를 누르세요...")


def scraper_submenu(mode: str, taxonomy_manager, config):
    """스크래핑 서브메뉴 (해수어/산고 공통)"""
    mode_name = "해수어" if mode == "fish" else "산고"
    emoji = "🐠" if mode == "fish" else "🪸"
    
    from .marine_scraper import MarineScraper
    scraper = MarineScraper(config, taxonomy_manager)
    
    while True:
        print(f"\n┌─────────────────────────────────────────────────────────────┐")
        print(f"│                    {emoji} {mode_name} 스크래핑 메뉴                    │")
        print(f"├─────────────────────────────────────────────────────────────┤")
        print(f"│  1. 전체 {mode_name} 대량 다운로드                            │")
        print(f"│  2. 특정 과(Family) 선택 다운로드                            │")
        print(f"│  3. 개별 종(Species) 선택 다운로드                           │")
        if mode == "coral":
            print(f"│  4. 인기 관상용 산고 다운로드                                 │")
            print(f"│  5. 변이(Variant) 선택 다운로드                             │")
        print(f"│  0. 메인 메뉴로 돌아가기                                      │")
        print(f"└─────────────────────────────────────────────────────────────┘")
        
        max_choice = 5 if mode == "coral" else 3
        choice = input(f"선택하세요 (0-{max_choice}): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            print(f"\n🚀 전체 {mode_name} 대량 다운로드 시작...")
            print("⚠️ 이 작업은 매우 오래 걸릴 수 있습니다. (수 시간)")
            if ask_yes_no("계속하시겠습니까?", default='n'):
                run_bulk_download(scraper, taxonomy_manager, mode)
        elif choice == '2':
            run_family_download(scraper, taxonomy_manager, mode)
        elif choice == '3':
            run_species_download(scraper, taxonomy_manager, mode)
        elif choice == '4' and mode == "coral":
            run_popular_coral_download(scraper, taxonomy_manager)
        elif choice == '5' and mode == "coral":
            run_variant_download(scraper, taxonomy_manager)
        else:
            print("❌ 잘못된 선택입니다.")


def run_bulk_download(scraper, taxonomy_manager, mode):
    """전체 대량 다운로드"""
    import time
    start_time = time.time()
    all_species = taxonomy_manager.get_all_species()
    total_downloaded = 0
    
    for species_info in all_species:
        print(f"다운로드 중: {species_info.scientific_name}")
        downloaded = scraper.scrape_species(
            species_info.genus, species_info.species,
            [species_info.primary_common_name], 500
        )
        total_downloaded += downloaded
    
    duration = time.time() - start_time
    print(f"\n🎉 스크래핑 완료!")
    print(f"📊 총 다운로드: {total_downloaded}장")
    print(f"⏱️ 소요 시간: {duration/3600:.1f}시간")


def run_family_download(scraper, taxonomy_manager, mode):
    """과별 다운로드"""
    while True:
        print(f"\n🔍 특정 과(Family) 선택 다운로드")
        
        # 과 선택 메뉴 호출
        family_info = show_family_selection_menu(taxonomy_manager)
        if not family_info:
            break
        
        class_name, order_name, family_name = family_info
        print(f"\n🎯 {family_name} 과 다운로드 시작...")
        
        # 해당 과의 모든 종 가져오기
        species_list = taxonomy_manager.get_species_by_family(
            class_name, order_name, family_name
        )
        
        if species_list:
            import time
            start_time = time.time()
            total_downloaded = 0
            
            for genus, species in species_list:
                common_names = taxonomy_manager.get_common_names(genus, species)
                downloaded = scraper.scrape_species(
                    genus, species, common_names, 500
                )
                total_downloaded += downloaded
            
            duration = time.time() - start_time
            print(f"\n🎉 {family_name} 과 스크래핑 완료!")
            print(f"📊 총 다운로드: {total_downloaded}장")
            print(f"⏱️ 소요 시간: {duration/60:.1f}분")
        else:
            print(f"❌ {family_name} 과에서 종을 찾을 수 없습니다.")
        
        if not ask_yes_no("다른 과를 선택하시겠습니까?", default='n'):
            break


def run_species_download(scraper, taxonomy_manager, mode):
    """개별 종 다운로드"""
    while True:
        print("\n🔍 개별 종 선택 다운로드")
        
        # 1단계: 과 선택
        family_info = show_family_selection_menu(taxonomy_manager)
        if not family_info:
            break
        
        # 2단계: 속 선택
        genus, species_list = show_genus_selection_menu(taxonomy_manager, family_info)
        if not genus:
            continue
        
        # 3단계: 종 선택
        selected_species = show_species_selection_menu(taxonomy_manager, genus, species_list)
        if not selected_species:
            continue
        
        # 산고 모드에서 변이 선택 옵션
        variant = None
        if mode == "coral" and hasattr(taxonomy_manager, 'get_variants'):
            variants = taxonomy_manager.get_variants(genus, selected_species)
            if variants:
                print(f"\n🪸 {genus} {selected_species}의 변이를 선택하세요:")
                print("0. 기본형 (변이 없음)")
                for i, variant_name in enumerate(variants, 1):
                    print(f"{i}. {variant_name}")
                
                try:
                    choice = int(input("선택 (0-{}): ".format(len(variants))))
                    if 1 <= choice <= len(variants):
                        variant = variants[choice - 1]
                        print(f"✅ 변이 선택: {variant}")
                except ValueError:
                    print("기본형으로 진행합니다.")
        
        # 다운로드 실행
        common_names = taxonomy_manager.get_common_names(genus, selected_species)
        print(f"\n🎯 {genus} {selected_species} 다운로드 시작...")
        if variant:
            print(f"🎨 변이: {variant}")
        
        import time
        start_time = time.time()
        downloaded = scraper.scrape_species(
            genus, selected_species, common_names, 500, variant
        )
        duration = time.time() - start_time
        
        print(f"\n🎉 {genus} {selected_species} 다운로드 완료!")
        print(f"📊 다운로드: {downloaded}장")
        print(f"⏱️ 소요 시간: {duration/60:.1f}분")
        
        if not ask_yes_no("다른 종을 선택하시겠습니까?", default='n'):
            break


def run_popular_coral_download(scraper, taxonomy_manager):
    """인기 산고 다운로드"""
    print("\n🌟 인기 관상용 산고 다운로드")
    
    # 인기 산고 리스트 (변이 포함)
    popular_corals = [
        ("Euphyllia", "ancora", "Golden Hammer"),
        ("Euphyllia", "ancora", "Toxic Green Hammer"),
        ("Acropora", "tenuis", "Walt Disney"),
        ("Acropora", "tenuis", "Homewrecker"),
        ("Discosoma", "sp", "Jawbreaker"),
        ("Discosoma", "sp", "Panty Dropper"),
        ("Zoanthus", "sp", "Rainbow"),
        ("Palythoa", "sp", "Nuclear Green")
    ]
    
    print("📋 다운로드 예정 산고:")
    for genus, species, variant in popular_corals:
        print(f"  • {genus} {species} - {variant}")
    
    if ask_yes_no("이 산고들을 다운로드하시겠습니까?", default='y'):
        import time
        start_time = time.time()
        total_downloaded = 0
        
        for genus, species, variant in popular_corals:
            print(f"\n다운로드 중: {genus} {species} ({variant})")
            common_names = taxonomy_manager.get_common_names(genus, species)
            downloaded = scraper.scrape_species(
                genus, species, common_names, 200, variant
            )
            total_downloaded += downloaded
        
        duration = time.time() - start_time
        print(f"\n🎉 인기 산고 다운로드 완료!")
        print(f"📊 총 다운로드: {total_downloaded}장")
        print(f"⏱️ 소요 시간: {duration/60:.1f}분")


def run_variant_download(scraper, taxonomy_manager):
    """변이 다운로드"""
    print("\n🎨 변이(Variant) 선택 다운로드")
    
    # 변이가 있는 종들 표시
    if hasattr(taxonomy_manager, 'variants_map'):
        variants_map = taxonomy_manager.variants_map
        print("🪸 변이가 있는 산고 종:")
        
        species_with_variants = []
        for i, (species_key, variants) in enumerate(variants_map.items(), 1):
            genus, species = species_key.split('_', 1)
            variant_names = list(variants.keys())
            print(f"{i}. {genus} {species} ({len(variant_names)}개 변이)")
            species_with_variants.append((genus, species, variant_names))
        
        try:
            choice = int(input(f"종 선택 (1-{len(species_with_variants)}): "))
            if 1 <= choice <= len(species_with_variants):
                genus, species, variant_names = species_with_variants[choice - 1]
                
                print(f"\n🎨 {genus} {species}의 변이 선택:")
                for i, variant in enumerate(variant_names, 1):
                    print(f"{i}. {variant}")
                
                variant_choice = int(input(f"변이 선택 (1-{len(variant_names)}): "))
                if 1 <= variant_choice <= len(variant_names):
                    selected_variant = variant_names[variant_choice - 1]
                    
                    # 다운로드 실행
                    common_names = taxonomy_manager.get_common_names(genus, species)
                    print(f"\n🎯 {genus} {species} ({selected_variant}) 다운로드 시작...")
                    
                    import time
                    start_time = time.time()
                    downloaded = scraper.scrape_species(
                        genus, species, common_names, 300, selected_variant
                    )
                    duration = time.time() - start_time
                    
                    print(f"\n🎉 다운로드 완료!")
                    print(f"📊 다운로드: {downloaded}장")
                    print(f"⏱️ 소요 시간: {duration/60:.1f}분")
        except (ValueError, IndexError):
            print("❌ 잘못된 선택입니다.")
    else:
        print("❌ 변이 정보를 찾을 수 없습니다.")


def main():
    """메인 함수"""
    try:
        # 명령행 인수가 있는지 확인
        if len(sys.argv) == 1:
            # 명령행 인수가 없으면 인터랙티브 메뉴 시스템 사용
            interactive_menu()
            return
        
        # 명령행 인수 파싱
        args = parse_arguments()
        
        # 생물 종류에 따라 분기 처리
        if args.type == "coral":
            # 산호 모드
            from .coral_taxonomy_manager import CoralTaxonomyManager
            taxonomy_manager = CoralTaxonomyManager()
            
            # 출력 디렉토리를 산호용으로 설정
            if not args.output:
                args.output = "coral_images"
        else:
            # 해수어 모드 (기본값)
            taxonomy_manager = TaxonomyManager()
            
            # 출력 디렉토리를 해수어용으로 설정
            if not args.output:
                args.output = "dataset"
        
        # 환경 설정
        logger, config = setup_environment(args)
        
        # 세션 목록 표시 요청
        if args.list_sessions:
            list_saved_sessions(config)
            return
        
        # 스크래핑 대상 결정 (이미 생성된 taxonomy_manager 사용)
        target_species = get_target_species(args, taxonomy_manager)
        
        logger.info(f"🎯 스크래핑 대상: {len(target_species)}종")
        logger.info(f"📥 종당 목표 이미지: {args.count}장")
        
        if args.dry_run:
            logger.info("🔍 DRY RUN 모드 - 실제 다운로드는 수행하지 않습니다")
            for species_info in target_species:
                logger.info(
                    f"  - {species_info.scientific_name} "
                    f"({species_info.primary_common_name})"
                )
            return
        
        # MarineScraper 초기화
        from .marine_scraper import MarineScraper
        scraper = MarineScraper(config, taxonomy_manager)
        
        # 산호 모드에서 variant 지원
        if args.type == "coral" and args.variant:
            logger.info(f"🪸 변이: {args.variant}")
            # 개별 종별로 스크래핑 (variant 지원)
            for species_info in target_species:
                downloaded = scraper.scrape_species(
                    species_info.genus, 
                    species_info.species,
                    [species_info.primary_common_name],
                    args.count,
                    args.variant
                )
                logger.info(f"📥 {species_info.scientific_name} 완료: {downloaded}장")
        else:
            # 기존 세션 방식 (해수어 또는 변이 없는 산호)
            if args.resume:
                logger.info(f"🔄 세션 복원: {args.resume}")
                success = scraper.restore_session(args.resume)
                if not success:
                    logger.error(f"세션 복원 실패: {args.resume}")
                    return
            else:
                # 새 스크래핑 세션 시작
                scraper.start_scraping_session(target_species, args.count)
        
        # 스크래핑 실행
        logger.info("🚀 스크래핑 시작!")
        results = scraper.run_scraping()
        
        # 결과 요약
        logger.info("✅ 스크래핑 완료!")
        logger.info(f"📊 총 다운로드: {results.get('total_downloaded', 0)}장")
        logger.info(f"⏱️  소요 시간: {results.get('duration', 0):.1f}초")
        
        # 통계 출력
        if hasattr(args, 'verbose') and args.verbose:
            stats = scraper.get_statistics()
            logger.info("📈 상세 통계:")
            for key, value in stats.items():
                logger.info(f"  {key}: {value}")
    
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단되었습니다")
        print("💾 진행 상황이 저장되었습니다. 나중에 재개할 수 있습니다.")
        sys.exit(0)
    
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        if len(sys.argv) > 1:
            # 명령행 모드에서만 상세 오류 표시
            import traceback
            print(traceback.format_exc())
        sys.exit(1)

 
if __name__ == "__main__":
    main()
