#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marine Fish Scraper - Main Entry Point
해양어류 이미지 스크래핑 시스템의 메인 진입점
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# 로컬 모듈 임포트
from config_manager import ConfigManager
from logger import get_logger, setup_logging
from taxonomy_manager import TaxonomyManager

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
    # 로깅 설정
    log_level = "DEBUG" if args.verbose else "WARNING" if args.quiet else "INFO"
    logger = setup_logging("marine_scraper")
    
    # 설정 파일 로드
    config_path = args.config if args.config else "config.json"
    config = ConfigManager(config_path)
    
    # 출력 디렉토리 설정
    if args.output:
        config.paths.output_dir = args.output
    
    return logger, config

def get_target_species(args, taxonomy_manager: TaxonomyManager):
    """스크래핑 대상 종 목록 생성"""
    if args.species:
        # 특정 종
        parts = args.species.split()
        if len(parts) != 2:
            raise ValueError("종명은 '속명 종명' 형식이어야 합니다 (예: 'Amphiprion ocellaris')")
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
        # 기본값: 인기 있는 관상어 몇 종
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
            
            status = "완료" if completed_species >= total_species else f"{completed_species}/{total_species}"
            
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
        "║    🐠 Stable Marine Fish Scraper v1.0.0                     ║\n"
        "║    안정적인 관상용 해수어 이미지 스크래핑 시스템                    ║\n"
        "║                                                              ║\n"
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
        "│  1. 전체 이미지 대량 다운로드 (종당 1000장 목표)                │\n"
        "│  2. 특정 과(Family) 선택 다운로드                            │\n"
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

def interactive_menu():
    """인터랙티브 메뉴 시스템"""
    print_banner()
    
    # 시스템 초기화
    config = ConfigManager()
    logger = setup_logging("marine_scraper", "logs")
    
    print("✅ 시스템 초기화 완료")
    
    # 분류 체계 로드
    taxonomy_manager = TaxonomyManager()
    
    # MarineScraper 초기화
    from marine_scraper import MarineScraper
    scraper = MarineScraper(config)
    
    while True:
        print_main_menu()
        choice = input("선택하세요 (1-9): ").strip()
        
        if choice == '1':
            print("\n🚀 전체 이미지 대량 다운로드 시작...")
            print("⚠️ 이 작업은 매우 오래 걸릴 수 있습니다. (수 시간 ~ 수 일)")
            if ask_yes_no("계속하시겠습니까?", default='n'):
                import time
                start_time = time.time()
                scraper.scrape_all_fish()
                duration = time.time() - start_time
                print(f"\n🎉 스크래핑 완료!")
                print(f"⏱️ 소요 시간: {duration/3600:.1f}시간")
            else:
                print("❌ 취소되었습니다.")
        
        elif choice == '2':
            while True:
                family_info = show_family_selection_menu(taxonomy_manager)
                if not family_info:
                    break
                class_name, order_name, family_name = family_info
                print(f"\n🎯 {family_name} 과 다운로드 시작...")
                
                # 해당 과의 모든 종 가져오기
                species_list = taxonomy_manager.get_species_by_family(class_name, order_name, family_name)
                
                if species_list:
                    import time
                    start_time = time.time()
                    total_downloaded = 0
                    
                    for genus, species in species_list:
                        common_names = taxonomy_manager.get_common_names(genus, species)
                        downloaded = scraper.scrape_species(genus, species, common_names, 100)
                        total_downloaded += downloaded
                    
                    duration = time.time() - start_time
                    print(f"\n🎉 {family_name} 과 스크래핑 완료!")
                    print(f"📊 총 다운로드: {total_downloaded}장")
                    print(f"⏱️ 소요 시간: {duration/60:.1f}분")
                else:
                    print(f"❌ {family_name} 과에서 종을 찾을 수 없습니다.")
                
                if not ask_yes_no("다른 과를 선택하시겠습니까?", default='n'):
                    break
        
        elif choice == '3':
            print("\n🔄 세션 관리 기능은 아직 구현 중입니다.")
            print("현재는 기본 스크래핑만 지원됩니다.")
        
        elif choice == '4':
            try:
                images_per_class = input("클래스당 이미지 수를 입력하세요 (기본값: 100): ").strip()
                if images_per_class:
                    images_per_class = int(images_per_class)
                else:
                    images_per_class = 100
                if images_per_class <= 0:
                    print("❌ 양수를 입력해주세요.")
                else:
                    print(f"\n🎯 훈련용 데이터셋 생성 중 (클래스당 {images_per_class}장)...")
                    scraper.create_training_dataset(images_per_class)
                    print("✅ 훈련용 데이터셋 생성 완료!")
            except ValueError:
                print("❌ 올바른 숫자를 입력해주세요.")
        
        elif choice == '5':
            print("\n📊 데이터셋 분석 중...")
            scraper.analyze_dataset()
        
        elif choice == '6':
            print("\n🏷️ 오토 라벨링 작업공간 설정 기능은 아직 구현 중입니다.")
        
        elif choice == '7':
            print("\n⚙️ 설정 관리 기능은 아직 구현 중입니다.")
        
        elif choice == '8':
            print("\n🔍 시스템 상태 확인 중...")
            stats = taxonomy_manager.get_taxonomy_statistics()
            print("\n📊 분류 체계 통계:")
            print(f"  총 종 수: {stats.get('total_species', 0)}")
            print(f"  총 속 수: {stats.get('total_genera', 0)}")
            print(f"  총 과 수: {stats.get('total_families', 0)}")
            print(f"  총 강 수: {stats.get('total_classes', 0)}")
        
        elif choice == '9':
            print("\n👋 프로그램을 종료합니다.")
            print("🧹 리소스 정리 중...")
            break
        
        else:
            print("❌ 잘못된 선택입니다. 1-9 중에서 선택해주세요.")
        
        input("\n계속하려면 엔터를 누르세요...")

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
        
        # 환경 설정
        logger, config = setup_environment(args)
        
        # 세션 목록 표시 요청
        if args.list_sessions:
            list_saved_sessions(config)
            return
        
        # 분류 체계 로드
        taxonomy_manager = TaxonomyManager()
        
        # 스크래핑 대상 결정
        target_species = get_target_species(args, taxonomy_manager)
        
        logger.info(f"🎯 스크래핑 대상: {len(target_species)}종")
        logger.info(f"📥 종당 목표 이미지: {args.count}장")
        
        if args.dry_run:
            logger.info("🔍 DRY RUN 모드 - 실제 다운로드는 수행하지 않습니다")
            for species_info in target_species:
                logger.info(f"  - {species_info.scientific_name} ({species_info.primary_common_name})")
            return
        
        # MarineScraper 초기화
        from marine_scraper import MarineScraper
        scraper = MarineScraper(config)
        
        # 세션 복원 또는 새 세션 시작
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