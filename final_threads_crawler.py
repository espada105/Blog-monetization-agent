import requests
import json
import time
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup

class FinalThreadsCrawler:
    def __init__(self):
        self.base_url = "https://www.threads.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
        })
    
    def search_threads(self, keyword, max_posts=5):
        """Threads에서 키워드 검색 (올바른 URL 구조 사용)"""
        try:
            # 올바른 검색 URL 구조
            search_url = f"{self.base_url}/search?q={quote(keyword)}&serp_type=default&hl=ko"
            
            print(f"🔍 '{keyword}' 키워드로 검색 중...")
            print(f"📱 URL: {search_url}")
            
            # 요청 보내기
            response = self.session.get(search_url, timeout=15)
            
            print(f"📊 HTTP 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 페이지 로딩 성공!")
                return self.parse_threads_page(response.text, keyword, max_posts)
            else:
                print(f"❌ HTTP 오류: {response.status_code}")
                # 응답 내용 확인
                print(f"📄 응답 내용 일부: {response.text[:500]}...")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 네트워크 오류: {e}")
            return []
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return []
    
    def parse_threads_page(self, html_content, keyword, max_posts):
        """HTML에서 Threads 포스트 정보 추출"""
        results = []
        
        try:
            # BeautifulSoup으로 HTML 파싱
            soup = BeautifulSoup(html_content, 'html.parser')
            
            print(f"📄 HTML 크기: {len(html_content)} 문자")
            
            # 페이지 제목 확인
            title = soup.find('title')
            if title:
                print(f"📋 페이지 제목: {title.text}")
            
            # 메타 태그 확인
            meta_description = soup.find('meta', attrs={'name': 'description'})
            if meta_description:
                print(f"📝 메타 설명: {meta_description.get('content', '')[:100]}...")
            
            # Threads 특정 구조 찾기
            posts = self.find_threads_posts(soup, keyword)
            
            if posts:
                print(f"📊 Threads 포스트 {len(posts)}개 발견")
                
                # 결과 생성
                for i, post_data in enumerate(posts[:max_posts], 1):
                    post_data['index'] = i
                    post_data['keyword'] = keyword
                    post_data['crawled_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    results.append(post_data)
                    self.print_post(post_data, i)
            else:
                print("🔍 Threads 포스트를 찾을 수 없습니다. 일반 텍스트 검색을 시도합니다...")
                # 일반 텍스트 검색으로 대체
                results = self.fallback_text_search(soup, keyword, max_posts)
            
            return results
            
        except Exception as e:
            print(f"⚠️ HTML 파싱 중 오류: {e}")
            return []
    
    def find_threads_posts(self, soup, keyword):
        """Threads 포스트 구조 찾기"""
        posts = []
        
        # 여러 가능한 Threads 포스트 선택자들
        selectors = [
            'article[data-testid="post"]',
            'div[data-testid="post"]',
            'article[role="article"]',
            'div[role="article"]',
            'div[class*="post"]',
            'div[class*="thread"]',
            'article[class*="post"]',
            'article[class*="thread"]',
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    print(f"✅ '{selector}' 선택자로 {len(elements)}개 요소 발견")
                    
                    for element in elements:
                        post_data = self.extract_post_data(element)
                        if post_data:
                            posts.append(post_data)
                    
                    if posts:
                        break
            except Exception as e:
                continue
        
        return posts
    
    def extract_post_data(self, element):
        """포스트 요소에서 데이터 추출"""
        try:
            # 사용자명 추출
            username = "알 수 없음"
            username_selectors = [
                'a[href*="/@"]',
                '[data-testid="username"]',
                '[class*="username"]',
                'span[class*="username"]'
            ]
            
            for selector in username_selectors:
                try:
                    username_elem = element.select_one(selector)
                    if username_elem:
                        username = username_elem.get_text(strip=True)
                        break
                except:
                    continue
            
            # 내용 추출
            content = "내용을 가져올 수 없습니다"
            content_selectors = [
                'div[dir="auto"]',
                '[data-testid="post-text"]',
                '[class*="content"]',
                'p',
                'span[class*="text"]'
            ]
            
            for selector in content_selectors:
                try:
                    content_elem = element.select_one(selector)
                    if content_elem:
                        content = content_elem.get_text(strip=True)
                        if len(content) > 10:  # 의미있는 내용인지 확인
                            break
                except:
                    continue
            
            # 시간 추출
            timestamp = "시간 정보 없음"
            time_selectors = [
                'time',
                '[data-testid="timestamp"]',
                '[class*="time"]',
                'span[class*="time"]'
            ]
            
            for selector in time_selectors:
                try:
                    time_elem = element.select_one(selector)
                    if time_elem:
                        timestamp = time_elem.get('datetime') or time_elem.get_text(strip=True)
                        break
                except:
                    continue
            
            # 좋아요 수 추출
            likes = "N/A"
            likes_selectors = [
                '[data-testid="like-count"]',
                '[class*="like"]',
                'span[class*="like"]'
            ]
            
            for selector in likes_selectors:
                try:
                    likes_elem = element.select_one(selector)
                    if likes_elem:
                        likes = likes_elem.get_text(strip=True)
                        break
                except:
                    continue
            
            # 댓글 수 추출
            replies = "N/A"
            replies_selectors = [
                '[data-testid="reply-count"]',
                '[class*="reply"]',
                'span[class*="reply"]'
            ]
            
            for selector in replies_selectors:
                try:
                    replies_elem = element.select_one(selector)
                    if replies_elem:
                        replies = replies_elem.get_text(strip=True)
                        break
                except:
                    continue
            
            return {
                "username": username,
                "content": content[:200] + "..." if len(content) > 200 else content,
                "timestamp": timestamp,
                "likes": likes,
                "replies": replies
            }
            
        except Exception as e:
            print(f"⚠️ 포스트 데이터 추출 중 오류: {e}")
            return None
    
    def fallback_text_search(self, soup, keyword, max_posts):
        """일반 텍스트 검색 (대체 방법)"""
        results = []
        
        # 키워드가 포함된 텍스트 찾기
        keyword_matches = []
        
        # 모든 텍스트 노드에서 키워드 검색
        for text in soup.stripped_strings:
            if keyword.lower() in text.lower() and len(text.strip()) > 10:
                keyword_matches.append(text.strip())
        
        print(f"📊 키워드 '{keyword}'가 포함된 {len(keyword_matches)}개 텍스트 발견")
        
        # 결과 생성
        for i, content in enumerate(keyword_matches[:max_posts], 1):
            post_data = {
                "index": i,
                "username": f"사용자_{i}",
                "content": content[:200] + "..." if len(content) > 200 else content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "likes": "N/A",
                "replies": "N/A",
                "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "keyword": keyword,
                "method": "fallback_text_search"
            }
            results.append(post_data)
            self.print_post(post_data, i)
        
        return results
    
    def print_post(self, post_data, index):
        """포스트 정보를 콘솔에 출력"""
        print(f"\n{'='*60}")
        print(f"📝 포스트 #{index}")
        print(f"👤 사용자: {post_data['username']}")
        print(f"⏰ 시간: {post_data['timestamp']}")
        print(f"❤️ 좋아요: {post_data['likes']}")
        print(f"💬 댓글: {post_data['replies']}")
        if 'keyword' in post_data:
            print(f"🔍 키워드: {post_data['keyword']}")
        if 'method' in post_data:
            print(f"🔧 방법: {post_data['method']}")
        print(f"📄 내용:")
        print(f"   {post_data['content']}")
        print(f"🕐 크롤링 시간: {post_data['crawled_at']}")
        print(f"{'='*60}")
    
    def save_results(self, results, keyword):
        """결과를 JSON 파일로 저장"""
        if results:
            filename = f"final_threads_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 결과가 '{filename}' 파일로 저장되었습니다.")
    
    def demo_search(self):
        """데모 검색 실행"""
        print("🎯 데모 검색을 실행합니다...")
        
        # 샘플 키워드들
        sample_keywords = ["AI", "technology", "programming", "python"]
        
        for keyword in sample_keywords:
            print(f"\n{'='*60}")
            print(f"🔍 데모: '{keyword}' 키워드 검색")
            print(f"{'='*60}")
            
            results = self.search_threads(keyword, 3)
            
            if results:
                print(f"✅ '{keyword}' 검색 완료: {len(results)}개 결과")
                self.save_results(results, keyword)
            else:
                print(f"❌ '{keyword}' 검색 결과 없음")
            
            time.sleep(2)  # 요청 간 딜레이

def main():
    print("🚀 Final Threads 크롤러 시작!")
    print("=" * 60)
    print("📍 올바른 URL 구조 사용: https://www.threads.com/search?q={keyword}&serp_type=default&hl=ko")
    print("=" * 60)
    
    crawler = FinalThreadsCrawler()
    
    try:
        while True:
            print("\n📋 옵션을 선택하세요:")
            print("1. 키워드 검색")
            print("2. 데모 실행")
            print("3. 종료")
            
            choice = input("\n선택 (1-3): ").strip()
            
            if choice == "1":
                keyword = input("\n🔍 검색할 키워드를 입력하세요: ").strip()
                
                if not keyword:
                    print("❌ 키워드를 입력해주세요.")
                    continue
                
                max_posts = input("📊 최대 몇 개의 포스트를 가져올까요? (기본값: 5): ").strip()
                max_posts = int(max_posts) if max_posts.isdigit() else 5
                
                print(f"\n🎯 '{keyword}' 키워드로 최대 {max_posts}개 포스트를 검색합니다...")
                
                results = crawler.search_threads(keyword, max_posts)
                
                if results:
                    print(f"\n✅ 총 {len(results)}개의 포스트를 찾았습니다!")
                    
                    save_choice = input("\n💾 결과를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
                    if save_choice in ['y', 'yes', '예']:
                        crawler.save_results(results, keyword)
                else:
                    print("❌ 검색 결과가 없습니다.")
            
            elif choice == "2":
                crawler.demo_search()
            
            elif choice == "3":
                break
            
            else:
                print("❌ 잘못된 선택입니다. 1-3 중에서 선택해주세요.")
            
            print("\n" + "="*60)
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    finally:
        print("👋 Final Threads 크롤러를 종료합니다.")

if __name__ == "__main__":
    main() 