#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coral Image Scraper - Main Entry Point
산호 이미지 스크래핑 시스템의 메인 진입점
"""

import argparse
from typing import List, Dict

# 로컬 모듈 임포트 (상대 임포트로 변경)
from .config_manager import ConfigManager
from .logger import setup_logging
from .coral_taxonomy_manager import CoralTaxonomyManager


def parse_arguments():
    """명령행 인수 파싱"""
    parser = argparse.ArgumentParser(
        description="Coral Image Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python coral_main.py --species "Acropora millepora" --count 50
  python coral_main.py --family Acroporidae --count 100
  python coral_main.py --config custom_config.json --resume session_123
        """
    )
    
    parser.add_argument('--species', type=str,
                        help='다운로드할 특정 종 (예: "Acropora millepora")')
    parser.add_argument('--family', type=str,
                        help='다운로드할 산호 과 (예: "Acroporidae")')
    parser.add_argument('--count', type=int, default=50,
                        help='각 종마다 다운로드할 이미지 수 (기본값: 50)')
    parser.add_argument('--config', type=str, default='config.json',
                        help='설정 파일 경로 (기본값: config.json)')
    parser.add_argument('--output-dir', type=str,
                        help='이미지 저장 디렉토리 (설정 파일보다 우선)')
    parser.add_argument('--resume', type=str,
                        help='재개할 세션 ID')
    parser.add_argument('--dry-run', action='store_true',
                        help='실제 다운로드 없이 실행 계획만 출력')
    parser.add_argument('--verbose', action='store_true',
                        help='상세 로그 출력')
    parser.add_argument('--interactive', action='store_true',
                        help='대화형 모드로 실행')
    
    return parser.parse_args()


def print_main_menu():
    """메인 메뉴 출력 (해수어와 동일 레이아웃)"""
    menu = (
        "\n"
        "┌─────────────────────────────────────────────────────────────┐\n"
        "│                        산호 메인 메뉴                          │\n"
        "├─────────────────────────────────────────────────────────────┤\n"
        "│  1. 전체 이미지 대량 다운로드 (종당 1000장)                    │\n"
        "│  2. 특정 과(Family) 선택 다운로드                            │\n"
        "│  3. 개별 종(Species) 선택 다운로드                           │\n"
        "│  4. 중단된 세션 재개                                         │\n"
        "│  5. 훈련용 데이터셋 생성 (종별 50장 샘플)                     │\n"
        "│  6. 데이터셋 분석 및 통계                                     │\n"
        "│  7. 오토 라벨링 작업공간 설정                                 │\n"
        "│  8. 설정 관리                                               │\n"
        "│  9. 시스템 상태 확인                                         │\n"
        "│  10. 종료                                                   │\n"
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


def show_family_selection_menu(taxonomy_manager: CoralTaxonomyManager):
    """과 선택 메뉴 (TaxonomyManager 기반)"""
    families = taxonomy_manager.get_all_families()

    print("\n📚 산호 과(Family) 목록:")
    print("-" * 60)

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


def show_genus_selection_menu(
    taxonomy_manager: CoralTaxonomyManager,
    family_info,
):
    """속 선택 메뉴"""
    class_name, order_name, family_name = family_info
    species_pairs = taxonomy_manager.get_species_by_family(
        class_name,
        order_name,
        family_name,
    )  # List[Tuple[genus, species]]

    # 속별 그룹화
    genera: Dict[str, List[str]] = {}
    for genus, species in species_pairs:
        genera.setdefault(genus, []).append(species)

    genus_list = list(genera.keys())

    print(f"\n📚 {family_name} 과의 속(Genus) 목록:")
    print("-" * 60)
    for i, genus in enumerate(genus_list, 1):
        print(f"{i:2d}. {genus} ({len(genera[genus])}종)")
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
    taxonomy_manager: CoralTaxonomyManager,
    genus: str,
    species_list: List[str],
):
    """종 선택 메뉴"""
    print(f"\n📋 {genus} 속의 종(Species) 목록:")
    print("-" * 60)

    for i, species in enumerate(species_list, 1):
        common_names = taxonomy_manager.get_common_names(genus, species)
        primary = common_names[0] if common_names else "Unknown"
        print(f"{i:2d}. {genus} {species}")
        print(f"    └─ {primary}")
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


