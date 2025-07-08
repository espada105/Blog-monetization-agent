#!/usr/bin/env python3
"""
BBC 뉴스 자동 포스팅 실행기
1. bbc_news_processor.py 실행 (뉴스 수집 + 블로그 글 생성)
2. tistory_selenium_poster.py 실행 (티스토리 자동 포스팅)
"""

import subprocess
import sys
import os
import time

def run_bbc_news_processor():
    """BBC 뉴스 프로세서 실행"""
    print("=" * 50)
    print("📰 1단계: BBC 뉴스 프로세서 실행")
    print("=" * 50)
    
    try:
        # 프로젝트 루트 경로 계산
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        processor_path = os.path.join(project_root, "src", "core", "bbc_news_processor.py")
        
        result = subprocess.run([
            sys.executable, processor_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(" BBC 뉴스 프로세서 실행 완료!")
            return True
        else:
            print(f" BBC 뉴스 프로세서 실행 실패: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[FAIL] BBC 뉴스 수집 실패: {e}")
        return False

def run_tistory_selenium_poster():
    """티스토리 셀레니움 포스터 실행"""
    print("=" * 50)
    print("🤖 2단계: 티스토리 셀레니움 포스터 실행")
    print("=" * 50)
    
    try:
        # 프로젝트 루트 경로 계산
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        poster_path = os.path.join(project_root, "src", "posters", "tistory_selenium_poster.py")
        
        result = subprocess.run([
            sys.executable, poster_path, "--auto"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(" 티스토리 셀레니움 포스터 실행 완료!")
            return True
        else:
            print(f" 티스토리 셀레니움 포스터 실행 실패: {result.stderr}")
            return False
            
    except Exception as e:
        print(f" 티스토리 셀레니움 포스터 실행 중 오류: {e}")
        return False

def main():
    """메인 실행 함수"""
    print(" BBC 뉴스 자동 포스팅 시작!")
    print("순서: BBC 뉴스 수집 → 블로그 글 생성 → 티스토리 포스팅")
    print()
    
    # 1단계: BBC 뉴스 프로세서 실행
    if not run_bbc_news_processor():
        print(" 1단계 실패로 중단합니다.")
        return False
    
    print("\n 2단계 실행 전 잠시 대기...")
    time.sleep(2)
    
    # 2단계: 티스토리 셀레니움 포스터 실행
    if not run_tistory_selenium_poster():
        print(" 2단계 실패로 중단합니다.")
        return False
    
    print("\n" + "=" * 50)
    print(" 모든 과정 완료!")
    print(" 블로그 확인: https://aigent-hong.tistory.com")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n 자동 포스팅이 성공적으로 완료되었습니다!")
    else:
        print("\n 자동 포스팅에 실패했습니다.") 