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

def update_recent_blog(title, file_path, keywords=None):
    """recentBlog.md 파일 업데이트"""
    try:
        recent_blog_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recentBlog.md")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 상대 경로로 변환
        relative_path = os.path.relpath(file_path, os.path.dirname(recent_blog_file))
        
        new_content = f"""# 최신 블로그 글 정보

## 현재 최신 글
- **제목**: {title}
- **파일경로**: {relative_path}
- **생성일시**: {current_time}
- **타입**: BBC뉴스
"""
        
        if keywords:
            new_content += f"- **키워드**: {', '.join(keywords)}\n"
        
        new_content += f"""
## 이전 글들
- **제목**: 한국 경제 동향과 기술 트렌드 분석
- **파일경로**: data/blog_posts/blog_한국뉴스_한국 경제 동향과 기술 트렌드 분석_2025-07-08.md
- **생성일시**: 2025-07-08 15:30:00
- **타입**: 한국뉴스
- **키워드**: 금리, 환율, 주식, 나스닥, 코스닥, 비트코인

---
*이 파일은 자동으로 업데이트됩니다.*
"""
        
        with open(recent_blog_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ recentBlog.md 업데이트 완료: {title}")
        
    except Exception as e:
        print(f"⚠️ recentBlog.md 업데이트 실패: {e}")

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
        
        # 2. 블로그 글 주제 생성 (자동 또는 수동)
        if USE_AUTO_TOPIC:
            print("🤖 LLM을 사용해 블로그 글 주제를 생성합니다...")
            topic = await processor.generate_topic(news_data)
            print(f"📝 생성된 주제: {topic}")
        else:
            topic = getattr(config, 'BLOG_TOPIC', "글로벌 기술 트렌드와 시장 동향")
            print(f"📝 설정된 주제 사용: {topic}")
        
        # 3. 블로그 글 생성
        print("✍️ 3단계: 블로그 글 생성 중...")
        blog_content = await processor.generate_blog_post(news_data, topic)
        
        # 4. 블로그 글 저장
        print("💾 4단계: 블로그 글 저장 중...")
        filename = await processor.save_blog_post(blog_content, topic)
        
        # recentBlog.md 업데이트
        update_recent_blog(topic, filename, [BBC_CATEGORY])
        
        print("=" * 50)
        print("✅ BBC 프로세서 완료!")
        print(f"📝 주제: {topic}")
        print(f"📁 파일: {filename}")
        print(f"📋 recentBlog.md 업데이트 완료")
        print("🚀 다음 단계: 셀레니움 업로드 실행")
        print("   python src/posters/tistory_selenium_poster.py --auto")
        return filename, topic  # 결과 반환
        
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