#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marine Species Scraper - 통합 메인 메뉴
산호와 해수어를 선택할 수 있는 통합 진입점
"""

import sys
import os
from pathlib import Path

def print_main_menu():
    """메인 메뉴 출력"""
    print("\n" + "="*60)
    print("🌊 Marine Species Image Scraper 🌊")
    print("="*60)
    print("1. 🐠 해수어 이미지 다운로드")
    print("2. 🪸 산호 이미지 다운로드") 
    print("3. ❓ 도움말")
    print("4. 🚪 종료")
    print("="*60)

def run_fish_scraper():
    """해수어 스크래퍼 실행"""
    print("\n🐠 해수어 이미지 스크래퍼를 시작합니다...")
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "marine_fish.main"
        ], cwd=".")
        return result.returncode
    except Exception as e:
        print(f"❌ 해수어 스크래퍼 실행 중 오류: {e}")
        return 1

def run_coral_scraper():
    """산호 스크래퍼 실행"""
    print("\n🪸 산호 이미지 스크래퍼를 시작합니다...")
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "marine_fish.coral_main", "--interactive"
        ], cwd=".")
        return result.returncode
    except Exception as e:
        print(f"❌ 산고 스크래퍼 실행 중 오류: {e}")
        return 1

def show_help():
    """도움말 출력"""
    print("\n📖 도움말")
    print("-" * 40)
    print("🐠 해수어 다운로드:")
    print("  - 다양한 해수어종의 이미지를 다운로드합니다")
    print("  - 종, 속, 과 단위로 검색 가능합니다")
    print("  - 예: Amphiprion ocellaris (흰동가리)")
    print()
    print("🪸 산고 다운로드:")
    print("  - 다양한 산고종의 이미지를 다운로드합니다")
    print("  - Acropora, Montipora 등 주요 속 지원")
    print("  - 예: Acropora millepora")
    print()
    print("⚙️  설정:")
    print("  - config.json 파일에서 다운로드 설정 조정 가능")
    print("  - 이미지 품질, 저장 경로 등 설정")
    print("-" * 40)

def main():
    """메인 함수"""
    print("🌊 Marine Species Image Scraper 시작")
    
    while True:
        try:
            print_main_menu()
            choice = input("\n선택하세요 (1-4): ").strip()
            
            if choice == '1':
                returncode = run_fish_scraper()
                if returncode != 0:
                    print(f"⚠️  해수어 스크래퍼가 오류 코드 {returncode}로 종료되었습니다.")
                input("\n계속하려면 Enter를 누르세요...")
                
            elif choice == '2':
                returncode = run_coral_scraper()
                if returncode != 0:
                    print(f"⚠️  산고 스크래퍼가 오류 코드 {returncode}로 종료되었습니다.")
                input("\n계속하려면 Enter를 누르세요...")
                
            elif choice == '3':
                show_help()
                input("\n계속하려면 Enter를 누르세요...")
                
            elif choice == '4':
                print("\n👋 프로그램을 종료합니다.")
                break
                
            else:
                print("❌ 잘못된 선택입니다. 1-4 중에서 선택해주세요.")
                
        except KeyboardInterrupt:
            print("\n\n👋 사용자가 프로그램을 중단했습니다.")
            break
        except Exception as e:
            print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
            input("계속하려면 Enter를 누르세요...")

if __name__ == "__main__":
    main()
