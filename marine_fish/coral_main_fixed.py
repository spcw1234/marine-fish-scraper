#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coral Image Scraper - Main Entry Point
산호 이미지 스크래핑 시스템의 메인 진입점
"""

import sys
import argparse
from pathlib import Path

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
    """메인 메뉴 출력"""
    print("\n" + "="*60)
    print("🐠 Coral Image Scraper - 산호 이미지 수집 시스템")
    print("="*60)
    print("1. 🚀 전체 산호 대량 다운로드")
    print("2. 🎯 특정 과(Family) 선택 다운로드")
    print("3. 🔍 특정 종(Species) 검색 및 다운로드")
    print("4. 📊 다운로드 통계 보기")
    print("5. 🗂️ 세션 관리")
    print("6. ⚙️ 설정 변경")
    print("7. 🧹 캐시 정리")
    print("8. 📝 로그 보기")
    print("9. ❓ 도움말")
    print("10. 🚪 종료")
    print("="*60)


def print_family_menu():
    """과(Family) 선택 메뉴 출력"""
    print("\n📚 산호 과(Family) 목록:")
    print("-" * 40)
    families = [
        "Acroporidae",
        "Faviidae", 
        "Fungiidae",
        "Pocilloporidae",
        "Poritidae",
        "Dendrophylliidae",
        "Euphylliidae",
        "Merulinidae",
        "Lobophylliidae",
        "Caryophylliidae"
    ]
    
    for i, family in enumerate(families, 1):
        print(f"{i:2d}. {family}")
    
    print(f"{len(families)+1:2d}. 🔙 이전 메뉴로")
    return families


def show_species_selection_menu(taxonomy_manager: CoralTaxonomyManager, 
                               family: str):
    """특정 과의 종 선택 메뉴"""
    species_list = taxonomy_manager.get_species_by_family(family)
    
    if not species_list:
        print(f"❌ {family}에서 종을 찾을 수 없습니다.")
        return None
    
    print(f"\n🔍 {family} 과의 종 목록:")
    print("-" * 50)
    
    for i, species in enumerate(species_list[:20], 1):  # 최대 20개만 표시
        genus_species = f"{species.genus} {species.species}"
        print(f"{i:2d}. {genus_species}")
        if species.common_names:
            print(f"     → {', '.join(species.common_names[:2])}")
    
    if len(species_list) > 20:
        print(f"    ... 및 {len(species_list) - 20}개 추가 종")
    
    print(f"{min(len(species_list), 20)+1:2d}. 🌊 전체 과 다운로드")
    print(f"{min(len(species_list), 20)+2:2d}. 🔙 이전 메뉴로")
    
    return species_list


def interactive_mode():
    """대화형 모드 실행"""
    print("🎉 Coral Image Scraper 시작!")
    print("📋 설정 파일 로드 중...")
    
    # 설정 로드
    config = ConfigManager()
    
    # 로깅 설정
    print("📝 로깅 시스템 초기화 중...")
    setup_logging(config.get('logging', {}))
    
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
            print("\n🚀 전체 산호 대량 다운로드 시작...")
            # 모든 산호 종 다운로드
            all_species = taxonomy_manager.get_all_species()
            print(f"📊 총 {len(all_species)}종의 산호 이미지를 다운로드합니다.")
            
            confirm = input("계속하시겠습니까? (y/N): ").strip().lower()
            if confirm == 'y':
                for species in all_species:
                    genus_species = f"{species.genus} {species.species}"
                    print(f"🔄 {genus_species} 다운로드 중...")
                    scraper.download_species(genus_species, 
                                           count=config.get('download.images_per_species', 50))
            
        elif choice == '2':
            print("\n🎯 과(Family) 선택 다운로드")
            families = print_family_menu()
            
            try:
                family_choice = int(input("과를 선택하세요: ").strip())
                if 1 <= family_choice <= len(families):
                    selected_family = families[family_choice - 1]
                    print(f"📋 {selected_family} 선택됨")
                    
                    species_list = show_species_selection_menu(taxonomy_manager, selected_family)
                    if species_list:
                        try:
                            species_choice = int(input("종을 선택하세요: ").strip())
                            if 1 <= species_choice <= min(len(species_list), 20):
                                selected_species = species_list[species_choice - 1]
                                genus_species = f"{selected_species.genus} {selected_species.species}"
                                print(f"🎯 {genus_species} 다운로드 시작...")
                                scraper.download_species(genus_species)
                            elif species_choice == min(len(species_list), 20) + 1:
                                # 전체 과 다운로드
                                print(f"🌊 {selected_family} 전체 다운로드 시작...")
                                for species in species_list:
                                    genus_species = f"{species.genus} {species.species}"
                                    scraper.download_species(genus_species)
                        except ValueError:
                            print("❌ 올바른 번호를 입력하세요.")
                elif family_choice == len(families) + 1:
                    continue
                else:
                    print("❌ 올바른 번호를 입력하세요.")
            except ValueError:
                print("❌ 올바른 번호를 입력하세요.")
        
        elif choice == '3':
            print("\n🔍 특정 종 검색 및 다운로드")
            search_term = input("검색할 종명을 입력하세요 (예: Acropora): ").strip()
            
            if search_term:
                results = taxonomy_manager.search_species(search_term)
                if results:
                    print(f"\n🎯 '{search_term}' 검색 결과 ({len(results)}개):")
                    print("-" * 50)
                    
                    for i, species in enumerate(results[:10], 1):  # 최대 10개 표시
                        genus_species = f"{species.genus} {species.species}"
                        print(f"{i:2d}. {genus_species}")
                        if species.common_names:
                            print(f"     → {', '.join(species.common_names[:2])}")
                    
                    try:
                        choice_idx = int(input("다운로드할 종을 선택하세요: ").strip())
                        if 1 <= choice_idx <= min(len(results), 10):
                            selected = results[choice_idx - 1]
                            genus_species = f"{selected.genus} {selected.species}"
                            print(f"🎯 {genus_species} 다운로드 시작...")
                            scraper.download_species(genus_species)
                        else:
                            print("❌ 올바른 번호를 입력하세요.")
                    except ValueError:
                        print("❌ 올바른 번호를 입력하세요.")
                else:
                    print(f"❌ '{search_term}'과 일치하는 종을 찾을 수 없습니다.")
        
        elif choice == '4':
            print("\n📊 다운로드 통계")
            stats = scraper.get_download_stats()
            print(f"총 다운로드 세션: {stats.get('total_sessions', 0)}")
            print(f"총 다운로드 이미지: {stats.get('total_images', 0)}")
            print(f"성공률: {stats.get('success_rate', 0):.1f}%")
        
        elif choice == '5':
            print("\n🗂️ 세션 관리")
            sessions = scraper.get_active_sessions()
            if sessions:
                print("활성 세션 목록:")
                for i, session in enumerate(sessions, 1):
                    print(f"{i}. {session}")
            else:
                print("활성 세션이 없습니다.")
        
        elif choice == '6':
            print("\n⚙️ 설정 변경")
            print("현재 설정:")
            print(f"- 종당 이미지 수: {config.get('download.images_per_species', 50)}")
            print(f"- 출력 디렉토리: {config.get('download.output_directory', './dataset')}")
            
        elif choice == '7':
            print("\n🧹 캐시 정리")
            scraper.clear_cache()
            print("✅ 캐시가 정리되었습니다.")
        
        elif choice == '8':
            print("\n📝 최근 로그")
            # 로그 표시 로직
            
        elif choice == '9':
            print("\n❓ 도움말")
            print("이 프로그램은 산호 이미지를 자동으로 수집합니다.")
            print("각 메뉴를 선택하여 원하는 작업을 수행하세요.")
            
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
    
    # 로깅 설정
    log_config = config.get('logging', {})
    if args.verbose:
        log_config['level'] = 'DEBUG'
    setup_logging(log_config)
    
    # 산호 분류 체계 로드
    taxonomy_manager = CoralTaxonomyManager()
    
    # MarineScraper 초기화
    from .marine_scraper import MarineScraper
    scraper = MarineScraper(config, taxonomy_manager)
    
    # 출력 디렉토리 설정 (명령행 인수가 우선)
    if args.output_dir:
        config.set('download.output_directory', args.output_dir)
    
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
        species_list = taxonomy_manager.get_species_by_family(args.family)
        
        if species_list:
            print(f"📊 {args.family}에서 {len(species_list)}종 발견")
            
            if args.dry_run:
                for species in species_list:
                    genus_species = f"{species.genus} {species.species}"
                    print(f"[DRY RUN] {genus_species} - {args.count}개 이미지")
            else:
                for species in species_list:
                    genus_species = f"{species.genus} {species.species}"
                    print(f"🔄 {genus_species} 다운로드 중...")
                    scraper.download_species(genus_species, count=args.count)
        else:
            print(f"❌ {args.family}에서 종을 찾을 수 없습니다.")
    
    else:
        # 인수가 없으면 대화형 모드로 실행
        interactive_mode()


if __name__ == "__main__":
    main()
