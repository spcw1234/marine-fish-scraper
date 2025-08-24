#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marine Fish Scraper - 메인 진입점
"""

if __name__ == "__main__":
    import subprocess
    import sys
    
    # marine_fish 디렉토리에서 main.py 실행
    result = subprocess.run([sys.executable, "marine_fish/main.py"], 
                          cwd=".", 
                          capture_output=False)
    sys.exit(result.returncode)
