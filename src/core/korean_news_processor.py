#!/usr/bin/env python3
"""
한국 뉴스 프로세서
한국 뉴스를 수집하고 블로그 글을 생성하는 프로세서
"""

import json
import asyncio
import os
import sys
from datetime import datetime
import requests
import re

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.scrapers.korean_news_crawler import KoreanNewsCrawler
from config import config

class KoreanNewsProcessor:
    def __init__(self, blog_name=None, cookie=None):
        self.crawler = KoreanNewsCrawler()
        self.ollama_url = config.OLLAMA_URL
        self.model = config.OLLAMA_MODEL
        
        # 티스토리 설정 (선택사항)
        self.blog_name = blog_name
        self.cookie = cookie
        self.tistory_poster = None  # API 포스터는 사용하지 않음
    
    async def collect_and_save_json(self, category='all', limit_per_category=5):
        """한국 뉴스를 수집하고 JSON으로 저장"""
        print("[NEWS] 한국 뉴스 수집 중...")
        
        async with self.crawler:
            if category == 'all':
                news_list = await self.crawler.get_all_categories_today(limit_per_category)
            else:
                news_list = await self.crawler.get_category_news(category, limit_per_category)
        
        # 기사별 본문 수집
        print(" 기사 본문 수집 중...")
        for news in news_list:
            content = await self.crawler.get_article_content(news['link'])
            news['content'] = content if content else "(본문을 가져오지 못했습니다.)"
        
        # JSON으로 저장
        today_str = datetime.now().strftime('%Y-%m-%d')
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'korean_news_json')
        os.makedirs(data_dir, exist_ok=True)
        filename = os.path.join(data_dir, f"korean_news_{category}_{today_str}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"[SAVE] JSON 저장 완료: {filename}")
        return news_list
    
    def create_topic_prompt(self, news_data):
        """블로그 글 주제 생성을 위한 프롬프트 생성"""
        # 뉴스 요약 생성
        news_summaries = []
        for news in news_data:
            summary = f"""
제목: {news['title']}
카테고리: {news['category']}
출처: {news['source']}
요약: {news['summary']}
"""
            news_summaries.append(summary)
        
        combined_summaries = "\n\n".join(news_summaries)
        
        prompt = f"""
당신은 한국의 전문 기술/경제 블로거입니다. 다음 한국 뉴스들을 분석하여 블로그 글의 주제를 생성해주세요.

참고 뉴스:
{combined_summaries}

요구사항:
1. 뉴스들의 공통 주제나 트렌드를 파악
2. 한국 독자들이 관심을 가질 만한 주제
3. 전문적이면서도 접근하기 쉬운 주제
4. SEO에 유리한 키워드 포함
5. 10-15자 이내의 간결한 주제
6. "한국", "트렌드", "동향", "분석" 등의 키워드 활용

주제:
"""
        return prompt

    def create_blog_prompt(self, news_data, topic):
        """블로그 글 작성을 위한 프롬프트 생성 (영어, 마크다운 텍스트 반환)"""
        # 뉴스 요약 생성
        news_summaries = []
        for news in news_data:
            summary = f"""
제목: {news['title']}
카테고리: {news['category']}
출처: {news['source']}
요약: {news['summary']}
링크: {news['link']}
발행일: {news['published']}
"""
            news_summaries.append(summary)
        
        combined_summaries = "\n\n".join(news_summaries)
        
        prompt = f"""
You are a professional tech/economy blogger. Based on the following Korean news, write a professional and easy-to-read English blog post about '{topic}'.

Write the entire post in English. Do not use Korean.

Reference News:
{combined_summaries}

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
        return prompt

    async def generate_topic(self, news_data):
        """LLM을 사용해 블로그 글 주제 생성"""
        prompt = self.create_topic_prompt(news_data)
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "max_tokens": 100
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                topic = response.json()["response"].strip()
                # 불필요한 문자 제거
                topic = topic.replace('"', '').replace("'", '').replace('\n', ' ').strip()
                return topic
            else:
                print(f" 주제 생성 LLM API 오류: {response.status_code}")
                return self._generate_default_topic(news_data)
                
        except Exception as e:
            print(f" 주제 생성 LLM 연결 실패: {e}")
            return self._generate_default_topic(news_data)
    
    def _generate_default_topic(self, news_data):
        """기본 주제 생성"""
        categories = [news['category'] for news in news_data]
        unique_categories = list(set(categories))
        
        if len(unique_categories) == 1:
            category = unique_categories[0]
            if category == 'it':
                return "한국 IT 산업 동향과 기술 트렌드"
            elif category == 'economy':
                return "한국 경제 동향과 시장 분석"
            elif category == 'politics':
                return "한국 정치경제 동향과 정책 분석"
            elif category == 'science':
                return "한국 과학기술 동향과 미래 전망"
            else:
                return f"한국 {category} 뉴스 분석과 시사점"
        else:
            return "한국 주요 이슈와 트렌드 분석"

    async def generate_blog_post(self, news_data, topic):
        """LLM을 사용해 블로그 글 생성 (영어, JSON 응답)"""
        prompt = self.create_blog_prompt(news_data, topic)
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
                        "max_tokens": 4000
                    }
                },
                timeout=120
            )
            if response.status_code == 200:
                raw = response.json()["response"].strip()
                # JSON 파싱
                try:
                    # JSON 응답이 코드블록(```json ... ```)으로 감싸져 있을 수도 있음
                    if raw.startswith('```json'):
                        raw = raw[7:]
                    if raw.startswith('```'):
                        raw = raw[3:]
                    if raw.endswith('```'):
                        raw = raw[:-3]
                    data = json.loads(raw)
                    # 필수 필드 추출
                    title = data.get('title', topic)
                    summary = data.get('summary', '')
                    tags = data.get('tags', [])
                    category = data.get('category', '')
                    content = data.get('content', '')
                    return {
                        'title': title,
                        'summary': summary,
                        'tags': tags,
                        'category': category,
                        'content': content
                    }
                except Exception as e:
                    print(f"LLM JSON 파싱 오류: {e}")
                    # fallback: 전체 응답을 content로 저장
                    return {
                        'title': topic,
                        'summary': '',
                        'tags': [],
                        'category': '',
                        'content': raw
                    }
            else:
                return {
                    'title': topic,
                    'summary': '',
                    'tags': [],
                    'category': '',
                    'content': self._generate_dummy_blog_post(news_data, topic)
                }
        except Exception as e:
            print(f"블로그 글 생성 중 오류: {e}")
            return {
                'title': topic,
                'summary': '',
                'tags': [],
                'category': '',
                'content': self._generate_dummy_blog_post(news_data, topic)
            }
    
    def _generate_dummy_blog_post(self, news_data, topic):
        """테스트용 더미 블로그 포스트"""
        blog_content = f"""# {topic} - 한국 뉴스 분석

## 들어가며

최근 한국 주요 언론사에서 보도한 주요 뉴스들을 바탕으로 {topic}에 대한 심층 분석을 제공합니다.

## 주요 뉴스 요약

"""
        
        for news in news_data:
            blog_content += f"""
### {news['title']}

**카테고리**: {news['category']}  
**출처**: {news['source']}  
**발행일**: {news['published']}  
**원문**: [링크]({news['link']})

{news['summary']}

---
"""
        
        blog_content += f"""
## 전문가 분석

위의 뉴스들을 종합적으로 분석한 결과, 다음과 같은 시사점을 도출할 수 있습니다:

### 1. 현재 동향
- 한국 시장에서 주요 이슈들이 급속도로 발전하고 있습니다
- 국내외 영향력이 확대되고 있습니다

### 2. 핵심 포인트
- **기술 발전**: 한국의 최신 기술이 빠르게 도입되고 있습니다
- **시장 변화**: 새로운 패러다임이 등장하고 있습니다
- **정책 동향**: 정부의 정책 변화가 산업에 영향을 미치고 있습니다

### 3. 향후 전망
{topic} 분야는 지속적인 성장세를 보일 것으로 예상되며, 특히 한국 시장에서도 활발한 활동이 예상됩니다.

## 결론

이러한 변화는 우리에게 새로운 기회와 도전을 동시에 제공합니다. 지속적인 학습과 적응이 필요한 시점입니다.

---

*이 글은 한국 주요 언론사의 뉴스를 참고하여 작성되었습니다.*
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
    
    async def post_to_tistory(self, blog_file, category_id=None, tags=None):
        """티스토리에 자동 포스팅 (API 방식은 사용하지 않음)"""
        print(" API 방식 포스팅은 사용하지 않습니다. 셀레니움 방식만 사용합니다.")
        return None

# 사용 예시
async def main():
    # 설정 파일에서 값 가져오기
    BLOG_NAME = config.TISTORY_BLOG_NAME
    COOKIE = config.TISTORY_COOKIE
    CATEGORY_ID = config.TISTORY_CATEGORY_ID
    TAGS = getattr(config, 'TISTORY_TAGS', None)  # 태그가 없으면 None 사용
    KOREAN_CATEGORY = getattr(config, 'KOREAN_CATEGORY', 'all')  # 한국 뉴스 카테고리
    KOREAN_LIMIT = getattr(config, 'KOREAN_LIMIT_PER_CATEGORY', 3)  # 카테고리당 뉴스 수
    USE_AUTO_TOPIC = getattr(config, 'USE_AUTO_TOPIC', True)  # 자동 주제 생성 사용 여부
    DEFAULT_TOPIC = getattr(config, 'KOREAN_BLOG_TOPIC', "Korean_News_")
    
    # 한국 뉴스 프로세서 초기화
    processor = KoreanNewsProcessor(BLOG_NAME, COOKIE)
    
    # 1. 한국 뉴스 수집 및 JSON 저장
    news_data = await processor.collect_and_save_json(KOREAN_CATEGORY, KOREAN_LIMIT)
    
    # 2. 블로그 글 주제 생성 (자동 또는 수동)
    if USE_AUTO_TOPIC:
        print(" LLM을 사용해 블로그 글 주제를 생성합니다...")
        topic = await processor.generate_topic(news_data)
        print(f" 생성된 주제: {topic}")
    else:
        topic = DEFAULT_TOPIC
        print(f" 설정된 주제 사용: {topic}")
    
    # 3. 블로그 글 생성
    blog_data = await processor.generate_blog_post(news_data, topic)
    
    # 4. 블로그 글 저장
    filename, blog_data = await processor.save_blog_post(blog_data.get('content', ''), topic)
    
    # 5. 티스토리 자동 포스팅 (선택사항)
    if processor.tistory_poster:
        await processor.post_to_tistory(
            filename,
            category_id=CATEGORY_ID,
            tags=TAGS
        )
    
    # 6. 셀레니움 자동 포스팅 (새로 추가)
    print(" 셀레니움 자동 포스팅 시작...")
    try:
        import subprocess
        import sys
        
        # 셀레니움 포스터 실행
        poster_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src', 'posters', 'tistory_selenium_poster.py')
        cmd = [
            sys.executable, poster_path,
            "--file", filename,
            "--auto"  # 자동으로 JSON 파일 찾기
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(" 셀레니움 자동 포스팅 완료!")
            print(f" 블로그 확인: https://aigent-hong.tistory.com")
        else:
            print(f" 셀레니움 포스팅 중 오류: {result.stderr}")
            
    except Exception as e:
        print(f" 셀레니움 포스팅 실패: {e}")
    
    print(f" 완료! 블로그 글: {filename}")
    print(f" 주제: {topic}")
    
    return filename, topic  # 결과 반환

if __name__ == "__main__":
    asyncio.run(main()) 