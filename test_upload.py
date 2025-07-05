import json
import asyncio
from bbc_news_processor import BBCNewsProcessor
import config

async def test_upload_from_json():
    """기존 JSON 파일을 사용해서 티스토리 자동 포스팅 테스트"""
    
    # 설정
    BLOG_NAME = config.TISTORY_BLOG_NAME
    COOKIE = config.TISTORY_COOKIE
    CATEGORY_ID = config.TISTORY_CATEGORY_ID
    TAGS = getattr(config, 'TISTORY_TAGS', None)
    USE_AUTO_TOPIC = getattr(config, 'USE_AUTO_TOPIC', True)
    DEFAULT_TOPIC = getattr(config, 'BLOG_TOPIC', "글로벌 기술 트렌드와 시장 동향")
    
    # BBC 뉴스 프로세서 초기화
    processor = BBCNewsProcessor(BLOG_NAME, COOKIE)
    
    try:
        # 1. 기존 JSON 파일 읽기
        print("📖 기존 JSON 파일 읽는 중...")
        with open("bbc_news_json/bbc_news_all_2025-07-05.json", "r", encoding="utf-8") as f:
            news_data = json.load(f)
        
        print(f"📰 읽은 뉴스 개수: {len(news_data)}개")
        
        # 2. 블로그 글 주제 생성 (자동 또는 수동)
        if USE_AUTO_TOPIC:
            print("🤖 LLM을 사용해 블로그 글 주제를 생성합니다...")
            topic = await processor.generate_topic(news_data)
            print(f"📝 생성된 주제: {topic}")
        else:
            topic = DEFAULT_TOPIC
            print(f"📝 설정된 주제 사용: {topic}")
        
        # 3. 블로그 글 생성
        print("✍️ 블로그 글 생성 중...")
        blog_content = await processor.generate_blog_post(news_data, topic)
        
        # 4. 블로그 글 저장
        print("💾 블로그 글 저장 중...")
        filename = await processor.save_blog_post(blog_content, topic)
        
        # 5. 티스토리 자동 포스팅
        if processor.tistory_poster:
            print("🚀 티스토리 포스팅 시작...")
            result = await processor.post_to_tistory(
                filename,
                category_id=CATEGORY_ID,
                tags=TAGS
            )
            
            if result:
                print("🎉 티스토리 포스팅 완료!")
                print(f"📝 주제: {topic}")
                print(f"📁 파일: {filename}")
            else:
                print("❌ 티스토리 포스팅 실패")
        else:
            print("❌ 티스토리 설정이 없습니다.")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(test_upload_from_json()) 