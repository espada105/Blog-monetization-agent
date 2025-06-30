#!/usr/bin/env python3
"""
Threads 크롤러 테스트 스크립트
"""

import sys
import time
from simple_threads_crawler import SimpleThreadsCrawler

def test_crawler():
    """크롤러 기능 테스트"""
    print("🧪 Threads 크롤러 테스트 시작")
    print("=" * 50)
    
    crawler = SimpleThreadsCrawler()
    
    # 테스트 키워드
    test_keyword = "test"
    
    print(f"🔍 테스트 키워드: '{test_keyword}'")
    print("⏳ 크롤링 시작...")
    
    start_time = time.time()
    results = crawler.search_threads(test_keyword, 3)
    end_time = time.time()
    
    print(f"⏱️ 크롤링 시간: {end_time - start_time:.2f}초")
    
    if results:
        print(f"✅ 테스트 성공! {len(results)}개 결과 발견")
        print("\n📊 결과 요약:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['content'][:50]}...")
        return True
    else:
        print("❌ 테스트 실패: 결과가 없습니다")
        return False

def test_network():
    """네트워크 연결 테스트"""
    print("\n🌐 네트워크 연결 테스트")
    print("-" * 30)
    
    try:
        import requests
        response = requests.get("https://www.threads.net", timeout=5)
        if response.status_code == 200:
            print("✅ Threads 웹사이트 접근 가능")
            return True
        else:
            print(f"⚠️ HTTP 상태 코드: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 네트워크 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 Threads 크롤러 종합 테스트")
    print("=" * 50)
    
    # 네트워크 테스트
    network_ok = test_network()
    
    if not network_ok:
        print("\n❌ 네트워크 연결에 문제가 있습니다.")
        print("인터넷 연결을 확인해주세요.")
        return
    
    # 크롤러 테스트
    crawler_ok = test_crawler()
    
    print("\n" + "=" * 50)
    if crawler_ok:
        print("🎉 모든 테스트가 성공했습니다!")
        print("크롤러를 사용할 준비가 되었습니다.")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
        print("README.md의 문제 해결 섹션을 참고하세요.")
    
    print("\n사용 방법:")
    print("python simple_threads_crawler.py")

if __name__ == "__main__":
    main() 