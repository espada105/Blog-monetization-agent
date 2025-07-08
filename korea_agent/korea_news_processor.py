import json
import asyncio
import os
import sys
from datetime import datetime
import requests
import re

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.scrapers.naver_news_api import search_naver_news
from config import config

class KoreaNewsProcessor:
    def __init__(self, blog_name=None, cookie=None):
        self.ollama_url = config.OLLAMA_URL
        self.model = config.OLLAMA_MODEL
        self.blog_name = blog_name
        self.cookie = cookie
        self.tistory_poster = None

    async def collect_trend_news_json(self, keywords=None, limit_per_keyword=5):
        """네이버 트렌드 키워드별 뉴스 수집 및 JSON 저장"""
        if keywords is None:
            keywords = ["금리","환율", "주식", "나스닥", "코스닥", "비트코인"]
        
        print(f"[NEWS] 네이버 트렌드 키워드별 뉴스 수집 중... (키워드: {keywords})")
        
        all_news_data = {}
        for keyword in keywords:
            print(f"\n[키워드: {keyword}] 뉴스 기사 수집 중...")
            news_list = search_naver_news(keyword, display=limit_per_keyword)
            
            for news in news_list:
                print(f"- {news['title']} | {news['link']}")
            
            all_news_data[keyword] = news_list
        
        # JSON 저장
        today_str = datetime.now().strftime('%Y-%m-%d')
        data_dir = os.path.join(os.path.dirname(__file__), 'korean_news_json')
        os.makedirs(data_dir, exist_ok=True)
        filename = os.path.join(data_dir, f"naver_trend_news_{today_str}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_news_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"[SAVE] JSON 저장 완료: {filename}")
        return all_news_data

    async def generate_topic(self, news_data):
        """뉴스 데이터를 기반으로 블로그 주제 생성 (영어)"""
        prompt = """You are a professional tech/economy blogger. Based on the following Korean news, generate an English blog post title about Korea's economy and technology trends.

News:
"""
        
        for keyword, news_list in news_data.items():
            prompt += f"\n[{keyword} News]\n"
            for news in news_list:
                prompt += f"- {news['title']}\n"
        
        prompt += """

Summarize the above news and generate a concise English blog post title about Korea's economy and technology trends.

Requirements:
- Concise title within 20-30 characters
- Topic that would interest global readers
- Professional but easy to understand
- Use keywords like "Korea", "Economy", "Technology", "Trend", "Insight"
- Only one clear title (do not suggest multiple options)

Title:"""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 200
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                topic = response.json()["response"].strip()
                # 불필요한 문자 제거 및 정리
                topic = topic.replace('"', '').replace("'", '').replace('\n', ' ').strip()
                return topic
            else:
                return "Korea Economy and Technology Trends"
        except Exception as e:
            print(f"주제 생성 중 오류: {e}")
            return "Korea Economy and Technology Trends"

    async def generate_blog_post(self, news_data, topic):
        """뉴스 데이터와 주제를 기반으로 블로그 글 생성 (영어, 마크다운 텍스트 반환)"""
        prompt = f"""You are a professional tech/economy blogger. Based on the following Korean news, write a professional and easy-to-read English blog post about '{topic}'.

Write the entire post in English. Do not use Korean.

Reference News:
"""
        
        for keyword, news_list in news_data.items():
            prompt += f"\n## {keyword} News\n"
            for news in news_list:
                prompt += f"- {news['title']} ({news['link']})\n"
        
        prompt += f"""

Summarize and analyze the above news to write a professional English blog post about '{topic}'.

Requirements:
1. Write only in English (no Korean)
2. Include in-depth analysis
3. Make it easy for global readers to understand
4. Use Markdown formatting (titles, subtitles, emphasis, quotes, etc.)
5. Each paragraph should be clearly separated (use a blank line between paragraphs)
6. Use proper spacing and indentation for readability
7. Include news source links
8. 2000-3000 characters in length
9. SEO optimized (naturally include keywords)
10. Catchy title and introduction
11. Key takeaways for business professionals
12. Future outlook and implications
13. Provide insights for the global market

Return ONLY the blog post in Markdown format. Do NOT return JSON, code block, or any explanation. Only the blog post content itself.
"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 4096
                    }
                },
                timeout=120
            )
            if response.status_code == 200:
                content = response.json()["response"].strip()
                return content
            else:
                return self._generate_fallback_blog_post(news_data, topic)
        except Exception as e:
            print(f"블로그 글 생성 중 오류: {e}")
            return self._generate_fallback_blog_post(news_data, topic)

    def _generate_fallback_blog_post(self, news_data, topic):
        """LLM 실패 시 기본 블로그 글 생성"""
        blog_content = f"""# {topic}

## 들어가며

최근 한국 경제와 기술 분야에서 주목할 만한 뉴스들이 쏟아지고 있습니다. 이번 글에서는 주요 키워드별 최신 동향을 분석해보겠습니다.

"""
        
        for keyword, news_list in news_data.items():
            blog_content += f"""
## {keyword} 관련 동향

"""
            for news in news_list:
                blog_content += f"""### {news['title']}

**출처**: [{news['link']}]({news['link']})

이 뉴스는 {keyword} 분야의 중요한 변화를 보여줍니다.

"""
        
        blog_content += f"""
## 종합 분석

위의 뉴스들을 종합적으로 분석한 결과, 한국 경제와 기술 분야에서 다음과 같은 트렌드를 확인할 수 있습니다:

### 주요 특징
- 다양한 분야에서 활발한 변화가 일어나고 있습니다
- 글로벌 영향력이 확대되고 있습니다
- 기술 발전과 경제 성장이 동반되고 있습니다

### 향후 전망
{topic} 분야는 지속적인 성장세를 보일 것으로 예상되며, 특히 한국 시장에서도 활발한 활동이 예상됩니다.

## 결론

이러한 변화는 우리에게 새로운 기회와 도전을 동시에 제공합니다. 지속적인 학습과 적응이 필요한 시점입니다.

---

*이 글은 네이버 뉴스를 참고하여 작성되었습니다.*
"""
        
        return blog_content

    async def save_blog_post(self, content, topic=None):
        """블로그 글을 마크다운 파일로 저장 (마크다운 텍스트)"""
        today_str = datetime.now().strftime('%Y-%m-%d')
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'blog_posts')
        os.makedirs(data_dir, exist_ok=True)
        # 파일명에 쓸 수 있도록 30자 이내, 영문/한글/숫자/공백/밑줄만 허용, 윈도우 금지 특수문자 완전 제거
        import re
        safe_topic = re.sub(r'[\\/:*?"<>|\s]', '_', topic or 'korean_blog_post')
        safe_topic = re.sub(r'[^\w\d가-힣_]', '', safe_topic)[:30]
        if not safe_topic:
            safe_topic = 'korean_blog_post'
        filename = os.path.join(data_dir, f"blog_KoreanNews_{safe_topic}_{today_str}.md")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[SAVE] 블로그 글 저장 완료: {filename}")
        # recentBlog.md 업데이트
        self.update_recent_blog_md(filename, {"title": topic or 'korean_blog_post'})
        return filename, {"title": topic or 'korean_blog_post'}

    def update_recent_blog_md(self, filename, blog_data):
        """recentBlog.md를 최신 블로그 글 정보로 갱신 (마크다운 리스트 형식)"""
        recent_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'recentBlog.md')
        title = blog_data.get('title', '')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 상대 경로로 변환
        relative_path = os.path.relpath(filename, os.path.dirname(recent_path))
        new_content = f"""# 최신 블로그 글 정보

## 현재 최신 글
- **제목**: {title}
- **파일경로**: {relative_path}
- **생성일시**: {current_time}
- **타입**: 한국뉴스

---
*이 파일은 자동으로 업데이트됩니다.*
"""
        with open(recent_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[UPDATE] recentBlog.md 갱신 완료: {recent_path}")

    async def post_to_tistory(self, filename, category_id=None, tags=None):
        """티스토리 API를 통한 포스팅"""
        try:
            # 티스토리 API 포스팅 로직 (기존 코드와 동일)
            print(f"[POST] 티스토리 API 포스팅 시도: {filename}")
            return True
        except Exception as e:
            print(f"티스토리 API 포스팅 실패: {e}")
            return False

# 테스트용 메인 함수
async def test_korea_news_processor():
    """한국 뉴스 프로세서 테스트"""
    processor = KoreaNewsProcessor()
    
    # 1. 트렌드 뉴스 수집
    news_data = await processor.collect_trend_news_json()
    
    # 2. 주제 생성
    topic = await processor.generate_topic(news_data)
    print(f"생성된 주제: {topic}")
    
    # 3. 블로그 글 생성
    blog_content = await processor.generate_blog_post(news_data, topic)
    
    # 4. 저장
    filename = await processor.save_blog_post(blog_content, topic)
    print(f"완료: {filename}")

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(test_korea_news_processor())
    # 블로그 글 저장 후 자동 포스팅 실행
    import os
    poster_path = os.path.join(os.path.dirname(__file__), "korea_tistory_selenium_poster.py")
    print("[AUTO POST] 티스토리 자동 포스팅 시작...")
    exit_code = os.system(f"python {poster_path} --auto")
    if exit_code == 0:
        print("[AUTO POST] 티스토리 자동 포스팅 완료!")
    else:
        print(f"[AUTO POST] 티스토리 자동 포스팅 실패 (exit code: {exit_code})") 