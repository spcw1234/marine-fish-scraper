#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marine Fish Scraper - 메인 진입점
"""

if __name__ == "__main__":
    import subprocess
    import sys

    # 패키지 모듈 형태로 실행하여 상대 임포트 문제 방지
    # 전달된 추가 인수는 그대로 marine_fish.main 으로 전달
    args = [sys.executable, "-m", "marine_fish.main", *sys.argv[1:]]
    result = subprocess.run(args, cwd=".")
    sys.exit(result.returncode)
