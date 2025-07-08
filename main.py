#!/usr/bin/env python3
"""
BBC 뉴스 자동 블로그 포스터 - 메인 실행 파일
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(__file__))

from src.core.auto_blog_poster import main

if __name__ == "__main__":
    main() 