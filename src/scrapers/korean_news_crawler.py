#!/usr/bin/env python3
"""
한국 뉴스 크롤러
네이버 뉴스 RSS와 연합뉴스 RSS를 활용한 한국 뉴스 수집기
"""

import asyncio
import aiohttp
import feedparser
from datetime import datetime, timedelta
import re
from typing import List, Dict, Optional
import logging

class KoreanNewsCrawler:
    def __init__(self):
        self.session = None
        self.setup_logging()
        
        # 연합뉴스 RSS URL들만 사용
        self.yonhap_rss_urls = {
            'main': 'https://www.yonhapnews.co.kr/feed/headline/main.xml',
            'politics': 'https://www.yonhapnews.co.kr/feed/headline/politics.xml',
            'economy': 'https://www.yonhapnews.co.kr/feed/headline/economy.xml',
            'society': 'https://www.yonhapnews.co.kr/feed/headline/society.xml',
            'world': 'https://www.yonhapnews.co.kr/feed/headline/world.xml',
            'science': 'https://www.yonhapnews.co.kr/feed/headline/science.xml'
        }
    
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    async def fetch_rss_feed(self, url: str) -> Optional[feedparser.FeedParserDict]:
        """RSS 피드 가져오기"""
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    return feedparser.parse(content)
                else:
                    self.logger.warning(f"RSS 피드 가져오기 실패: {url}, 상태: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"RSS 피드 가져오기 오류: {url}, 오류: {e}")
            return None
    
    def parse_yonhap_news(self, feed: feedparser.FeedParserDict, category: str) -> List[Dict]:
        """연합뉴스 파싱"""
        news_list = []
        
        for entry in feed.entries[:10]:  # 최신 10개만
            try:
                # 제목 정리
                title = entry.title.strip()
                
                # 날짜 파싱
                pub_date = datetime.now()  # 기본값
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                
                # 링크
                link = entry.link if hasattr(entry, 'link') else ''
                
                # 요약
                summary = ""
                if hasattr(entry, 'summary'):
                    summary = re.sub(r'<.*?>', '', entry.summary).strip()
                elif hasattr(entry, 'description'):
                    summary = re.sub(r'<.*?>', '', entry.description).strip()
                
                news_item = {
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'category': category,
                    'source': '연합뉴스',
                    'published': pub_date.isoformat(),
                    'published_date': pub_date
                }
                
                news_list.append(news_item)
                
            except Exception as e:
                self.logger.error(f"연합뉴스 파싱 오류: {e}")
                continue
        
        return news_list
    
    async def get_category_news(self, category: str, limit: int = 5) -> List[Dict]:
        """특정 카테고리의 뉴스 가져오기"""
        all_news = []
        
        # 연합뉴스에서 가져오기
        if category in self.yonhap_rss_urls:
            feed = await self.fetch_rss_feed(self.yonhap_rss_urls[category])
            if feed:
                yonhap_news = self.parse_yonhap_news(feed, category)
                all_news.extend(yonhap_news[:limit//2])
        
        # 날짜순으로 정렬하고 중복 제거
        unique_news = self.remove_duplicates(all_news)
        return sorted(unique_news, key=lambda x: x['published_date'], reverse=True)[:limit]
    
    async def get_all_categories_today(self, limit_per_category: int = 3) -> List[Dict]:
        """모든 카테고리의 오늘 뉴스 가져오기"""
        all_news = []
        
        # 연합뉴스에서 가져오기
        for category in ['main', 'politics', 'economy', 'society', 'world', 'science']:
            try:
                news = await self.get_category_news(category, limit_per_category)
                all_news.extend(news)
                self.logger.info(f"카테고리 '{category}'에서 {len(news)}개 뉴스 수집")
            except Exception as e:
                self.logger.error(f"카테고리 '{category}' 수집 오류: {e}")
        
        # 중복 제거 및 정렬
        unique_news = self.remove_duplicates(all_news)
        return sorted(unique_news, key=lambda x: x['published_date'], reverse=True)
    
    def remove_duplicates(self, news_list: List[Dict]) -> List[Dict]:
        """중복 뉴스 제거 (제목 기준)"""
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            # 제목 정규화 (공백 제거, 소문자 변환)
            normalized_title = re.sub(r'\s+', ' ', news['title'].lower().strip())
            
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_news.append(news)
        
        return unique_news
    
    async def get_article_content(self, url: str) -> Optional[str]:
        """기사 본문 가져오기 (간단한 버전)"""
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # 간단한 본문 추출 (실제로는 더 정교한 파싱 필요)
                    # 여기서는 요약만 반환
                    return "본문은 원문 링크를 참조하세요."
                else:
                    return None
        except Exception as e:
            self.logger.error(f"기사 본문 가져오기 오류: {url}, 오류: {e}")
            return None

# 사용 예시
async def main():
    """테스트 함수"""
    async with KoreanNewsCrawler() as crawler:
        print("🇰🇷 한국 뉴스 크롤러 테스트")
        print("=" * 50)
        
        # 특정 카테고리 테스트
        print("📰 IT 뉴스 수집 중...")
        it_news = await crawler.get_category_news('it', 5)
        for news in it_news:
            print(f"- {news['title']} ({news['source']})")
        
        print("\n" + "=" * 50)
        
        # 전체 카테고리 테스트
        print("📰 모든 카테고리 뉴스 수집 중...")
        all_news = await crawler.get_all_categories_today(3)
        print(f"총 {len(all_news)}개 뉴스 수집 완료")
        
        for news in all_news[:5]:  # 상위 5개만 출력
            print(f"- [{news['category']}] {news['title']} ({news['source']})")

if __name__ == "__main__":
    asyncio.run(main()) 