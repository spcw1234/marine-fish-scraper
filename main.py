#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marine Fish Scraper - 메인 진입점
"""

import sys
from pathlib import Path

# marine_fish 폴더를 Python 경로에 추가
marine_fish_dir = Path(__file__).parent / "marine_fish"
sys.path.insert(0, str(marine_fish_dir))

# marine_fish의 main 실행
if __name__ == "__main__":
    from main import main

    main()
