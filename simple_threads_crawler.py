import requests
import json
import time
from datetime import datetime
from urllib.parse import quote

class SimpleThreadsCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def search_threads(self, keyword, max_posts=5):
        """Threads에서 키워드 검색 (간단한 버전)"""
        try:
            # URL 인코딩
            encoded_keyword = quote(keyword)
            search_url = f"https://www.threads.net/search/{encoded_keyword}"
            
            print(f"🔍 '{keyword}' 키워드로 검색 중...")
            print(f"📱 URL: {search_url}")
            
            # 요청 보내기
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                print("✅ 페이지 로딩 성공!")
                return self.parse_threads_page(response.text, keyword, max_posts)
            else:
                print(f"❌ HTTP 오류: {response.status_code}")
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
            # 간단한 텍스트 기반 파싱 (실제 구현에서는 더 정교한 파싱 필요)
            lines = html_content.split('\n')
            
            # 키워드가 포함된 라인 찾기
            keyword_lines = []
            for i, line in enumerate(lines):
                if keyword.lower() in line.lower() and len(line.strip()) > 10:
                    keyword_lines.append((i, line.strip()))
            
            print(f"📊 키워드 '{keyword}'가 포함된 {len(keyword_lines)}개 라인 발견")
            
            # 결과 생성
            for i, (line_num, content) in enumerate(keyword_lines[:max_posts], 1):
                post_data = {
                    "index": i,
                    "username": f"사용자_{i}",
                    "content": content[:200] + "..." if len(content) > 200 else content,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "likes": "N/A",
                    "replies": "N/A",
                    "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "line_number": line_num
                }
                results.append(post_data)
                self.print_post(post_data, i)
            
            return results
            
        except Exception as e:
            print(f"⚠️ HTML 파싱 중 오류: {e}")
            return []
    
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
        if 'line_number' in post_data:
            print(f"📍 라인 번호: {post_data['line_number']}")
        print(f"{'='*60}")
    
    def save_results(self, results, keyword):
        """결과를 JSON 파일로 저장"""
        if results:
            filename = f"simple_threads_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 결과가 '{filename}' 파일로 저장되었습니다.")
    
    def demo_search(self):
        """데모 검색 실행"""
        print("🎯 데모 검색을 실행합니다...")
        
        # 샘플 키워드들
        sample_keywords = ["AI", "technology", "programming"]
        
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
    print("🚀 Simple Threads 크롤러 시작!")
    print("=" * 60)
    
    crawler = SimpleThreadsCrawler()
    
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
        print("👋 Simple Threads 크롤러를 종료합니다.")

if __name__ == "__main__":
    main() 