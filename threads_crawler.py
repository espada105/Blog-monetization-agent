import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import re
from datetime import datetime

class ThreadsCrawler:
    def __init__(self):
        self.base_url = "https://www.threads.net"
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 백그라운드 실행
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # User-Agent 설정
        ua = UserAgent()
        chrome_options.add_argument(f"--user-agent={ua.random}")
        
        # 드라이버 초기화
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
    
    def search_threads(self, keyword, max_posts=10):
        """Threads에서 키워드 검색"""
        try:
            # Threads 검색 페이지로 이동
            search_url = f"{self.base_url}/search/{keyword}"
            print(f"🔍 '{keyword}' 키워드로 검색 중...")
            print(f"📱 URL: {search_url}")
            
            self.driver.get(search_url)
            time.sleep(3)  # 페이지 로딩 대기
            
            # 검색 결과 대기
            wait = WebDriverWait(self.driver, 10)
            
            # 포스트 컨테이너 찾기 (실제 선택자는 Threads 구조에 따라 조정 필요)
            posts = []
            
            # 여러 가능한 선택자 시도
            selectors = [
                "article",  # 일반적인 포스트 선택자
                "[data-testid='post']",  # 테스트 ID 기반
                ".post",  # 클래스 기반
                "div[role='article']"  # 역할 기반
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ '{selector}' 선택자로 {len(elements)}개 요소 발견")
                        posts = elements[:max_posts]
                        break
                except Exception as e:
                    continue
            
            if not posts:
                print("❌ 포스트를 찾을 수 없습니다. 페이지 구조를 확인해주세요.")
                return []
            
            results = []
            for i, post in enumerate(posts, 1):
                try:
                    post_data = self.extract_post_data(post, i)
                    if post_data:
                        results.append(post_data)
                        self.print_post(post_data, i)
                except Exception as e:
                    print(f"⚠️ 포스트 {i} 파싱 중 오류: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"❌ 검색 중 오류 발생: {e}")
            return []
    
    def extract_post_data(self, post_element, index):
        """포스트에서 데이터 추출"""
        try:
            # 사용자명 추출
            username = "알 수 없음"
            try:
                username_elem = post_element.find_element(By.CSS_SELECTOR, "a[href*='/@']")
                username = username_elem.text.strip()
            except:
                pass
            
            # 내용 추출
            content = "내용을 가져올 수 없습니다"
            try:
                content_elem = post_element.find_element(By.CSS_SELECTOR, "div[dir='auto']")
                content = content_elem.text.strip()
            except:
                pass
            
            # 시간 추출
            timestamp = "시간 정보 없음"
            try:
                time_elem = post_element.find_element(By.CSS_SELECTOR, "time")
                timestamp = time_elem.get_attribute("datetime") or time_elem.text.strip()
            except:
                pass
            
            # 좋아요 수 추출
            likes = "0"
            try:
                likes_elem = post_element.find_element(By.CSS_SELECTOR, "[data-testid='like-count']")
                likes = likes_elem.text.strip()
            except:
                pass
            
            # 댓글 수 추출
            replies = "0"
            try:
                replies_elem = post_element.find_element(By.CSS_SELECTOR, "[data-testid='reply-count']")
                replies = replies_elem.text.strip()
            except:
                pass
            
            return {
                "index": index,
                "username": username,
                "content": content[:200] + "..." if len(content) > 200 else content,
                "timestamp": timestamp,
                "likes": likes,
                "replies": replies,
                "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"⚠️ 데이터 추출 중 오류: {e}")
            return None
    
    def print_post(self, post_data, index):
        """포스트 정보를 콘솔에 출력"""
        print(f"\n{'='*60}")
        print(f"📝 포스트 #{index}")
        print(f"👤 사용자: {post_data['username']}")
        print(f"⏰ 시간: {post_data['timestamp']}")
        print(f"❤️ 좋아요: {post_data['likes']}")
        print(f"💬 댓글: {post_data['replies']}")
        print(f"📄 내용:")
        print(f"   {post_data['content']}")
        print(f"🕐 크롤링 시간: {post_data['crawled_at']}")
        print(f"{'='*60}")
    
    def save_results(self, results, keyword):
        """결과를 JSON 파일로 저장"""
        if results:
            filename = f"threads_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 결과가 '{filename}' 파일로 저장되었습니다.")
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()

def main():
    print("🚀 Threads 크롤러 시작!")
    print("=" * 60)
    
    crawler = ThreadsCrawler()
    
    try:
        while True:
            keyword = input("\n🔍 검색할 키워드를 입력하세요 (종료하려면 'quit' 입력): ").strip()
            
            if keyword.lower() == 'quit':
                break
            
            if not keyword:
                print("❌ 키워드를 입력해주세요.")
                continue
            
            max_posts = input("📊 최대 몇 개의 포스트를 가져올까요? (기본값: 5): ").strip()
            max_posts = int(max_posts) if max_posts.isdigit() else 5
            
            print(f"\n🎯 '{keyword}' 키워드로 최대 {max_posts}개 포스트를 검색합니다...")
            
            results = crawler.search_threads(keyword, max_posts)
            
            if results:
                print(f"\n✅ 총 {len(results)}개의 포스트를 찾았습니다!")
                
                # 결과 저장 여부 확인
                save_choice = input("\n💾 결과를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
                if save_choice in ['y', 'yes', '예']:
                    crawler.save_results(results, keyword)
            else:
                print("❌ 검색 결과가 없습니다.")
            
            print("\n" + "="*60)
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    finally:
        crawler.close()
        print("👋 Threads 크롤러를 종료합니다.")

if __name__ == "__main__":
    main() 