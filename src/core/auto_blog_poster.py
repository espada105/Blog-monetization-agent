#!/usr/bin/env python3
"""
BBC 뉴스 자동 블로그 포스터
BBC 뉴스를 수집 → LLM으로 블로그 글 생성 → 티스토리 자동 포스팅
"""

import asyncio
import sys
import os
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.bbc_news_processor import BBCNewsProcessor
from config import config

async def auto_blog_posting():
    """BBC 뉴스 수집부터 티스토리 포스팅까지 완전 자동화"""
    
    print("🚀 BBC 뉴스 자동 블로그 포스터 시작!")
    print("=" * 50)
    
    # 설정 가져오기
    BLOG_NAME = config.TISTORY_BLOG_NAME
    COOKIE = config.TISTORY_COOKIE
    BBC_CATEGORY = config.BBC_CATEGORY
    BBC_LIMIT = config.BBC_LIMIT_PER_CATEGORY
    USE_AUTO_TOPIC = getattr(config, 'USE_AUTO_TOPIC', True)
    
    # BBC 뉴스 프로세서 초기화
    processor = BBCNewsProcessor(BLOG_NAME, COOKIE)
    
    try:
        # 1. BBC 뉴스 수집 및 JSON 저장
        print("📰 1단계: BBC 뉴스 수집 중...")
        news_data = await processor.collect_and_save_json(BBC_CATEGORY, BBC_LIMIT)
        
        if not news_data:
            print("❌ 뉴스 데이터를 수집할 수 없습니다.")
            return None
        
        print(f"✅ {len(news_data)}개의 뉴스 수집 완료")
        
        # 2. 블로그 글 주제 생성
        print("🤖 2단계: 블로그 글 주제 생성 중...")
        if USE_AUTO_TOPIC:
            topic = await processor.generate_topic(news_data)
            print(f"📝 생성된 주제: {topic}")
        else:
            topic = getattr(config, 'BLOG_TOPIC', "글로벌 기술 트렌드와 시장 동향")
            print(f"📝 설정된 주제: {topic}")
        
        # 3. 블로그 글 생성
        print("✍️ 3단계: 블로그 글 생성 중...")
        blog_content = await processor.generate_blog_post(news_data, topic)
        
        # 4. 블로그 글 저장
        print("💾 4단계: 블로그 글 저장 중...")
        filename = await processor.save_blog_post(blog_content, topic)
        
        # 5. 티스토리 자동 포스팅
        print("🚀 5단계: 티스토리 자동 포스팅 중...")
        result = await processor.post_to_tistory(
            filename,
            category_id=getattr(config, 'TISTORY_CATEGORY_ID', None),
            tags=getattr(config, 'TISTORY_TAGS', None)
        )
        
        if result:
            print("🎉 티스토리 API 포스팅 완료!")
        
        # 6. 셀레니움 자동 포스팅 (백업)
        print("🤖 6단계: 셀레니움 자동 포스팅 중...")
        try:
            import subprocess
            
            # 셀레니움 포스터 경로 설정
            poster_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src', 'posters', 'tistory_selenium_poster.py')
            
            cmd = [
                sys.executable, poster_path,
                "--file", filename,
                "--auto"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("🎉 셀레니움 자동 포스팅 완료!")
                print(f"🌐 블로그 확인: https://aigent-hong.tistory.com")
            else:
                print(f"⚠️ 셀레니움 포스팅 중 오류: {result.stderr}")
                
        except Exception as e:
            print(f"❌ 셀레니움 포스팅 실패: {e}")
        
        print("=" * 50)
        print("✅ 모든 과정 완료!")
        print(f"📝 주제: {topic}")
        print(f"📁 파일: {filename}")
        print(f"🌐 블로그: https://aigent-hong.tistory.com")
        
        return filename, topic
        
    except Exception as e:
        print(f"❌ 자동 포스팅 중 오류 발생: {e}")
        return None

def main():
    """메인 함수"""
    print("🤖 BBC 뉴스 자동 블로그 포스터")
    print("BBC 뉴스 수집 → LLM 글 생성 → 티스토리 포스팅")
    print()
    
    # 비동기 실행
    result = asyncio.run(auto_blog_posting())
    
    if result:
        filename, topic = result
        print(f"\n🎉 성공! '{topic}' 글이 티스토리에 포스팅되었습니다.")
    else:
        print("\n❌ 자동 포스팅에 실패했습니다.")

if __name__ == "__main__":
    main() 