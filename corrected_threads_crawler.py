import requests
import json
import time
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup

class CorrectedThreadsCrawler:
    def __init__(self):
        self.base_url = "https://www.threads.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
    
    def search_threads(self, keyword, max_posts=5):
        """Threads에서 키워드 검색 (올바른 URL 사용)"""
        try:
            # 올바른 검색 URL 구조
            search_url = f"{self.base_url}/search?q={quote(keyword)}&hl=ko"
            
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
                    "keyword": keyword
                }
                results.append(post_data)
                self.print_post(post_data, i)
            
            # 결과가 없으면 페이지 구조 분석
            if not results:
                print("🔍 페이지 구조 분석 중...")
                self.analyze_page_structure(soup)
            
            return results
            
        except Exception as e:
            print(f"⚠️ HTML 파싱 중 오류: {e}")
            return []
    
    def analyze_page_structure(self, soup):
        """페이지 구조 분석"""
        print("📋 페이지 구조 분석:")
        
        # 주요 태그들 확인
        tags_to_check = ['article', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        
        for tag in tags_to_check:
            elements = soup.find_all(tag)
            if elements:
                print(f"  - {tag}: {len(elements)}개")
        
        # 클래스명이 있는 요소들 확인
        elements_with_class = soup.find_all(class_=True)
        if elements_with_class:
            classes = set()
            for elem in elements_with_class[:10]:  # 처음 10개만
                classes.update(elem.get('class', []))
            print(f"  - 발견된 클래스들: {list(classes)[:10]}")
    
    def print_post(self, post_data, index):
        """포스트 정보를 콘솔에 출력"""
        print(f"\n{'='*60}")
        print(f"📝 포스트 #{index}")
        print(f"👤 사용자: {post_data['username']}")
        print(f"⏰ 시간: {post_data['timestamp']}")
        print(f"❤️ 좋아요: {post_data['likes']}")
        print(f"💬 댓글: {post_data['replies']}")
        print(f"🔍 키워드: {post_data['keyword']}")
        print(f"📄 내용:")
        print(f"   {post_data['content']}")
        print(f"🕐 크롤링 시간: {post_data['crawled_at']}")
        print(f"{'='*60}")
    
    def save_results(self, results, keyword):
        """결과를 JSON 파일로 저장"""
        if results:
            filename = f"corrected_threads_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    print("🚀 Corrected Threads 크롤러 시작!")
    print("=" * 60)
    print("📍 올바른 URL 사용: https://www.threads.com")
    print("=" * 60)
    
    crawler = CorrectedThreadsCrawler()
    
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
        print("👋 Corrected Threads 크롤러를 종료합니다.")

if __name__ == "__main__":
    main() 