import feedparser
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import asyncio
import os

class BBCNewsCrawler:
    def __init__(self):
        self.rss_feeds = {
            'world': 'http://feeds.bbci.co.uk/news/world/rss.xml',
            'technology': 'http://feeds.bbci.co.uk/news/technology/rss.xml',
            'business': 'http://feeds.bbci.co.uk/news/business/rss.xml',
            'science': 'http://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
            'entertainment': 'http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml',
            'health': 'http://feeds.bbci.co.uk/news/health/rss.xml'
        }
    
    async def get_today_news(self, category='world', limit=10):
        """오늘 BBC 뉴스 가져오기"""
        if category not in self.rss_feeds:
            print(f"❌ 지원하지 않는 카테고리: {category}")
            return []
        
        try:
            # RSS 피드 파싱
            feed = feedparser.parse(self.rss_feeds[category])
            today = datetime.now().date()
            
            today_news = []
            for entry in feed.entries[:limit]:
                # 발행일 확인
                pub_date = datetime(*entry.published_parsed[:6])
                if pub_date.date() == today:
                    news_item = {
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.summary,
                        'published': pub_date,
                        'category': category
                    }
                    today_news.append(news_item)
            
            print(f"✅ BBC {category} 뉴스 {len(today_news)}개 수집 완료")
            return today_news
            
        except Exception as e:
            print(f"❌ BBC 뉴스 수집 실패: {e}")
            return []
    
    async def get_all_categories_today(self, limit_per_category=5):
        """모든 카테고리의 오늘 뉴스 가져오기"""
        all_news = []
        
        for category in self.rss_feeds.keys():
            print(f"📰 {category} 카테고리 수집 중...")
            category_news = await self.get_today_news(category, limit_per_category)
            all_news.extend(category_news)
            await asyncio.sleep(1)  # 요청 간격 조절
        
        return all_news
    
    async def get_article_content(self, url):
        """BBC 기사 본문 가져오기"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # BBC 기사 본문 추출
            article_body = soup.find('article')
            if article_body:
                # 본문 텍스트 추출
                paragraphs = article_body.find_all('p')
                content = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                return content
            
            return None
            
        except Exception as e:
            print(f"❌ 기사 본문 가져오기 실패: {e}")
            return None

    async def save_to_file(self, news_list, category='all'):
        """기사 리스트를 마크다운 파일로 저장 (본문 포함)"""
        if not news_list:
            print("저장할 뉴스가 없습니다.")
            return
        today_str = datetime.now().strftime('%Y-%m-%d')
        os.makedirs('bbc_news', exist_ok=True)
        filename = f"bbc_news/bbc_{category}_{today_str}.md"
        
        # 기사별 본문 비동기 수집
        print("📝 기사 본문 수집 중...")
        tasks = [self.get_article_content(news['link']) for news in news_list]
        contents = await asyncio.gather(*tasks)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# BBC {category.capitalize()} News - {today_str}\n\n")
            for idx, news in enumerate(news_list):
                f.write(f"## {news['title']}\n")
                f.write(f"- 링크: [{news['link']}]({news['link']})\n")
                f.write(f"- 발행일: {news['published']}\n")
                f.write(f"- 요약: {news['summary']}\n")
                content = contents[idx]
                if content:
                    f.write(f"\n### 본문\n{content}\n")
                else:
                    f.write("\n### 본문\n(본문을 가져오지 못했습니다.)\n")
                f.write("\n---\n\n")
        print(f"💾 파일 저장 완료: {filename}")

# 사용 예시
async def main():
    crawler = BBCNewsCrawler()
    
    # 특정 카테고리 오늘 뉴스
    world_news = await crawler.get_today_news('world', 5)
    for news in world_news:
        print(f"📰 {news['title']}")
        print(f"🔗 {news['link']}")
        print(f"📅 {news['published']}")
        print("-" * 50)
    # 파일 저장 (본문 포함)
    await crawler.save_to_file(world_news, category='world')
    
    # 모든 카테고리 뉴스
    all_news = await crawler.get_all_categories_today(3)
    print(f"📊 총 {len(all_news)}개의 오늘 뉴스 수집")
    # 파일 저장 (본문 포함)
    await crawler.save_to_file(all_news, category='all')

if __name__ == "__main__":
    asyncio.run(main()) 