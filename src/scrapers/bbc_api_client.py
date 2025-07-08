import requests
import json
from datetime import datetime, timedelta
import asyncio

class BBCAPIClient:
    def __init__(self):
        self.base_url = "https://www.bbc.co.uk"
        self.api_url = "https://www.bbc.co.uk/api"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def get_news_by_category(self, category='news', limit=10):
        """카테고리별 BBC 뉴스 가져오기"""
        try:
            # BBC 뉴스 페이지에서 데이터 추출
            url = f"{self.base_url}/{category}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # BBC 뉴스 페이지 파싱
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                news_items = []
                # 뉴스 링크 찾기
                news_links = soup.find_all('a', href=True)
                
                for link in news_links[:limit]:
                    href = link.get('href')
                    if href and '/news/' in href and not href.startswith('http'):
                        full_url = f"{self.base_url}{href}"
                        title = link.get_text().strip()
                        
                        if title and len(title) > 10:  # 의미있는 제목만
                            news_item = {
                                'title': title,
                                'link': full_url,
                                'category': category
                            }
                            news_items.append(news_item)
                
                return news_items
            else:
                print(f"❌ BBC API 요청 실패: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ BBC 뉴스 가져오기 실패: {e}")
            return []
    
    async def get_latest_news(self, limit=10):
        """최신 BBC 뉴스 가져오기"""
        return await self.get_news_by_category('news', limit)
    
    async def get_world_news(self, limit=10):
        """세계 뉴스 가져오기"""
        return await self.get_news_by_category('news/world', limit)
    
    async def get_technology_news(self, limit=10):
        """기술 뉴스 가져오기"""
        return await self.get_news_by_category('news/technology', limit)
    
    async def get_business_news(self, limit=10):
        """비즈니스 뉴스 가져오기"""
        return await self.get_news_by_category('news/business', limit)

# 사용 예시
async def main():
    client = BBCAPIClient()
    
    # 최신 뉴스
    latest_news = await client.get_latest_news(5)
    print("📰 최신 BBC 뉴스:")
    for news in latest_news:
        print(f"- {news['title']}")
        print(f"  🔗 {news['link']}")
    
    # 세계 뉴스
    world_news = await client.get_world_news(3)
    print("\n🌍 세계 뉴스:")
    for news in world_news:
        print(f"- {news['title']}")

if __name__ == "__main__":
    asyncio.run(main()) 