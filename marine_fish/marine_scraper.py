#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 관상용 해수어 이미지 스크래핑 프로그램
Simple Marine Fish Image Scraper
"""

import os
import requests
import time
import json
import random
import shutil
import re
import hashlib
from pathlib import Path
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime


class MarineScraper:
    """간단한 해수어 스크래퍼"""
    
    def __init__(self, config=None, taxonomy_manager=None):
        self.base_dir = Path(".")
        self.dataset_dir = self.base_dir / "dataset"
        self.train_dir = self.base_dir / "train"
        
        # 디렉토리 생성
        self.dataset_dir.mkdir(exist_ok=True)
        self.train_dir.mkdir(exist_ok=True)
        
        # TaxonomyManager 추가
        if taxonomy_manager:
            self.taxonomy_manager = taxonomy_manager
        else:
            from .taxonomy_manager import TaxonomyManager
            self.taxonomy_manager = TaxonomyManager()
        
        # HTTP 세션
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 설정 저장
        self.config = config
        
        # 품질 통계 추가
        self.quality_stats = {
            'total_checked': 0,
            'quality_passed': 0,
            'quality_failed': 0,
            'blur_rejected': 0,
            'brightness_rejected': 0,
            'contrast_rejected': 0,
            'noise_rejected': 0,
            'resolution_rejected': 0
        }
        
        # 해수어 분류 (간단한 버전)
        self.fish_taxonomy = {
            "연골어류": {
                "상어류": {
                    "Chiloscyllium": {
                        "punctatum": ["Brownbanded bamboo shark", "갈색줄무늬 대나무상어"]
                    }
                }
            },
            "경골어류": {
                "가시고등어목": {
                    "Paracanthurus": {
                        "hepatus": ["Blue tang", "블루탱", "도리"]
                    },
                    "Zebrasoma": {
                        "flavescens": ["Yellow tang", "옐로우탱"],
                        "xanthurum": ["Purple tang", "퍼플탱"]
                    },
                    "Centropyge": {
                        "bicolor": ["Bicolor angelfish", "바이컬러 엔젤"],
                        "loricula": ["Flame angelfish", "플레임 엔젤"]
                    },
                    "Amphiprion": {
                        "ocellaris": ["Ocellaris clownfish", "오셀라리스 클라운", "니모"],
                        "percula": ["Percula clownfish", "퍼큘라 클라운"],
                        "clarkii": ["Clark's anemonefish", "클락스 클라운"]
                    },
                    "Chaetodon": {
                        "auriga": ["Threadfin butterflyfish", "실지느러미 나비고기"],
                        "lunula": ["Raccoon butterflyfish", "라쿤 나비고기"]
                    }
                },
                "복어목": {
                    "Arothron": {
                        "nigropunctatus": ["Blackspotted puffer", "검은점 복어"],
                        "meleagris": ["Guineafowl puffer", "기니파울 복어"]
                    },
                    "Rhinecanthus": {
                        "aculeatus": ["Lagoon triggerfish", "라군 트리거"],
                        "rectangulus": ["Wedgetail triggerfish", "웨지테일 트리거"]
                    }
                }
            }
        }
        
        # 통계
        self.stats = {
            'total_downloaded': 0,
            'total_errors': 0
        }
    
    def download_image(self, url, save_path):
        """이미지 다운로드 및 품질 검증 (완화된 기준)"""
        try:
            # 타임아웃 증가 및 더 관대한 헤더
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = self.session.get(url, timeout=25, stream=True, headers=headers)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                # Content-Type 검증 완화 (이미지가 아니어도 URL에 이미지 확장자가 있으면 허용)
                is_image_content = ('image' in content_type or 
                                  any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']))
                
                if is_image_content:
                    # 임시 파일에 먼저 다운로드
                    temp_path = save_path.with_suffix('.tmp')
                    
                    try:
                        with open(temp_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        
                        # 파일 크기 체크 (너무 작으면 스킵)
                        if temp_path.stat().st_size < 3000:  # 3KB 미만
                            temp_path.unlink()
                            return False
                        
                        # 간단한 품질 검증만 수행 (더 관대하게)
                        if self.simple_quality_check(temp_path):
                            # 품질이 좋으면 최종 파일로 이동
                            temp_path.rename(save_path)
                            return True
                        else:
                            # 품질이 나쁘면 임시 파일 삭제
                            temp_path.unlink()
                            return False
                            
                    except Exception as e:
                        if temp_path.exists():
                            temp_path.unlink()
                        return False
                        
            return False
            
        except Exception as e:
            # 에러 로그를 줄임 (너무 많은 로그 방지)
            if "timeout" not in str(e).lower():
                print(f"다운로드 실패: {url[:50]}... - {e}")
            return False

    def simple_quality_check(self, image_path):
        """간단하고 관대한 품질 검증"""
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                width, height = img.size
                
                # 매우 관대한 기준
                # 1. 최소 해상도: 100x100
                if width < 100 or height < 100:
                    return False
                
                # 2. 종횡비: 매우 관대하게 (0.1 ~ 10.0)
                aspect_ratio = width / height
                if aspect_ratio < 0.1 or aspect_ratio > 10.0:
                    return False
                
                # 3. 이미지 모드 체크 (RGB, RGBA, L 등 허용)
                if img.mode not in ['RGB', 'RGBA', 'L', 'P']:
                    return False
                
                return True
                
        except Exception:
            # PIL로 열 수 없으면 OpenCV 시도
            try:
                import cv2
                img = cv2.imread(str(image_path))
                if img is not None:
                    height, width = img.shape[:2]
                    return width >= 100 and height >= 100
                return False
            except:
                return False
    
    def is_good_quality_image(self, image_path):
        """OpenCV를 사용한 이미지 품질 검증 (완화된 기준)"""
        self.quality_stats['total_checked'] += 1
        
        try:
            import cv2
            import numpy as np
            
            # 이미지 로드
            img = cv2.imread(str(image_path))
            if img is None:
                self.quality_stats['quality_failed'] += 1
                return False
            
            height, width = img.shape[:2]
            
            # 1. 최소 해상도 체크 (대폭 완화: 150x150 → 100x100)
            if width < 100 or height < 100:
                self.quality_stats['resolution_rejected'] += 1
                self.quality_stats['quality_failed'] += 1
                return False
            
            # 2. 종횡비 체크 (완화: 0.3-3.0 → 0.2-5.0)
            aspect_ratio = width / height
            if aspect_ratio < 0.2 or aspect_ratio > 5.0:
                self.quality_stats['quality_failed'] += 1
                return False
            
            # 3. 블러 검출 (대폭 완화: 50 → 20)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 20:  # 블러 임계값 대폭 완화
                self.quality_stats['blur_rejected'] += 1
                self.quality_stats['quality_failed'] += 1
                return False
            
            # 4. 밝기 체크 (완화: 30-225 → 20-235)
            mean_brightness = np.mean(gray)
            if mean_brightness < 20 or mean_brightness > 235:
                self.quality_stats['brightness_rejected'] += 1
                self.quality_stats['quality_failed'] += 1
                return False
            
            # 5. 대비 체크 (완화: 20 → 10)
            contrast = np.std(gray)
            if contrast < 10:
                self.quality_stats['contrast_rejected'] += 1
                self.quality_stats['quality_failed'] += 1
                return False
            
            # 6. 색상 다양성 체크 (완화: 15 → 8)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            color_std = np.std(hsv[:,:,1])  # 채도의 표준편차
            if color_std < 8:
                self.quality_stats['quality_failed'] += 1
                return False
            
            # 7. 노이즈 레벨 체크 (완화: 25 → 35)
            noise_level = self.estimate_noise_level(gray)
            if noise_level > 35:
                self.quality_stats['noise_rejected'] += 1
                self.quality_stats['quality_failed'] += 1
                return False
            
            # 모든 검사를 통과하면 좋은 품질
            self.quality_stats['quality_passed'] += 1
            return True
            
        except Exception as e:
            # OpenCV 오류 시 기본 검증만 수행
            return self.basic_image_validation(image_path)
    
    def estimate_noise_level(self, gray_img):
        """이미지 노이즈 레벨 추정"""
        try:
            import cv2
            import numpy as np
            # 가우시안 블러 적용 후 원본과의 차이로 노이즈 추정
            blurred = cv2.GaussianBlur(gray_img, (5, 5), 0)
            noise = cv2.absdiff(gray_img, blurred)
            return np.mean(noise)
        except:
            return 0
    
    def basic_image_validation(self, image_path):
        """기본 이미지 검증 (OpenCV 없이) - 완화된 기준"""
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                width, height = img.size
                
                # 최소 해상도 체크 (완화: 200x200 → 120x120)
                if width < 120 or height < 120:
                    return False
                
                # 종횡비 체크 (완화: 0.3-3.0 → 0.2-5.0)
                aspect_ratio = width / height
                if aspect_ratio < 0.2 or aspect_ratio > 5.0:
                    return False
                
                # 파일 크기 체크 (완화: 10KB → 5KB)
                file_size = image_path.stat().st_size
                if file_size < 5000:  # 5KB 미만
                    return False
                
                return True
        except:
            return False
    
    def search_fishbase(self, genus, species, max_images=50):
        """FishBase에서 이미지 검색"""
        images = []
        
        try:
            # FishBase URL들
            urls = [
                f"https://www.fishbase.se/summary/{genus}-{species}.html",
                f"https://www.fishbase.se/photos/ThumbnailsSummary.php?Genus={genus}&Species={species}",
                f"https://www.fishbase.se/search.php?lang=English&SearchALL={genus}+{species}"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        img_tags = soup.find_all('img', src=True)
                        
                        for img_tag in img_tags:
                            img_url = img_tag.get('src')
                            if img_url and not img_url.startswith('http'):
                                img_url = urljoin(url, img_url)
                            
                            # FishBase 특화 필터링
                            if self.is_valid_fishbase_image(img_url):
                                images.append(img_url)
                                
                                if len(images) >= max_images:
                                    break
                    
                    time.sleep(1)  # 요청 간 지연
                    
                except Exception as e:
                    print(f"FishBase 검색 오류: {e}")
                    continue
                    
                if len(images) >= max_images:
                    break
                    
        except Exception as e:
            print(f"FishBase 전체 오류: {e}")
        
        return images[:max_images]

    def is_valid_fishbase_image(self, url):
        """FishBase 이미지 전용 검증 (불필요한 이미지 제외)"""
        if not url or not self.is_valid_image_url(url):
            return False
        
        # FishBase에서 제외할 패턴들
        exclude_patterns = [
            'banner', 'logo', 'facebook', 'donate', 'nav', 'button',
            'fb3.png', 'fb-nav', 'DonateButton', 'ADBanner',
            'thumbnail', 'tn_', 'aquamaps', 'native/pic'
        ]
        
        url_lower = url.lower()
        if any(pattern.lower() in url_lower for pattern in exclude_patterns):
            return False
        
        # FishBase에서 유효한 이미지 패턴들 (더 관대하게)
        valid_patterns = [
            '/species/', '/photos/', 'fish', 'specimen', 'adult', 'juvenile',
            '.jpg', '.jpeg', '.png'  # 기본 이미지 확장자
        ]
        
        # 유효한 패턴이 하나라도 있으면 허용
        if any(pattern.lower() in url_lower for pattern in valid_patterns):
            return True
        
        return False
    
    def search_google_images(self, genus, species, common_names=None, max_images=30):
        """Google Images에서 검색"""
        images = []
        
        # 검색어 생성
        search_terms = [
            f"{genus} {species} fish",
            f"{species} fish"
        ]
        
        if common_names:
            for name in common_names[:2]:
                search_terms.append(f"{name} fish")
        
        for search_term in search_terms:
            try:
                search_url = f"https://www.google.com/search?q={quote(search_term)}&tbm=isch"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    # 간단한 이미지 URL 추출
                    img_urls = re.findall(r'"(https://[^"]*\.(?:jpg|jpeg|png|gif))"', response.text)
                    
                    for img_url in img_urls[:10]:  # 검색어당 최대 10개
                        if self.is_valid_image_url(img_url):
                            images.append(img_url)
                            
                            if len(images) >= max_images:
                                break
                
                time.sleep(2)  # 검색어 간 지연
                
            except Exception as e:
                print(f"Google 검색 오류: {search_term} - {e}")
                continue
                
            if len(images) >= max_images:
                break
        
        return images[:max_images]
    
    def search_google_images_extended(self, genus, species, common_names=None, max_images=150):
        """확장된 Google Images 검색 (다양한 각도와 상황)"""
        images = []
        
        # 다양한 각도와 상황을 위한 확장된 검색 키워드
        base_terms = [
            f"{genus} {species}",
            f"{genus} {species} fish",
            f"{genus} {species} marine",
            f"{genus} {species} aquarium",
            f"{genus} {species} underwater",
            f"{genus} {species} profile",
            f"{genus} {species} side view",
            f"{genus} {species} front view",
            f"{genus} {species} swimming",
            f"{genus} {species} coral reef",
            f"{genus} {species} different angles",
            f"{genus} {species} close up",
            f"{genus} {species} full body"
        ]
        
        if common_names:
            for name in common_names[:3]:  # 상위 3개 일반명 사용
                base_terms.extend([
                    name,
                    f"{name} fish",
                    f"{name} marine fish",
                    f"{name} aquarium fish",
                    f"{name} underwater photo",
                    f"{name} swimming",
                    f"{name} profile view",
                    f"{name} side angle",
                    f"{name} different poses",
                    f"{name} various angles"
                ])
        
        for term in base_terms:
            if len(images) >= max_images:
                break
                
            try:
                search_url = f"https://www.google.com/search?q={quote(term)}&tbm=isch"
                response = self.session.get(search_url, timeout=20)
                
                if response.status_code == 200:
                    import re
                    # 다양한 Google Images URL 패턴들
                    patterns = [
                        r'"ou":"([^"]*\.(?:jpg|jpeg|png|gif))"',  # 기본 패턴
                        r'"(https?://[^"]*\.(?:jpg|jpeg|png|gif))"',  # 직접 URL
                        r'imgurl=([^&]*\.(?:jpg|jpeg|png|gif))',  # imgurl 파라미터
                        r'src="([^"]*\.(?:jpg|jpeg|png|gif))"',  # src 속성
                        r'data-src="([^"]*\.(?:jpg|jpeg|png|gif))"',  # data-src 속성
                        r'https://[^"]*\.(?:jpg|jpeg|png|gif)',  # 단순 URL 매칭
                    ]
                    
                    img_urls = []
                    for pattern in patterns:
                        matches = re.findall(pattern, response.text)
                        img_urls.extend(matches)
                    
                    # 중복 제거
                    img_urls = list(set(img_urls))
                    
                    for url in img_urls[:8]:  # 검색어당 최대 8개로 증가
                        if len(images) >= max_images:
                            break
                        if self.is_valid_image_url(url):
                            images.append(url)
                
                time.sleep(0.4)  # 요청 간 지연
                
            except Exception as e:
                print(f"    Google 검색 오류 ({term}): {e}")
                continue
        
        return images[:max_images]
    
    def search_wikipedia(self, genus, species, common_names=None, max_images=30):
        """Wikipedia에서 이미지 검색"""
        images = []
        
        search_terms = [f"{genus} {species}", f"{genus}_{species}"]
        if common_names:
            search_terms.extend([name.replace(' ', '_') for name in common_names[:2]])
        
        for term in search_terms:
            if len(images) >= max_images:
                break
                
            try:
                wiki_url = f"https://en.wikipedia.org/wiki/{quote(term)}"
                response = self.session.get(wiki_url, timeout=15)
                
                if response.status_code == 200:
                    import re
                    # Wikipedia 이미지 패턴
                    patterns = [
                        r'//upload\.wikimedia\.org/[^"]*\.(?:jpg|jpeg|png)',
                        r'https://upload\.wikimedia\.org/[^"]*\.(?:jpg|jpeg|png)'
                    ]
                    
                    for pattern in patterns:
                        urls = re.findall(pattern, response.text)
                        for url in urls:
                            if not url.startswith('http'):
                                url = f"https:{url}"
                            if self.is_valid_image_url(url):
                                images.append(url)
                                if len(images) >= max_images:
                                    break
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    Wikipedia 검색 오류: {e}")
                continue
        
        return images[:max_images]
    
    def search_flickr(self, genus, species, common_names=None, max_images=40):
        """Flickr에서 이미지 검색"""
        images = []
        
        search_terms = [f"{genus} {species}", f"{genus} {species} fish"]
        if common_names:
            search_terms.extend(common_names[:2])
        
        for term in search_terms:
            if len(images) >= max_images:
                break
                
            try:
                search_url = f"https://www.flickr.com/search/?text={quote(term)}"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    import re
                    # Flickr 이미지 패턴
                    patterns = [
                        r'https://live\.staticflickr\.com/[^"]*_[a-z]\.jpg',
                        r'https://farm\d+\.staticflickr\.com/[^"]*\.jpg'
                    ]
                    
                    for pattern in patterns:
                        urls = re.findall(pattern, response.text)
                        for url in urls[:8]:
                            if self.is_valid_image_url(url):
                                images.append(url)
                                if len(images) >= max_images:
                                    break
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    Flickr 검색 오류: {e}")
                continue
        
        return images[:max_images]
    
    def search_with_additional_terms(self, genus, species, common_names=None, max_images=50):
        """추가 검색어로 더 많은 이미지 수집"""
        images = []
        
        # 학습에 도움이 되는 다양한 상황의 검색어
        additional_terms = [
            f"{genus} {species} juvenile",  # 어린 개체
            f"{genus} {species} adult",     # 성체
            f"{genus} {species} male",      # 수컷
            f"{genus} {species} female",    # 암컷
            f"{genus} {species} breeding",  # 번식기
            f"{genus} {species} natural habitat",  # 자연 서식지
            f"{genus} {species} aquarium tank",    # 수족관
            f"{genus} {species} feeding",   # 먹이 활동
            f"{genus} {species} schooling", # 무리 행동
            f"{genus} {species} behavior"   # 행동
        ]
        
        if common_names:
            for name in common_names[:2]:
                additional_terms.extend([
                    f"{name} juvenile",
                    f"{name} adult fish",
                    f"{name} natural environment",
                    f"{name} aquarium"
                ])
        
        for term in additional_terms:
            if len(images) >= max_images:
                break
                
            try:
                search_url = f"https://www.google.com/search?q={quote(term)}&tbm=isch"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    import re
                    img_urls = re.findall(r'"(https?://[^"]*\.(?:jpg|jpeg|png|gif))"', response.text)
                    
                    for url in img_urls[:4]:  # 검색어당 최대 4개
                        if len(images) >= max_images:
                            break
                        if self.is_valid_image_url(url):
                            images.append(url)
                
                time.sleep(0.6)
                
            except Exception as e:
                print(f"    추가 검색 오류 ({term}): {e}")
                continue
        
        return images[:max_images]
    
    def search_bing_images(self, genus, species, common_names=None, max_images=120):
        """Bing Images에서 검색"""
        images = []
        
        search_terms = [
            f"{genus} {species}",
            f"{genus} {species} fish",
            f"{genus} {species} marine aquarium",
            f"{genus} {species} underwater photography"
        ]
        
        if common_names:
            for name in common_names[:3]:
                search_terms.extend([
                    name,
                    f"{name} fish",
                    f"{name} marine fish",
                    f"{name} aquarium"
                ])
        
        for term in search_terms:
            if len(images) >= max_images:
                break
                
            try:
                search_url = f"https://www.bing.com/images/search?q={quote(term)}"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    import re
                    # 다양한 Bing 이미지 URL 패턴들
                    patterns = [
                        r'"murl":"([^"]*\.(?:jpg|jpeg|png|gif))"',  # 기본 murl 패턴
                        r'"imgurl":"([^"]*\.(?:jpg|jpeg|png|gif))"',  # imgurl 패턴
                        r'"src":"([^"]*\.(?:jpg|jpeg|png|gif))"',  # src 패턴
                        r'src="([^"]*\.(?:jpg|jpeg|png|gif))"',  # 따옴표 없는 src
                        r'https://[^"\s]*\.(?:jpg|jpeg|png|gif)',  # 직접 URL 매칭
                    ]
                    
                    img_urls = []
                    for pattern in patterns:
                        matches = re.findall(pattern, response.text)
                        img_urls.extend(matches)
                    
                    # 중복 제거
                    img_urls = list(set(img_urls))
                    
                    for url in img_urls[:10]:  # 검색어당 최대 10개로 증가
                        if len(images) >= max_images:
                            break
                        if self.is_valid_image_url(url):
                            images.append(url)
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    Bing 검색 오류: {e}")
                continue
        
        return images[:max_images]
    
    def search_yandex_images(self, genus, species, common_names=None, max_images=100):
        """Yandex Images에서 검색"""
        images = []
        
        search_terms = [f"{genus} {species}", f"{genus} {species} fish"]
        if common_names:
            search_terms.extend(common_names[:2])
        
        for term in search_terms:
            if len(images) >= max_images:
                break
                
            try:
                search_url = f"https://yandex.com/images/search?text={quote(term)}"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    import re
                    # Yandex 이미지 패턴
                    img_urls = re.findall(r'"url":"([^"]*\.(?:jpg|jpeg|png|gif))"', response.text)
                    
                    for url in img_urls[:10]:
                        if len(images) >= max_images:
                            break
                        # URL 디코딩
                        url = url.replace('\\/', '/')
                        if self.is_valid_image_url(url):
                            images.append(url)
                
                time.sleep(0.7)
                
            except Exception as e:
                print(f"    Yandex 검색 오류: {e}")
                continue
        
        return images[:max_images]
    
    def search_reef2reef(self, genus, species, common_names=None, max_images=40):
        """Reef2Reef 포럼에서 검색"""
        images = []
        
        search_terms = [f"{genus} {species}"]
        if common_names:
            search_terms.extend(common_names[:2])
        
        for term in search_terms:
            if len(images) >= max_images:
                break
                
            try:
                search_url = f"https://www.reef2reef.com/search/1/?q={quote(term)}&o=relevance"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    img_tags = soup.find_all('img', src=True)
                    
                    for img in img_tags:
                        if len(images) >= max_images:
                            break
                        src = img.get('src')
                        if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png']):
                            if not src.startswith('http'):
                                src = urljoin('https://www.reef2reef.com', src)
                            if self.is_valid_image_url(src):
                                images.append(src)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    Reef2Reef 검색 오류: {e}")
                continue
        
        return images[:max_images]
    
    def search_marinespecies_org(self, genus, species, max_images=30):
        """WoRMS (World Register of Marine Species)에서 검색"""
        images = []
        
        try:
            # WoRMS API 검색
            search_url = f"http://www.marinespecies.org/rest/AphiaRecordsByName/{quote(genus + ' ' + species)}"
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    aphia_id = data[0].get('AphiaID')
                    if aphia_id:
                        # 이미지 검색
                        img_url = f"http://www.marinespecies.org/rest/AphiaExternalIDsByAphiaID/{aphia_id}?type=images"
                        img_response = self.session.get(img_url, timeout=15)
                        
                        if img_response.status_code == 200:
                            img_data = img_response.json()
                            for item in img_data[:max_images]:
                                if 'url' in item:
                                    url = item['url']
                                    if self.is_valid_image_url(url):
                                        images.append(url)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    MarineSpecies.org 검색 오류: {e}")
        
        return images[:max_images]
    
    def search_eol(self, genus, species, common_names=None, max_images=35):
        """Encyclopedia of Life (EOL)에서 검색"""
        images = []
        
        try:
            # EOL 검색
            search_url = f"https://eol.org/search?q={quote(genus + ' ' + species)}"
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 이미지 링크 찾기
                img_links = soup.find_all('a', href=True)
                for link in img_links:
                    if len(images) >= max_images:
                        break
                    href = link.get('href')
                    if href and '/media/' in href:
                        # 미디어 페이지에서 실제 이미지 URL 추출
                        try:
                            media_url = urljoin('https://eol.org', href)
                            media_response = self.session.get(media_url, timeout=10)
                            if media_response.status_code == 200:
                                media_soup = BeautifulSoup(media_response.content, 'html.parser')
                                img_tags = media_soup.find_all('img', src=True)
                                for img in img_tags:
                                    src = img.get('src')
                                    if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png']):
                                        if not src.startswith('http'):
                                            src = urljoin('https://eol.org', src)
                                        if self.is_valid_image_url(src):
                                            images.append(src)
                                            break
                        except:
                            continue
            
            time.sleep(1)
            
        except Exception as e:
            print(f"    EOL 검색 오류: {e}")
        
        return images[:max_images]
    
    def search_inaturalist(self, genus, species, common_names=None, max_images=45):
        """iNaturalist에서 검색"""
        images = []
        
        try:
            # iNaturalist API 검색
            search_url = f"https://api.inaturalist.org/v1/taxa?q={quote(genus + ' ' + species)}"
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    taxon_id = data['results'][0].get('id')
                    if taxon_id:
                        # 관찰 이미지 검색
                        obs_url = f"https://api.inaturalist.org/v1/observations?taxon_id={taxon_id}&photos=true&per_page=30"
                        obs_response = self.session.get(obs_url, timeout=15)
                        
                        if obs_response.status_code == 200:
                            obs_data = obs_response.json()
                            for obs in obs_data.get('results', []):
                                if len(images) >= max_images:
                                    break
                                for photo in obs.get('photos', []):
                                    if len(images) >= max_images:
                                        break
                                    url = photo.get('url')
                                    if url:
                                        # 고해상도 버전 URL 생성
                                        high_res_url = url.replace('square', 'large')
                                        if self.is_valid_image_url(high_res_url):
                                            images.append(high_res_url)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    iNaturalist 검색 오류: {e}")
        
        return images[:max_images]
    
    def search_gbif(self, genus, species, max_images=25):
        """GBIF (Global Biodiversity Information Facility)에서 검색"""
        images = []
        
        try:
            # GBIF 종 검색
            search_url = f"https://api.gbif.org/v1/species/match?name={quote(genus + ' ' + species)}"
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                species_key = data.get('speciesKey')
                if species_key:
                    # 이미지가 있는 occurrence 검색
                    occ_url = f"https://api.gbif.org/v1/occurrence/search?speciesKey={species_key}&mediaType=StillImage&limit=20"
                    occ_response = self.session.get(occ_url, timeout=15)
                    
                    if occ_response.status_code == 200:
                        occ_data = occ_response.json()
                        for result in occ_data.get('results', []):
                            if len(images) >= max_images:
                                break
                            media = result.get('media', [])
                            for item in media:
                                if len(images) >= max_images:
                                    break
                                url = item.get('identifier')
                                if url and self.is_valid_image_url(url):
                                    images.append(url)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    GBIF 검색 오류: {e}")
        
        return images[:max_images]
    
    def search_aquarium_sites(self, genus, species, common_names=None, max_images=40):
        """수족관 관련 사이트들에서 검색"""
        images = []
        
        # 주요 수족관 사이트들
        aquarium_sites = [
            "liveaquaria.com",
            "marinedepot.com", 
            "saltwaterfish.com",
            "aquariumcoop.com"
        ]
        
        search_terms = [f"{genus} {species}"]
        if common_names:
            search_terms.extend(common_names[:2])
        
        for site in aquarium_sites:
            if len(images) >= max_images:
                break
                
            for term in search_terms:
                if len(images) >= max_images:
                    break
                    
                try:
                    # Google site-specific 검색
                    search_url = f"https://www.google.com/search?q=site:{site}+{quote(term)}&tbm=isch"
                    response = self.session.get(search_url, timeout=15)
                    
                    if response.status_code == 200:
                        import re
                        img_urls = re.findall(r'"(https?://[^"]*\.(?:jpg|jpeg|png|gif))"', response.text)
                        
                        for url in img_urls[:5]:  # 사이트당 최대 5개
                            if len(images) >= max_images:
                                break
                            if site in url and self.is_valid_image_url(url):
                                images.append(url)
                    
                    time.sleep(0.8)
                    
                except Exception as e:
                    print(f"    {site} 검색 오류: {e}")
                    continue
        
        return images[:max_images]
    
    def search_pinterest(self, genus, species, common_names=None, max_images=35):
        """Pinterest에서 검색"""
        images = []
        
        search_terms = [f"{genus} {species} fish"]
        if common_names:
            search_terms.extend([f"{name} fish" for name in common_names[:2]])
        
        for term in search_terms:
            if len(images) >= max_images:
                break
                
            try:
                search_url = f"https://www.pinterest.com/search/pins/?q={quote(term)}"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    import re
                    # Pinterest 이미지 패턴
                    img_urls = re.findall(r'"url":"([^"]*\.(?:jpg|jpeg|png))"', response.text)
                    
                    for url in img_urls[:12]:
                        if len(images) >= max_images:
                            break
                        url = url.replace('\\/', '/')
                        if self.is_valid_image_url(url):
                            images.append(url)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    Pinterest 검색 오류: {e}")
                continue
        
        return images[:max_images]
    
    def search_duckduckgo_images(self, genus, species, common_names=None, max_images=80):
        """DuckDuckGo Images에서 검색"""
        images = []
        
        search_terms = [
            f"{genus} {species}",
            f"{genus} {species} fish",
            f"{genus} {species} marine aquarium"
        ]
        
        if common_names:
            search_terms.extend([f"{name} fish" for name in common_names[:2]])
        
        for term in search_terms:
            if len(images) >= max_images:
                break
                
            try:
                search_url = f"https://duckduckgo.com/?q={quote(term)}&t=h_&iax=images&ia=images"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    import re
                    # DuckDuckGo 이미지 패턴
                    img_urls = re.findall(r'"image":"([^"]*\.(?:jpg|jpeg|png|gif))"', response.text)
                    
                    for url in img_urls[:10]:
                        if len(images) >= max_images:
                            break
                        url = url.replace('\\/', '/')
                        if self.is_valid_image_url(url):
                            images.append(url)
                
                time.sleep(0.6)
                
            except Exception as e:
                print(f"    DuckDuckGo 검색 오류: {e}")
                continue
        
        return images[:max_images]
    
    def search_shutterstock(self, genus, species, common_names=None, max_images=60):
        """Shutterstock에서 검색 (무료 이미지만)"""
        images = []
        
        search_terms = [f"{genus} {species}"]
        if common_names:
            search_terms.extend(common_names[:2])
        
        for term in search_terms:
            if len(images) >= max_images:
                break
                
            try:
                # Shutterstock 무료 이미지 검색
                search_url = f"https://www.shutterstock.com/search/{quote(term)}?image_type=photo&category=animals"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    img_tags = soup.find_all('img', src=True)
                    
                    for img in img_tags[:15]:
                        if len(images) >= max_images:
                            break
                        src = img.get('src')
                        if src and 'shutterstock' in src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png']):
                            if self.is_valid_image_url(src):
                                images.append(src)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    Shutterstock 검색 오류: {e}")
                continue
        
        return images[:max_images]
    
    def search_unsplash(self, genus, species, common_names=None, max_images=50):
        """Unsplash에서 검색"""
        images = []
        
        search_terms = [f"{genus} {species} fish"]
        if common_names:
            search_terms.extend([f"{name} fish" for name in common_names[:2]])
        
        for term in search_terms:
            if len(images) >= max_images:
                break
                
            try:
                search_url = f"https://unsplash.com/s/photos/{quote(term)}"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    import re
                    # Unsplash 이미지 패턴
                    img_urls = re.findall(r'https://images\.unsplash\.com/[^"]*\.jpg[^"]*', response.text)
                    
                    for url in img_urls[:12]:
                        if len(images) >= max_images:
                            break
                        if self.is_valid_image_url(url):
                            images.append(url)
                
                time.sleep(0.8)
                
            except Exception as e:
                print(f"    Unsplash 검색 오류: {e}")
                continue
        
        return images[:max_images]
    
    def search_pexels(self, genus, species, common_names=None, max_images=45):
        """Pexels에서 검색"""
        images = []
        
        search_terms = [f"{genus} {species} fish"]
        if common_names:
            search_terms.extend([f"{name} fish" for name in common_names[:2]])
        
        for term in search_terms:
            if len(images) >= max_images:
                break
                
            try:
                search_url = f"https://www.pexels.com/search/{quote(term)}/"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    img_tags = soup.find_all('img', src=True)
                    
                    for img in img_tags[:12]:
                        if len(images) >= max_images:
                            break
                        src = img.get('src')
                        if src and 'pexels' in src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png']):
                            if self.is_valid_image_url(src):
                                images.append(src)
                
                time.sleep(0.7)
                
            except Exception as e:
                print(f"    Pexels 검색 오류: {e}")
                continue
        
        return images[:max_images]
    
    def search_reddit_aquariums(self, genus, species, common_names=None, max_images=40):
        """Reddit 수족관 커뮤니티에서 검색"""
        images = []
        
        # Reddit 수족관 관련 서브레딧들
        subreddits = ['Aquariums', 'ReefTank', 'MarineAquariums', 'SaltWaterAquarium']
        
        search_terms = [f"{genus} {species}"]
        if common_names:
            search_terms.extend(common_names[:2])
        
        for subreddit in subreddits:
            if len(images) >= max_images:
                break
                
            for term in search_terms:
                if len(images) >= max_images:
                    break
                    
                try:
                    search_url = f"https://www.reddit.com/r/{subreddit}/search/?q={quote(term)}&restrict_sr=1"
                    response = self.session.get(search_url, timeout=15)
                    
                    if response.status_code == 200:
                        import re
                        # Reddit 이미지 패턴
                        img_urls = re.findall(r'https://[^"]*\.(?:jpg|jpeg|png|gif)', response.text)
                        
                        for url in img_urls[:5]:  # 서브레딧당 최대 5개
                            if len(images) >= max_images:
                                break
                            if 'reddit' in url and self.is_valid_image_url(url):
                                images.append(url)
                    
                    time.sleep(1.2)
                    
                except Exception as e:
                    print(f"    Reddit r/{subreddit} 검색 오류: {e}")
                    continue
        
        return images[:max_images]
    
    def search_instagram_hashtags(self, genus, species, common_names=None, max_images=35):
        """Instagram 해시태그에서 검색 (공개 피드만)"""
        images = []
        
        hashtags = [
            f"{genus.lower()}{species.lower()}",
            f"{genus.lower()}_{species.lower()}",
            "marinefish", "saltwatertank", "reeftank"
        ]
        
        if common_names:
            for name in common_names[:2]:
                hashtags.append(name.lower().replace(' ', ''))
        
        for hashtag in hashtags:
            if len(images) >= max_images:
                break
                
            try:
                search_url = f"https://www.instagram.com/explore/tags/{hashtag}/"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    import re
                    # Instagram 이미지 패턴
                    img_urls = re.findall(r'https://[^"]*\.(?:jpg|jpeg)', response.text)
                    
                    for url in img_urls[:8]:
                        if len(images) >= max_images:
                            break
                        if 'instagram' in url and self.is_valid_image_url(url):
                            images.append(url)
                
                time.sleep(1.5)
                
            except Exception as e:
                print(f"    Instagram #{hashtag} 검색 오류: {e}")
                continue
        
        return images[:max_images]
    
    def search_aquarium_forums(self, genus, species, common_names=None, max_images=50):
        """다양한 수족관 포럼에서 검색"""
        images = []
        
        # 주요 수족관 포럼들
        forums = [
            "nanoreef.com",
            "reefcentral.com", 
            "ultimatereef.net",
            "reefbuilders.com",
            "aquariumadvice.com"
        ]
        
        search_terms = [f"{genus} {species}"]
        if common_names:
            search_terms.extend(common_names[:2])
        
        for forum in forums:
            if len(images) >= max_images:
                break
                
            for term in search_terms:
                if len(images) >= max_images:
                    break
                    
                try:
                    # Google site-specific 검색
                    search_url = f"https://www.google.com/search?q=site:{forum}+{quote(term)}+images&tbm=isch"
                    response = self.session.get(search_url, timeout=15)
                    
                    if response.status_code == 200:
                        import re
                        img_urls = re.findall(r'"(https?://[^"]*\.(?:jpg|jpeg|png|gif))"', response.text)
                        
                        for url in img_urls[:4]:  # 포럼당 최대 4개
                            if len(images) >= max_images:
                                break
                            if forum in url and self.is_valid_image_url(url):
                                images.append(url)
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"    {forum} 검색 오류: {e}")
                    continue
        
        return images[:max_images]
    
    def search_youtube_thumbnails(self, genus, species, common_names=None, max_images=30):
        """YouTube 동영상 썸네일에서 검색"""
        images = []
        
        search_terms = [
            f"{genus} {species} aquarium",
            f"{genus} {species} care guide",
            f"{genus} {species} feeding"
        ]
        
        if common_names:
            for name in common_names[:2]:
                search_terms.extend([
                    f"{name} aquarium",
                    f"{name} care"
                ])
        
        for term in search_terms:
            if len(images) >= max_images:
                break
                
            try:
                search_url = f"https://www.youtube.com/results?search_query={quote(term)}"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    import re
                    # YouTube 썸네일 패턴
                    thumbnail_urls = re.findall(r'https://i\.ytimg\.com/vi/[^/]+/[^"]*\.jpg', response.text)
                    
                    for url in thumbnail_urls[:8]:
                        if len(images) >= max_images:
                            break
                        if self.is_valid_image_url(url):
                            images.append(url)
                
                time.sleep(0.8)
                
            except Exception as e:
                print(f"    YouTube 검색 오류: {e}")
                continue
        
        return images[:max_images]
    
    def search_academic_sources(self, genus, species, max_images=25):
        """학술 자료에서 검색"""
        images = []
        
        # 학술 사이트들
        academic_sites = [
            "researchgate.net",
            "academia.edu", 
            "bioone.org",
            "fishbase.org"
        ]
        
        for site in academic_sites:
            if len(images) >= max_images:
                break
                
            try:
                search_url = f"https://www.google.com/search?q=site:{site}+{quote(genus + ' ' + species)}+image&tbm=isch"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    import re
                    img_urls = re.findall(r'"(https?://[^"]*\.(?:jpg|jpeg|png|gif))"', response.text)
                    
                    for url in img_urls[:6]:  # 사이트당 최대 6개
                        if len(images) >= max_images:
                            break
                        if site in url and self.is_valid_image_url(url):
                            images.append(url)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    {site} 검색 오류: {e}")
                continue
        
        return images[:max_images]
    
    def _get_species_directory_path(
        self, genus: str, species: str, variant: str | None = None
    ) -> Path:
        """종의 분류학적 위치에 따른 디렉토리 경로 반환 (variant 하위 폴더 지원)"""
        # TaxonomyManager에서 종 정보 가져오기
        species_info = self.taxonomy_manager.get_species_info(genus, species)
        
        if species_info:
            # 정확한 분류학적 계층구조
            if species_info.class_name == "Chondrichthyes":
                # dataset/Chondrichthyes/Order/Family/Genus/Genus_species
                full_path = (
                    self.dataset_dir
                    / species_info.class_name
                    / species_info.order
                    / species_info.family
                    / species_info.genus
                    / f"{genus}_{species}"
                )
            elif species_info.class_name == "Osteichthyes":
                # dataset/Osteichthyes/Actinopterygii/Order/Family/Genus/Genus_species
                full_path = (
                    self.dataset_dir
                    / species_info.class_name
                    / "Actinopterygii"
                    / species_info.order
                    / species_info.family
                    / species_info.genus
                    / f"{genus}_{species}"
                )
            elif species_info.class_name == "Anthozoa":
                # 산호: dataset/Anthozoa/Order/Family/Genus/Genus_species
                full_path = (
                    self.dataset_dir
                    / species_info.class_name
                    / species_info.order
                    / species_info.family
                    / species_info.genus
                    / f"{genus}_{species}"
                )
            else:
                # 알 수 없는 class는 보수적으로 class/order/family/genus
                full_path = (
                    self.dataset_dir
                    / species_info.class_name
                    / species_info.order
                    / species_info.family
                    / species_info.genus
                    / f"{genus}_{species}"
                )
        else:
            # 분류 정보를 찾을 수 없는 경우 기본 경로
            full_path = (
                self.dataset_dir
                / "Unclassified"
                / genus
                / f"{genus}_{species}"
            )
        
        # 변이(트레이드 네임) 하위 폴더 추가
        if variant:
            safe_variant = self._sanitize_name(variant)
            full_path = full_path / safe_variant

        return full_path

    def download_species(
        self,
        genus_species: str,
        count: int = 50,
        variant: str | None = None,
    ) -> int:
        """간편 종 다운로드 래퍼: "Genus species" 문자열과 개수로 호출.
        산호 기본은 50장으로 사용.
        """
        try:
            parts = genus_species.split()
            if len(parts) != 2:
                print(f"잘못된 종명 형식: {genus_species}")
                return 0
            genus, species = parts
            common_names = self.taxonomy_manager.get_common_names(
                genus,
                species,
            )
            return self.scrape_species(
                genus,
                species,
                common_names,
                count,
                variant,
            )
        except Exception as e:
            print(f"{genus_species} 다운로드 중 오류: {e}")
            return 0

    def _sanitize_name(self, name: str) -> str:
        """폴더/파일명에 안전하도록 정리"""
        import re
        cleaned = re.sub(r"[\\/]+", "-", name).strip()
        cleaned = re.sub(r"[<>:\\|?*]", "", cleaned)
        return cleaned[:80]
    
    def is_valid_image_url(self, url):
        """유효한 이미지 URL인지 확인 (강화된 필터링)"""
        if not url or len(url) < 10:
            return False

        url_lower = url.lower()

        # 명백히 문제가 있는 패턴들 제외
        exclude_patterns = [
            'javascript:', 'data:text', 'mailto:',
            # 로고 및 UI 요소들
            'logo', 'icon', 'banner', 'button', 'nav', 'menu',
            'header', 'footer', 'sidebar', 'toolbar', 'badge',
            # 소셜미디어 로고들
            'facebook', 'twitter', 'instagram', 'youtube', 'reddit',
            'linkedin', 'pinterest', 'tiktok', 'snapchat',
            # 광고 및 프로모션
            'ad', 'ads', 'advertisement', 'promo', 'sponsor',
            'donate', 'donation', 'paypal', 'patreon',
            # 썸네일 및 작은 이미지들
            'thumb', 'tn_', 'thumbnail', 'preview', 'mini',
            # 기타 불필요한 요소들
            'avatar', 'profile', 'user', 'member', 'admin',
            'loading', 'spinner', 'placeholder', 'blank',
            'error', '404', 'not-found', 'missing'
        ]

        if any(pattern in url_lower for pattern in exclude_patterns):
            return False

        # HTTP/HTTPS URL 체크
        if not url.startswith(('http://', 'https://')):
            return False

        # 이미지 확장자가 있으면 허용 (단, 제외 패턴에 걸리지 않은 경우)
        if any(
            ext in url_lower
            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        ):
            return True

        # 어류/산호 관련 키워드가 있으면 허용
        allow_keywords = [
            'fish', 'marine', 'aquarium', 'coral', 'reef', 'ocean', 'sea',
            'underwater', 'diving', 'snorkel', 'scuba', 'tropical',
            'saltwater', 'species', 'specimen', 'animal', 'wildlife'
        ]
        if any(keyword in url_lower for keyword in allow_keywords):
            return True

        # 신뢰할 수 있는 이미지 호스팅 도메인들
        trusted_domains = [
            'imgur', 'flickr', 'wikimedia', 'googleusercontent',
            'pinimg', 'unsplash', 'pexels', 'fishbase', 'inaturalist',
            'eol.org', 'gbif.org', 'marinespecies.org'
        ]
        if any(domain in url_lower for domain in trusted_domains):
            return True

        return False
    
    def scrape_species(self, genus, species, common_names=None, target_images=1500, variant: str | None = None):
        """단일 종 스크래핑 (확장된 다중 소스)"""
        print(f"\n🔍 {genus} {species} 검색 중...")
        
        # 분류학적 계층에 따른 저장 폴더 생성
        species_path = self._get_species_directory_path(genus, species, variant)
        species_path.mkdir(parents=True, exist_ok=True)
        
        # 이미지 URL 수집 (다중 소스)
        all_urls = []
        
        # 1. FishBase에서 수집 (전문 어류 DB)
        print("  📥 FishBase 검색 중...")
        try:
            fishbase_urls = self.search_fishbase(genus, species, 100)
            all_urls.extend(fishbase_urls)
            print(f"  📊 FishBase: {len(fishbase_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ FishBase 오류: {e}")
        
        # 2. Google Images에서 수집 (확장된 검색어) - 증량
        print("  📥 Google Images 검색 중...")
        try:
            google_urls = self.search_google_images_extended(genus, species, common_names, 250)
            all_urls.extend(google_urls)
            print(f"  📊 Google: {len(google_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ Google 오류: {e}")
        
        # 2-1. 간단한 Google 검색 추가
        print("  📥 간단 Google 검색 중...")
        try:
            simple_google_urls = self.search_simple_google(genus, species, common_names, 200)
            all_urls.extend(simple_google_urls)
            print(f"  📊 간단 Google: {len(simple_google_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ 간단 Google 오류: {e}")
        
        # 2-2. 직접 이미지 사이트들에서 검색
        print("  📥 직접 이미지 사이트 검색 중...")
        try:
            direct_urls = self.search_direct_image_sites(genus, species, common_names, 150)
            all_urls.extend(direct_urls)
            print(f"  📊 직접 사이트: {len(direct_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ 직접 사이트 오류: {e}")
        
        # 3. Bing Images에서 수집 (마이크로소프트) - 증량
        print("  📥 Bing Images 검색 중...")
        try:
            bing_urls = self.search_bing_images(genus, species, common_names, 200)
            all_urls.extend(bing_urls)
            print(f"  📊 Bing: {len(bing_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ Bing 오류: {e}")
        
        # 4. Yandex Images에서 수집 (러시아 검색엔진) - 증량
        print("  📥 Yandex Images 검색 중...")
        try:
            yandex_urls = self.search_yandex_images(genus, species, common_names, 150)
            all_urls.extend(yandex_urls)
            print(f"  📊 Yandex: {len(yandex_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ Yandex 오류: {e}")
        
        # 5. iNaturalist에서 수집 (생물 관찰 플랫폼) - 증량
        print("  📥 iNaturalist 검색 중...")
        try:
            inaturalist_urls = self.search_inaturalist(genus, species, common_names, 120)
            all_urls.extend(inaturalist_urls)
            print(f"  📊 iNaturalist: {len(inaturalist_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ iNaturalist 오류: {e}")
        
        # 6. Flickr에서 수집 (사진 공유) - 증량
        print("  📥 Flickr 검색 중...")
        try:
            flickr_urls = self.search_flickr(genus, species, common_names, 100)
            all_urls.extend(flickr_urls)
            print(f"  📊 Flickr: {len(flickr_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ Flickr 오류: {e}")
        
        # 7. 수족관 사이트들에서 수집 (상업적 사이트)
        print("  📥 수족관 사이트 검색 중...")
        try:
            aquarium_urls = self.search_aquarium_sites(genus, species, common_names, 80)
            all_urls.extend(aquarium_urls)
            print(f"  📊 수족관 사이트: {len(aquarium_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ 수족관 사이트 오류: {e}")
        
        # 8. Pinterest에서 수집 (이미지 공유)
        print("  📥 Pinterest 검색 중...")
        try:
            pinterest_urls = self.search_pinterest(genus, species, common_names, 70)
            all_urls.extend(pinterest_urls)
            print(f"  📊 Pinterest: {len(pinterest_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ Pinterest 오류: {e}")
        
        # 9. Encyclopedia of Life에서 수집 (생물 백과사전)
        print("  📥 EOL 검색 중...")
        try:
            eol_urls = self.search_eol(genus, species, common_names, 60)
            all_urls.extend(eol_urls)
            print(f"  📊 EOL: {len(eol_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ EOL 오류: {e}")
        
        # 10. Wikipedia에서 수집 (백과사전)
        print("  📥 Wikipedia 검색 중...")
        try:
            wiki_urls = self.search_wikipedia(genus, species, common_names, 50)
            all_urls.extend(wiki_urls)
            print(f"  📊 Wikipedia: {len(wiki_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ Wikipedia 오류: {e}")
        
        # 11. GBIF에서 수집 (글로벌 생물다양성)
        print("  📥 GBIF 검색 중...")
        try:
            gbif_urls = self.search_gbif(genus, species, 40)
            all_urls.extend(gbif_urls)
            print(f"  📊 GBIF: {len(gbif_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ GBIF 오류: {e}")
        
        # 12. WoRMS에서 수집 (해양생물 등록소)
        print("  📥 WoRMS 검색 중...")
        try:
            worms_urls = self.search_marinespecies_org(genus, species, 50)
            all_urls.extend(worms_urls)
            print(f"  📊 WoRMS: {len(worms_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ WoRMS 오류: {e}")
        
        # 13. Reef2Reef 포럼에서 수집 (해수어 커뮤니티)
        print("  📥 Reef2Reef 검색 중...")
        try:
            reef2reef_urls = self.search_reef2reef(genus, species, common_names, 60)
            all_urls.extend(reef2reef_urls)
            print(f"  📊 Reef2Reef: {len(reef2reef_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ Reef2Reef 오류: {e}")
        
        # 14. DuckDuckGo Images에서 수집
        print("  📥 DuckDuckGo Images 검색 중...")
        try:
            duckduckgo_urls = self.search_duckduckgo_images(genus, species, common_names, 80)
            all_urls.extend(duckduckgo_urls)
            print(f"  📊 DuckDuckGo: {len(duckduckgo_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ DuckDuckGo 오류: {e}")
        
        # 15. Shutterstock에서 수집
        print("  📥 Shutterstock 검색 중...")
        try:
            shutterstock_urls = self.search_shutterstock(genus, species, common_names, 60)
            all_urls.extend(shutterstock_urls)
            print(f"  📊 Shutterstock: {len(shutterstock_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ Shutterstock 오류: {e}")
        
        # 16. Unsplash에서 수집
        print("  📥 Unsplash 검색 중...")
        try:
            unsplash_urls = self.search_unsplash(genus, species, common_names, 50)
            all_urls.extend(unsplash_urls)
            print(f"  📊 Unsplash: {len(unsplash_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ Unsplash 오류: {e}")
        
        # 17. Pexels에서 수집
        print("  📥 Pexels 검색 중...")
        try:
            pexels_urls = self.search_pexels(genus, species, common_names, 45)
            all_urls.extend(pexels_urls)
            print(f"  📊 Pexels: {len(pexels_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ Pexels 오류: {e}")
        
        # 18. Reddit 수족관 커뮤니티에서 수집
        print("  📥 Reddit 수족관 커뮤니티 검색 중...")
        try:
            reddit_urls = self.search_reddit_aquariums(genus, species, common_names, 40)
            all_urls.extend(reddit_urls)
            print(f"  📊 Reddit: {len(reddit_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ Reddit 오류: {e}")
        
        # 19. Instagram 해시태그에서 수집
        print("  📥 Instagram 해시태그 검색 중...")
        try:
            instagram_urls = self.search_instagram_hashtags(genus, species, common_names, 35)
            all_urls.extend(instagram_urls)
            print(f"  📊 Instagram: {len(instagram_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ Instagram 오류: {e}")
        
        # 20. 수족관 포럼들에서 수집
        print("  📥 수족관 포럼 검색 중...")
        try:
            forum_urls = self.search_aquarium_forums(genus, species, common_names, 50)
            all_urls.extend(forum_urls)
            print(f"  📊 수족관 포럼: {len(forum_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ 수족관 포럼 오류: {e}")
        
        # 21. YouTube 썸네일에서 수집
        print("  📥 YouTube 썸네일 검색 중...")
        try:
            youtube_urls = self.search_youtube_thumbnails(genus, species, common_names, 30)
            all_urls.extend(youtube_urls)
            print(f"  📊 YouTube: {len(youtube_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ YouTube 오류: {e}")
        
        # 22. 학술 자료에서 수집
        print("  📥 학술 자료 검색 중...")
        try:
            academic_urls = self.search_academic_sources(genus, species, 25)
            all_urls.extend(academic_urls)
            print(f"  📊 학술 자료: {len(academic_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ 학술 자료 오류: {e}")
        
        # 23. 추가 검색어로 Google 재검색 (특수 상황)
        print("  📥 추가 검색어로 재검색 중...")
        try:
            additional_urls = self.search_with_additional_terms(genus, species, common_names, 100)
            all_urls.extend(additional_urls)
            print(f"  📊 추가 검색: {len(additional_urls)}개 발견")
        except Exception as e:
            print(f"  ❌ 추가 검색 오류: {e}")
        
        # 중복 제거 및 필터링
        unique_urls = []
        seen_urls = set()
        
        for url in all_urls:
            if url not in seen_urls and self.is_valid_image_url(url):
                # 문제가 있는 서버 스킵
                if any(problem_server in url for problem_server in ['mediaphoto.mnhn.fr', 'timeout-prone-server.com']):
                    continue
                unique_urls.append(url)
                seen_urls.add(url)
        
        print(f"  🎯 총 {len(unique_urls)}개 고유 이미지 발견 (필터링 후)")
        print(f"  📋 원본 URL 수: {len(all_urls)}, 중복 제거 후: {len(unique_urls)}")
        
        # 다운로드할 URL 수 결정
        download_count = min(len(unique_urls), target_images)
        print(f"  🎯 다운로드 시도할 이미지 수: {download_count}")
        
        # 이미지 다운로드 (병렬 처리 고려)
        downloaded = 0
        failed = 0
        
        for i, url in enumerate(unique_urls[:download_count]):
            filename = f"{genus}_{species}_{i+1:03d}.jpg"
            save_path = species_path / filename
            
            try:
                if self.download_image(url, save_path):
                    downloaded += 1
                    if downloaded % 20 == 0:
                        print(f"    📥 {downloaded}장 다운로드 완료...")
                else:
                    failed += 1
                    # 실패 원인을 더 자세히 로그
                    if failed <= 10:  # 처음 10개 실패만 로그
                        print(f"    ❌ 다운로드 실패: {url[:60]}...")
            except Exception as e:
                failed += 1
                if failed <= 10:  # 처음 10개 예외만 로그
                    print(f"    💥 예외 발생: {str(e)[:50]}...")
                elif failed % 50 == 0:
                    print(f"    ⚠️ {failed}개 다운로드 실패...")
            
            # 적응적 지연 (더 짧게 조정)
            success_rate = downloaded / (downloaded + failed) if (downloaded + failed) > 0 else 1
            delay = 0.1 if success_rate > 0.7 else 0.3 if success_rate > 0.4 else 0.6
            time.sleep(delay)
        
        # 품질 통계 계산
        quality_rate = (self.quality_stats['quality_passed'] / max(1, self.quality_stats['total_checked'])) * 100
        
        print(f"  ✅ {genus} {species}: {downloaded}장 다운로드 완료")
        print(f"     📊 품질 통과율: {quality_rate:.1f}% ({self.quality_stats['quality_passed']}/{self.quality_stats['total_checked']})")
        if self.quality_stats['quality_failed'] > 0:
            print(f"     🚫 품질 불량: 블러({self.quality_stats['blur_rejected']}) 밝기({self.quality_stats['brightness_rejected']}) 대비({self.quality_stats['contrast_rejected']}) 노이즈({self.quality_stats['noise_rejected']}) 해상도({self.quality_stats['resolution_rejected']})")
        
        self.stats['total_downloaded'] += downloaded
        self.stats['total_errors'] += failed
        
        # 품질 통계 초기화 (다음 종을 위해)
        self.quality_stats = {
            'total_checked': 0,
            'quality_passed': 0,
            'quality_failed': 0,
            'blur_rejected': 0,
            'brightness_rejected': 0,
            'contrast_rejected': 0,
            'noise_rejected': 0,
            'resolution_rejected': 0
        }
        
        return downloaded
    
    def scrape_all_fish(self):
        """모든 물고기 대량 스크래핑 (ML 학습용)"""
        print("🐠 해수어 이미지 대량 스크래핑 시작!")
        print(f"📊 총 {self.count_species()}종 처리 예정")
        print("🎯 종당 목표: 1500장 (대량 수집 후 고품질 선별)")
        print("🔍 23개 소스: FishBase, Google, Bing, Yandex, iNaturalist, Flickr,")
        print("             수족관사이트, Pinterest, EOL, Wikipedia, GBIF, WoRMS,")
        print("             Reef2Reef, DuckDuckGo, Shutterstock, Unsplash, Pexels,")
        print("             Reddit, Instagram, 수족관포럼, YouTube, 학술자료")
        print("📊 전략: 대량 수집 → 품질 필터링 → 오토 라벨링 → ML 학습")
        
        total_species = 0
        
        for class_name, orders in self.fish_taxonomy.items():
            print(f"\n📁 {class_name} 처리 중...")
            
            for order_name, genera in orders.items():
                print(f"  📂 {order_name}")
                
                for genus_name, species_dict in genera.items():
                    for species_name, common_names in species_dict.items():
                        total_species += 1
                        try:
                            print(f"\n🔄 [{total_species}/{self.count_species()}] {genus_name} {species_name}")
                            downloaded = self.scrape_species(genus_name, species_name, common_names, 1500)
                            
                            # 성공률에 따른 적응적 지연 (1500장 기준)
                            if downloaded > 1200:
                                print(f"  🎉 우수한 수집률: {downloaded}장 (80%+)")
                                time.sleep(1)  # 성공적이면 짧은 지연
                            elif downloaded > 900:
                                print(f"  ✅ 양호한 수집률: {downloaded}장 (60%+)")
                                time.sleep(2)  # 보통이면 중간 지연
                            elif downloaded > 600:
                                print(f"  ⚠️ 보통 수집률: {downloaded}장 (40%+)")
                                time.sleep(3)  # 낮으면 긴 지연
                            elif downloaded > 300:
                                print(f"  ❌ 낮은 수집률: {downloaded}장 (20%+)")
                                time.sleep(4)  # 매우 낮으면 더 긴 지연
                            else:
                                print(f"  💥 매우 낮은 수집률: {downloaded}장 (<20%)")
                                time.sleep(5)  # 극도로 낮으면 가장 긴 지연
                                
                        except Exception as e:
                            print(f"  💥 {genus_name} {species_name} 치명적 오류: {e}")
                            self.stats['total_errors'] += 1
                            time.sleep(5)  # 오류 시 긴 지연
        
        # 최종 통계
        avg_per_species = self.stats['total_downloaded'] / total_species if total_species > 0 else 0
        success_rate = (total_species - self.stats['total_errors']) / total_species * 100 if total_species > 0 else 0
        
        print(f"\n🎉 대량 스크래핑 완료!")
        print("=" * 60)
        print(f"📊 총 다운로드: {self.stats['total_downloaded']:,}장")
        print(f"🐠 처리된 종: {total_species}종")
        print(f"📈 평균 종당: {avg_per_species:.1f}장")
        print(f"✅ 성공률: {success_rate:.1f}%")
        print(f"⚠️ 총 오류: {self.stats['total_errors']}개")
        print("=" * 60)
    
    def create_training_dataset(self, images_per_class=50):
        """훈련용 데이터셋 생성"""
        print(f"🎯 훈련용 데이터셋 생성 (클래스당 {images_per_class}장)")
        
        # 클래스별 폴더 생성
        for class_name in self.fish_taxonomy.keys():
            class_dir = self.train_dir / class_name
            class_dir.mkdir(exist_ok=True)
            
            # 해당 클래스의 모든 이미지 수집
            all_images = []
            for img_path in self.dataset_dir.rglob("*.jpg"):
                all_images.append(img_path)
            
            if len(all_images) == 0:
                print(f"  ⚠️ {class_name}: 이미지 없음")
                continue
            
            # 랜덤 샘플링
            selected_count = min(images_per_class, len(all_images))
            selected_images = random.sample(all_images, selected_count)
            
            # 복사
            for i, img_path in enumerate(selected_images, 1):
                new_name = f"{class_name}_{i:03d}.jpg"
                new_path = class_dir / new_name
                shutil.copy2(img_path, new_path)
            
            print(f"  ✅ {class_name}: {selected_count}장 복사 완료")
        
        print("🎉 훈련용 데이터셋 생성 완료!")
    
    def analyze_dataset(self):
        """데이터셋 분석"""
        print("📊 데이터셋 분석 중...")
        
        total_images = 0
        species_stats = {}
        
        for species_dir in self.dataset_dir.iterdir():
            if species_dir.is_dir():
                images = list(species_dir.glob("*.jpg"))
                count = len(images)
                species_stats[species_dir.name] = count
                total_images += count
        
        print(f"\n📈 분석 결과:")
        print(f"  총 이미지: {total_images}장")
        print(f"  총 종 수: {len(species_stats)}종")
        
        if species_stats:
            avg_images = total_images / len(species_stats)
            print(f"  평균 종당 이미지: {avg_images:.1f}장")
            
            # 상위 5종
            top_species = sorted(species_stats.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"\n🏆 이미지가 많은 상위 5종:")
            for species, count in top_species:
                print(f"    {species}: {count}장")
    
    def count_species(self):
        """총 종 수 계산"""
        count = 0
        for class_name, orders in self.fish_taxonomy.items():
            for order_name, genera in orders.items():
                for genus_name, species_dict in genera.items():
                    count += len(species_dict)
        return count
    
    # 고급 CLI 인터페이스를 위한 메서드들
    def restore_session(self, session_id: str) -> bool:
        """세션 복원 (임시 구현)"""
        print(f"세션 복원 시도: {session_id}")
        # 실제로는 session_manager를 사용해야 함
        return False
    
    def start_scraping_session(self, target_species, images_per_species: int):
        """스크래핑 세션 시작"""
        print(f"스크래핑 세션 시작: {len(target_species)}종, 종당 {images_per_species}장")
        self.target_species = target_species
        self.images_per_species = images_per_species
    
    def run_scraping(self) -> dict:
        """스크래핑 실행"""
        print("스크래핑 실행 중...")
        
        total_downloaded = 0
        species_processed = 0
        
        if hasattr(self, 'target_species'):
            for species_info in self.target_species:
                genus = species_info.genus
                species = species_info.species
                common_names = species_info.common_names
                
                downloaded = self.scrape_species(genus, species, common_names, self.images_per_species)
                total_downloaded += downloaded
                species_processed += 1
        else:
            # 기본 동작: 모든 종 스크래핑
            self.scrape_all_fish()
            total_downloaded = self.stats.get('total_downloaded', 0)
            species_processed = self.stats.get('species_processed', 0)
        
        return {
            'total_downloaded': total_downloaded,
            'duration': 0,  # 실제로는 시간 측정 필요
            'species_processed': species_processed
        }
    
    def get_statistics(self) -> dict:
        """통계 반환"""
        return getattr(self, 'stats', {
            'total_downloaded': 0,
            'total_errors': 0,
            'species_processed': 0
        })

    def search_simple_google(self, genus, species, common_names=None, max_images=200):
        """간단하고 효과적인 Google 검색"""
        images = []
        
        # 간단하지만 효과적인 검색어들
        search_terms = [
            f"{genus} {species}",
            f"{genus} {species} fish",
            f"{genus} {species} marine",
        ]
        
        if common_names:
            search_terms.extend(common_names[:2])
        
        for term in search_terms:
            try:
                # 더 간단한 Google 검색 URL
                search_url = f"https://www.google.com/search?q={quote(term)}&tbm=isch&safe=off"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
                
                response = self.session.get(search_url, headers=headers, timeout=20)
                
                if response.status_code == 200:
                    import re
                    # 모든 가능한 이미지 URL 패턴
                    all_patterns = [
                        r'imgurl=([^&]*\.(?:jpg|jpeg|png|gif))',
                        r'"ou":"([^"]*\.(?:jpg|jpeg|png|gif))"',
                        r'src="([^"]*\.(?:jpg|jpeg|png|gif))"',
                        r'https://[^"\s<>]*\.(?:jpg|jpeg|png|gif)',
                    ]
                    
                    found_urls = []
                    for pattern in all_patterns:
                        matches = re.findall(pattern, response.text, re.IGNORECASE)
                        found_urls.extend(matches)
                    
                    # URL 디코딩 및 정리
                    from urllib.parse import unquote
                    cleaned_urls = []
                    for url in found_urls:
                        try:
                            clean_url = unquote(url)
                            if clean_url.startswith('http') and any(ext in clean_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                                cleaned_urls.append(clean_url)
                        except:
                            continue
                    
                    # 중복 제거
                    cleaned_urls = list(set(cleaned_urls))
                    
                    for url in cleaned_urls[:15]:  # 검색어당 15개
                        if len(images) >= max_images:
                            break
                        if self.is_valid_image_url(url):
                            images.append(url)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    간단 Google 검색 오류: {e}")
                continue
        
        return images[:max_images]

    def search_direct_image_sites(self, genus, species, common_names=None, max_images=150):
        """직접 이미지 사이트들에서 검색"""
        images = []
        
        # 이미지가 많은 사이트들
        image_sites = [
            "pixabay.com",
            "pexels.com", 
            "unsplash.com",
            "wikimedia.org",
            "commons.wikimedia.org",
            "imgur.com",
            "500px.com",
            "deviantart.com"
        ]
        
        search_terms = [f"{genus} {species}"]
        if common_names:
            search_terms.extend(common_names[:2])
        
        for site in image_sites:
            for term in search_terms[:2]:  # 각 사이트당 2개 검색어만
                try:
                    # Google을 통한 사이트별 검색
                    search_url = f"https://www.google.com/search?q=site:{site}+{quote(term)}+fish&tbm=isch"
                    response = self.session.get(search_url, timeout=15)
                    
                    if response.status_code == 200:
                        import re
                        img_urls = re.findall(r'"ou":"([^"]*\.(?:jpg|jpeg|png|gif))"', response.text)
                        
                        for url in img_urls[:5]:  # 사이트당 5개
                            if len(images) >= max_images:
                                break
                            if self.is_valid_image_url(url):
                                images.append(url)
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    continue
                
                if len(images) >= max_images:
                    break
            
            if len(images) >= max_images:
                break
        
        return images[:max_images]


def main():
    """메인 함수"""
    scraper = MarineScraper()
    
    while True:
        print("\n" + "="*60)
        print("🐠 고성능 해수어 이미지 대량 스크래퍼 v2.0")
        print("="*60)
        print("1. 전체 이미지 대량 다운로드 (종당 1500장 목표)")
        print("2. 훈련용 데이터셋 생성 (고품질 선별)")
        print("3. 데이터셋 분석 및 통계")
        print("4. 종료")
        print("-"*60)
        print("💡 23개 소스에서 대량 수집 → 품질 필터링 → 오토 라벨링")
        print("🔍 소스: Google, Bing, Yandex, DuckDuckGo, Shutterstock, Unsplash,")
        print("       Pexels, Reddit, Instagram, YouTube, 학술자료, 수족관포럼 등")
        print("-"*60)
        
        choice = input("선택하세요 (1-4): ").strip()
        
        if choice == '1':
            scraper.scrape_all_fish()
        
        elif choice == '2':
            try:
                images_per_class = input("클래스당 이미지 수 (기본값: 500): ").strip()
                if images_per_class:
                    images_per_class = int(images_per_class)
                else:
                    images_per_class = 500
                
                scraper.create_training_dataset(images_per_class)
            except ValueError:
                print("❌ 올바른 숫자를 입력해주세요.")
        
        elif choice == '3':
            scraper.analyze_dataset()
        
        elif choice == '4':
            print("👋 프로그램을 종료합니다.")
            break
        
        else:
            print("❌ 잘못된 선택입니다.")


    def search_with_additional_terms(self, genus, species, common_names=None, max_images=100):
        """추가 검색어로 더 많은 이미지 수집 (해양생물 특화)"""
        images = []
        
        # 해양생물 특화 검색어들
        marine_terms = [
            "marine fish", "saltwater fish", "coral reef fish", "tropical fish",
            "aquarium fish", "reef tank", "marine aquarium", "underwater",
            "diving photo", "scuba diving", "snorkeling", "reef life",
            "ocean fish", "sea fish", "marine life", "coral fish"
        ]
        
        # 기본 검색어들
        search_terms = [f"{genus} {species}"]
        if common_names:
            search_terms.extend(common_names[:3])
        
        # 해양생물 특화 검색어와 조합
        for base_term in search_terms[:2]:  # 처음 2개만 사용
            for marine_term in marine_terms[:8]:  # 처음 8개만 사용
                combined_term = f"{base_term} {marine_term}"
                
                try:
                    search_url = f"https://www.google.com/search?q={quote(combined_term)}&tbm=isch"
                    response = self.session.get(search_url, timeout=15)
                    
                    if response.status_code == 200:
                        import re
                        img_urls = re.findall(r'"ou":"([^"]*\.(?:jpg|jpeg|png|gif))"', response.text)
                        
                        for url in img_urls[:5]:  # 각 검색어당 5개씩
                            if self.is_valid_image_url(url):
                                images.append(url)
                    
                    time.sleep(0.5)  # 요청 간격
                    
                except Exception as e:
                    continue
        
        return images[:max_images]

    def search_youtube_thumbnails(self, genus, species, common_names=None, max_images=30):
        """YouTube 썸네일에서 이미지 수집"""
        images = []
        
        search_terms = [f"{genus} {species}"]
        if common_names:
            search_terms.extend(common_names[:2])
        
        for term in search_terms:
            try:
                # YouTube 검색
                search_url = f"https://www.youtube.com/results?search_query={quote(term + ' fish aquarium')}"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    import re
                    # YouTube 썸네일 패턴
                    thumbnail_urls = re.findall(r'https://i\.ytimg\.com/vi/[^/]+/[^"]*\.jpg', response.text)
                    
                    for url in thumbnail_urls[:15]:
                        # 고화질 썸네일로 변환
                        hq_url = url.replace('/default.jpg', '/hqdefault.jpg').replace('/mqdefault.jpg', '/hqdefault.jpg')
                        images.append(hq_url)
                
                time.sleep(1)
                
            except Exception as e:
                continue
        
        return images[:max_images]

    def search_academic_sources(self, genus, species, max_images=25):
        """학술 자료에서 이미지 수집"""
        images = []
        
        # 학술 사이트들
        academic_sites = [
            "researchgate.net",
            "scholar.google.com", 
            "ncbi.nlm.nih.gov",
            "biodiversitylibrary.org",
            "journals.plos.org",
            "nature.com",
            "sciencedirect.com"
        ]
        
        for site in academic_sites:
            try:
                search_url = f"https://www.google.com/search?q=site:{site}+{quote(genus + ' ' + species)}+image&tbm=isch"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    import re
                    img_urls = re.findall(r'"ou":"([^"]*\.(?:jpg|jpeg|png|gif))"', response.text)
                    
                    for url in img_urls[:4]:  # 각 사이트당 4개씩
                        if self.is_valid_image_url(url):
                            images.append(url)
                
                time.sleep(1)
                
            except Exception as e:
                continue
        
        return images[:max_images]


if __name__ == "__main__":
    main()