def interactive_mode():
    """대화형 모드 실행"""
    print("🎉 Coral Image Scraper 시작!")
    print("📋 설정 파일 로드 중...")
    
    # 설정 로드
    config = ConfigManager()
    
    # 로깅 설정
    print("📝 로깅 시스템 초기화 중...")
    # ConfigManager는 dict가 아니므로 단순 이름 기반 초기화
    setup_logging("coral_scraper")
    
    print("✅ 시스템 초기화 완료")
    
    # 산호 분류 체계 로드
    print("📚 산호 분류 체계 로드 중...")
    taxonomy_manager = CoralTaxonomyManager()
    
    # MarineScraper 초기화 (산호용으로 재사용)
    from .marine_scraper import MarineScraper
    scraper = MarineScraper(config, taxonomy_manager)
    
    while True:
        print_main_menu()
        choice = input("선택하세요 (1-10): ").strip()

        if choice == '1':
            print("\n🚀 전체 이미지 대량 다운로드 시작...")
            print("⚠️ 오래 걸릴 수 있습니다.")
            if ask_yes_no("계속하시겠습니까?", default='n'):
                all_species = taxonomy_manager.get_all_species()
                images_per_species = 1000
                for s in all_species:
                    genus_species = f"{s.genus} {s.species}"
                    scraper.download_species(
                        genus_species,
                        count=images_per_species,
                    )
            else:
                print("❌ 취소되었습니다.")

        elif choice == '2':
            while True:
                family_info = show_family_selection_menu(taxonomy_manager)
                if not family_info:
                    break
                class_name, order_name, family_name = family_info
                print(f"\n🎯 {family_name} 과 다운로드 시작...")
                pairs = taxonomy_manager.get_species_by_family(
                    class_name, order_name, family_name
                )
                if not pairs:
                    print("❌ 종을 찾을 수 없습니다.")
                    continue
                total = 0
                for genus, species in pairs:
                    genus_species = f"{genus} {species}"
                    total += scraper.download_species(
                        genus_species,
                        count=50,
                    )
                print(f"✅ 완료: 총 {total}장")
                if not ask_yes_no("다른 과를 선택하시겠습니까?", default='n'):
                    break

        elif choice == '3':
            while True:
                family_info = show_family_selection_menu(taxonomy_manager)
                if not family_info:
                    break
                genus, species_list = show_genus_selection_menu(
                    taxonomy_manager, family_info
                )
                if not genus:
                    continue
                selected_species = show_species_selection_menu(
                    taxonomy_manager, genus, species_list
                )
                if not selected_species:
                    continue
                print(
                    f"\n🎯 {genus} {selected_species} 다운로드 시작..."
                )
                genus_species = f"{genus} {selected_species}"
                scraper.download_species(
                    genus_species,
                    count=50,
                )
                if not ask_yes_no("다른 종을 선택하시겠습니까?", default='n'):
                    break

        elif choice == '4':
            print("\n🔄 세션 관리 기능은 아직 구현 중입니다.")

        elif choice == '5':
            print("\n🎯 훈련용 데이터셋 생성: 종별 최대 50장 샘플링")
            try:
                per_species = 50
                from pathlib import Path as _P
                import random
                import shutil
                dataset_root = (
                    scraper.dataset_dir
                    if hasattr(scraper, 'dataset_dir')
                    else _P('dataset')
                )
                if not dataset_root.exists():
                    print("❌ dataset 폴더가 없습니다.")
                else:
                    train_root = _P('train')
                    train_root.mkdir(exist_ok=True)
                    copied = 0
                    species_count = 0
                    for class_dir in dataset_root.iterdir():
                        if not class_dir.is_dir():
                            continue
                        for species_dir in class_dir.rglob('*'):
                            if not species_dir.is_dir():
                                continue
                            name = species_dir.name
                            if '_' not in name:
                                continue
                            images = [
                                p
                                for p in species_dir.iterdir()
                                if p.suffix.lower() in (
                                    '.jpg', '.jpeg', '.png'
                                )
                            ]
                            if not images:
                                continue
                            species_count += 1
                            take = min(per_species, len(images))
                            for img in random.sample(images, take):
                                out_dir = train_root / name
                                out_dir.mkdir(parents=True, exist_ok=True)
                                dst = out_dir / img.name
                                try:
                                    if not dst.exists():
                                        shutil.copy2(img, dst)
                                        copied += 1
                                except Exception as ce:
                                    print(f"⚠️ 복사 실패: {img} - {ce}")
                    print(
                        f"✅ 완료: {species_count}개 종에서 "
                        f"{copied}개 이미지 샘플링 → train/"
                    )
            except Exception as e:
                print(f"❌ 생성 실패: {e}")

        elif choice == '6':
            print("\n📈 데이터셋 분석 기능은 아직 구현 중입니다.")

        elif choice == '7':
            print("\n🏷️ 오토 라벨링 작업공간 설정 기능은 아직 구현 중입니다.")

        elif choice == '8':
            print("\n⚙️ 설정 관리 기능은 아직 구현 중입니다.")

        elif choice == '9':
            print("\n🔍 시스템 상태 확인 중...")
            try:
                species = taxonomy_manager.get_all_species()
                species_count = len(species)
                genera = {s.genus for s in species}
                families = taxonomy_manager.get_all_families()
                print("\n📊 분류 체계 통계:")
                print(f"  총 종 수: {species_count}")
                print(f"  총 속 수: {len(genera)}")
                print(f"  총 과 수: {len(families)}")
            except Exception as e:
                print(f"⚠️ 상태 확인 실패: {e}")

        elif choice == '10':
            print("\n👋 프로그램을 종료합니다.")
            break

        else:
            print("❌ 올바른 번호를 입력하세요 (1-10).")


