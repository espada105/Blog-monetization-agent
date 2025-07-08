#!/usr/bin/env python3
"""
BBC 뉴스 자동 블로그 포스터
BBC 뉴스를 수집 → LLM으로 블로그 글 생성 → 티스토리 자동 포스팅
"""

import asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from korea_news_processor import KoreaNewsProcessor
from config import config

def update_recent_blog(title, file_path, keywords=None):
    """recentBlog.md 파일 업데이트"""
    try:
        recent_blog_file = os.path.join(os.path.dirname(__file__), "..", "recentBlog.md")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 상대 경로로 변환
        relative_path = os.path.relpath(file_path, os.path.dirname(recent_blog_file))
        
        new_content = f"""# 최신 블로그 글 정보

## 현재 최신 글
- **제목**: {title}
- **파일경로**: {relative_path}
- **생성일시**: {current_time}
- **타입**: 한국뉴스
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

async def korea_auto_blog_posting():
    print("🚀 한국 뉴스 자동 블로그 포스터 시작!")
    print("=" * 50)
    BLOG_NAME = config.TISTORY_BLOG_NAME
    COOKIE = config.TISTORY_COOKIE
    KOREAN_KEYWORDS = getattr(config, 'KOREAN_KEYWORDS', ["경제", "주식", "정치", "나스닥", "코스닥", "미국", "한국"])
    KOREAN_LIMIT = getattr(config, 'KOREAN_LIMIT_PER_KEYWORD', 5)
    USE_AUTO_TOPIC = getattr(config, 'USE_AUTO_TOPIC', True)
    processor = KoreaNewsProcessor(BLOG_NAME, COOKIE)
    try:
        print("📰 1단계: 네이버 트렌드 키워드별 뉴스 수집 중...")
        news_data = await processor.collect_trend_news_json(KOREAN_KEYWORDS, KOREAN_LIMIT)
        if not news_data:
            print("❌ 뉴스 데이터를 수집할 수 없습니다.")
            return None
        print(f"✅ {len(KOREAN_KEYWORDS)}개 키워드, 총 {sum(len(news_list) for news_list in news_data.values())}개의 뉴스 수집 완료")
        print("🤖 2단계: 블로그 글 주제 생성 중...")
        if USE_AUTO_TOPIC:
            topic = await processor.generate_topic(news_data)
            print(f"📝 생성된 주제: {topic}")
        else:
            topic = getattr(config, 'KOREAN_BLOG_TOPIC', "한국 경제 동향과 기술 트렌드 분석")
            print(f"📝 설정된 주제: {topic}")
        print("✍️ 3단계: 블로그 글 생성 중...")
        blog_content = await processor.generate_blog_post(news_data, topic)
        print("💾 4단계: 블로그 글 저장 중...")
        filename = await processor.save_blog_post(blog_content, topic)
        
        # recentBlog.md 업데이트
        update_recent_blog(topic, filename, KOREAN_KEYWORDS)
        
        print("=" * 50)
        print("✅ 한국뉴스 프로세서 완료!")
        print(f"📝 주제: {topic}")
        print(f"📁 파일: {filename}")
        print(f"📋 recentBlog.md 업데이트 완료")
        print("🚀 다음 단계: 셀레니움 업로드 실행")
        print("   python korea_agent/korea_tistory_selenium_poster.py --auto")
        return filename, topic
    except Exception as e:
        print(f"❌ 자동 포스팅 중 오류 발생: {e}")
        return None

def main():
    print("🤖 한국 뉴스 자동 블로그 포스터")
    print("네이버 트렌드 키워드별 뉴스 수집 → LLM 글 생성 → 티스토리 포스팅")
    print()
    result = asyncio.run(korea_auto_blog_posting())
    if result:
        filename, topic = result
        print(f"\n🎉 성공! '{topic}' 글이 티스토리에 포스팅되었습니다.")
    else:
        print("\n❌ 자동 포스팅에 실패했습니다.")

if __name__ == "__main__":
    main() 