import json
import asyncio
import os
from datetime import datetime
from bbc_rss_crawler import BBCNewsCrawler
import requests

class BBCNewsProcessor:
    def __init__(self):
        self.crawler = BBCNewsCrawler()
        self.ollama_url = "http://localhost:11434"
        self.model = "llama3:8b"
    
    async def collect_and_save_json(self, category='all', limit_per_category=5):
        """BBC 뉴스를 수집하고 JSON으로 저장"""
        print("📰 BBC 뉴스 수집 중...")
        
        if category == 'all':
            news_list = await self.crawler.get_all_categories_today(limit_per_category)
        else:
            news_list = await self.crawler.get_today_news(category, limit_per_category)
        
        # 기사별 본문 수집
        print("📝 기사 본문 수집 중...")
        for news in news_list:
            content = await self.crawler.get_article_content(news['link'])
            news['content'] = content if content else "(본문을 가져오지 못했습니다.)"
        
        # JSON으로 저장
        today_str = datetime.now().strftime('%Y-%m-%d')
        os.makedirs('bbc_news_json', exist_ok=True)
        filename = f"bbc_news_json/bbc_news_{category}_{today_str}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 JSON 저장 완료: {filename}")
        return news_list
    
    def create_blog_prompt(self, news_data, topic):
        """블로그 글 작성을 위한 프롬프트 생성"""
        # 뉴스 요약 생성
        news_summaries = []
        for news in news_data:
            summary = f"""
제목: {news['title']}
카테고리: {news['category']}
요약: {news['summary']}
출처: {news['link']}
발행일: {news['published']}
"""
            news_summaries.append(summary)
        
        combined_summaries = "\n\n".join(news_summaries)
        
        prompt = f"""
당신은 한국의 전문 기술/경제 블로거입니다. 다음 BBC 뉴스들을 바탕으로 티스토리 블로그에 올릴 전문적인 글을 작성해주세요.

주제: {topic}

참고 뉴스:
{combined_summaries}

작성 요구사항:
1. 전문적이고 깊이 있는 분석이 포함된 글
2. 한국 독자들이 이해하기 쉽게 설명
3. 마크다운 형식 적절히 사용 (제목, 소제목, 강조, 인용 등)
4. 뉴스 출처 링크 포함
5. 2000-3000자 분량
6. SEO 최적화 (키워드 자연스럽게 포함)
7. 독자의 관심을 끄는 제목과 인트로
8. 실무진들이 알아야 할 핵심 포인트 포함
9. 향후 전망과 시사점 포함

블로그 글:
"""
        return prompt
    
    async def generate_blog_post(self, news_data, topic):
        """LLM을 사용해 블로그 글 생성"""
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
                return response.json()["response"]
            else:
                print(f"❌ LLM API 오류: {response.status_code}")
                return self._generate_dummy_blog_post(news_data, topic)
                
        except Exception as e:
            print(f"❌ LLM 연결 실패: {e}")
            return self._generate_dummy_blog_post(news_data, topic)
    
    def _generate_dummy_blog_post(self, news_data, topic):
        """테스트용 더미 블로그 포스트"""
        blog_content = f"""# {topic} - BBC 뉴스 분석

## 들어가며

최근 BBC에서 보도한 주요 뉴스들을 바탕으로 {topic}에 대한 심층 분석을 제공합니다.

## 주요 뉴스 요약

"""
        
        for news in news_data:
            blog_content += f"""
### {news['title']}

**카테고리**: {news['category']}  
**발행일**: {news['published']}  
**출처**: [BBC 뉴스]({news['link']})

{news['summary']}

---
"""
        
        blog_content += f"""
## 전문가 분석

위의 뉴스들을 종합적으로 분석한 결과, 다음과 같은 시사점을 도출할 수 있습니다:

### 1. 현재 동향
- 주요 이슈들이 급속도로 발전하고 있습니다
- 글로벌 영향력이 확대되고 있습니다

### 2. 핵심 포인트
- **기술 발전**: 최신 기술이 빠르게 도입되고 있습니다
- **시장 변화**: 새로운 패러다임이 등장하고 있습니다
- **글로벌 협력**: 국제적 협력이 강화되고 있습니다

### 3. 향후 전망
{topic} 분야는 지속적인 성장세를 보일 것으로 예상되며, 특히 한국 시장에서도 활발한 활동이 예상됩니다.

## 결론

이러한 변화는 우리에게 새로운 기회와 도전을 동시에 제공합니다. 지속적인 학습과 적응이 필요한 시점입니다.

---

*이 글은 BBC 뉴스를 참고하여 작성되었습니다.*
"""
        
        return blog_content
    
    async def save_blog_post(self, content, topic):
        """블로그 글을 마크다운 파일로 저장"""
        today_str = datetime.now().strftime('%Y-%m-%d')
        os.makedirs('blog_posts', exist_ok=True)
        filename = f"blog_posts/blog_{topic.replace(' ', '_')}_{today_str}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"💾 블로그 글 저장 완료: {filename}")
        return filename

# 사용 예시
async def main():
    processor = BBCNewsProcessor()
    
    # 1. BBC 뉴스 수집 및 JSON 저장
    news_data = await processor.collect_and_save_json('all', 3)
    
    # 2. 블로그 글 생성
    topic = "글로벌 기술 트렌드와 시장 동향"
    blog_content = await processor.generate_blog_post(news_data, topic)
    
    # 3. 블로그 글 저장
    filename = await processor.save_blog_post(blog_content, topic)
    
    print(f"✅ 완료! 블로그 글: {filename}")

if __name__ == "__main__":
    asyncio.run(main()) 