def main():
    """메인 함수"""
    args = parse_arguments()
    
    if args.interactive:
        interactive_mode()
        return
    
    # 설정 로드
    config = ConfigManager(args.config)
    
    # 로깅 설정 (간단 초기화)
    setup_logging("coral_scraper")
    
    # 산호 분류 체계 로드
    taxonomy_manager = CoralTaxonomyManager()
    
    # MarineScraper 초기화
    from .marine_scraper import MarineScraper
    scraper = MarineScraper(config, taxonomy_manager)
    
    # 출력 디렉토리 설정은 현재 스크래퍼 내부 기본값(./dataset)을 사용합니다.
    # args.output_dir는 현재 버전에서 직접 반영되지 않습니다.
    
    # 세션 재개
    if args.resume:
        print(f"🔄 세션 {args.resume} 재개 중...")
        scraper.resume_session(args.resume)
    
    # 다운로드 실행
    if args.species:
        print(f"🎯 특정 종 다운로드: {args.species}")
        if args.dry_run:
            print(f"[DRY RUN] {args.species} - {args.count}개 이미지")
        else:
            scraper.download_species(args.species, count=args.count)
            
    elif args.family:
        print(f"🌊 과 단위 다운로드: {args.family}")
        # 해수어와 동일하게 family_index 활용
        species_infos = taxonomy_manager.family_index.get(args.family, [])
        if species_infos:
            print(f"📊 {args.family}에서 {len(species_infos)}종 발견")
            if args.dry_run:
                for s in species_infos:
                    print(
                        f"[DRY RUN] {s.genus} {s.species} - "
                        f"{args.count}개 이미지"
                    )
            else:
                for s in species_infos:
                    print(
                        f"🔄 {s.genus} {s.species} 다운로드 중..."
                    )
                    scraper.download_species(
                        f"{s.genus} {s.species}",
                        count=args.count,
                    )
        else:
            print(f"❌ {args.family}에서 종을 찾을 수 없습니다.")
    
    else:
        # 인수가 없으면 대화형 모드로 실행
        interactive_mode()


if __name__ == "__main__":
    main()
