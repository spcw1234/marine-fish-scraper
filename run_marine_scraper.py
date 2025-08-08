#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marine Fish Scraper - 메인 실행 스크립트
해양어류 이미지 스크래핑 시스템
"""

import sys
import os
from pathlib import Path

def main():
    """메인 실행 함수"""
    print("🐠 Marine Fish Scraper 시작")
    print("=" * 50)
    
    # marine_fish 폴더를 Python 경로에 추가
    marine_fish_dir = Path(__file__).parent / "marine_fish"
    
    if not marine_fish_dir.exists():
        print("❌ marine_fish 폴더를 찾을 수 없습니다!")
        print(f"현재 위치: {Path.cwd()}")
        print(f"찾는 위치: {marine_fish_dir}")
        return 1
    
    sys.path.insert(0, str(marine_fish_dir))
    
    try:
        # marine_fish의 main 모듈 실행
        from main import main as marine_main
        marine_main()
        return 0
        
    except ImportError as e:
        print(f"❌ 모듈 임포트 오류: {e}")
        print("marine_fish 폴더의 파일들을 확인해주세요.")
        return 1
        
    except Exception as e:
        print(f"❌ 실행 중 오류: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)