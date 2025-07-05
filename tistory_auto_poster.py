import requests
import json
import re
from datetime import datetime
import config
import os

class TistoryAutoPoster:
    def __init__(self, blog_name, cookie):
        self.blog_name = blog_name
        self.cookie = cookie
        self.session = requests.Session()
        
        # 블로그 정보 (HTML에서 추출)
        self.blog_id = "8102681"  # aigent-hong.tistory.com의 블로그 ID
        self.categories = {
            "주식": 1263075,
            "비트코인": 1263076, 
            "프로그래밍": 1263077,
            "IT": 1263078,
            "밈": 1263079,
            "연예계": 1263080,
            "정치": 1263081
        }
        
        # 쿠키 설정
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cookie': cookie,
            'Referer': f'https://{blog_name}/manage/newpost/',
            'Origin': f'https://{blog_name}'
        })
    
    def convert_markdown_to_html(self, markdown_content):
        """마크다운을 HTML로 변환"""
        # 기본 마크다운 변환
        html = markdown_content
        
        # 제목 변환
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        
        # 강조 변환
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # 링크 변환
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        # 줄바꿈 변환
        html = html.replace('\n', '<br>\n')
        
        # 단락 변환
        html = re.sub(r'<br>\n<br>\n', '</p>\n<p>', html)
        html = f'<p>{html}</p>'
        
        return html
    
    def post_blog_from_file(self, markdown_file, category_id=None, tags=None):
        """마크다운 파일을 읽어서 티스토리에 포스팅"""
        try:
            # 마크다운 파일 읽기
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 제목과 본문 분리
            lines = content.split('\n')
            title = ""
            body_content = []
            
            for line in lines:
                if line.startswith('# ') and not title:
                    title = line[2:].strip()
                else:
                    body_content.append(line)
            
            if not title:
                title = f"BBC 뉴스 분석 - {datetime.now().strftime('%Y년 %m월 %d일')}"
            
            body = '\n'.join(body_content).strip()
            
            # 마크다운을 HTML로 변환
            html_content = self.convert_markdown_to_html(body)
            
            # 포스팅 실행
            return self.post_blog(title, html_content, category_id, tags)
            
        except Exception as e:
            print(f"❌ 파일 읽기 오류: {e}")
            return None
    
    def post_blog(self, title, content, category_id=None, tags=None):
        """티스토리에 블로그 포스팅"""
        try:
            # 글쓰기 페이지 접속 (세션 유지)
            write_url = f"https://{self.blog_name}/manage/newpost/?type=post&returnURL=%2Fmanage%2Fposts%2F"
            response = self.session.get(write_url)
            
            if response.status_code != 200:
                print(f"❌ 글쓰기 페이지 접속 실패: {response.status_code}")
                return None
            
            # 실제 글쓰기 API 호출 (다른 엔드포인트 시도)
            post_url = f"https://{self.blog_name}/manage/entry/post"
            
            # 포스팅 데이터 구성 (티스토리 API 형식에 맞춤)
            post_data = {
                "id": "0",  # 새 글
                "title": title,
                "content": content,
                "slogan": "",
                "visibility": 20,  # 공개
                "category": category_id if category_id else self.categories.get("IT", 1263078),
                "tag": tags if tags else "BBC뉴스,글로벌트렌드,기술동향",
                "published": 1,
                "password": "",
                "uselessMarginForEntry": 1,
                "daumLike": "401",
                "cclCommercial": 0,
                "cclDerive": 0,
                "thumbnail": None,
                "type": "post",
                "attachments": [],
                "recaptchaValue": "",
                "draftSequence": None
            }
            
            # 헤더 업데이트
            self.session.headers.update({
                'Content-Type': 'application/json;charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': write_url
            })
            
            # POST 요청
            response = self.session.post(post_url, json=post_data)
            
            print(f"📡 응답 상태: {response.status_code}")
            print(f"📡 응답 내용: {response.text[:200]}...")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('status') == 'success' or result.get('id'):
                        print("✅ 포스팅 성공!")
                        return result
                    else:
                        print(f"❌ 포스팅 실패: {result}")
                        return None
                except:
                    print("✅ 포스팅 성공 (JSON 파싱 실패했지만 200 응답)")
                    return {"status": "success", "response": response.text}
            else:
                print(f"❌ 포스팅 실패: {response.status_code}")
                print(f"응답: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 포스팅 중 오류: {e}")
            return None
    
    def get_categories(self):
        """카테고리 목록 반환"""
        return self.categories
    
    def get_blog_info(self):
        """블로그 정보 반환"""
        return {
            "blog_id": self.blog_id,
            "blog_name": self.blog_name,
            "categories": self.categories
        }

# 사용 예시
def main():
    # 설정
    BLOG_NAME = "your-blog.tistory.com"  # 본인의 블로그 주소
    COOKIE = "your-cookie-here"  # 본인의 쿠키
    
    # 티스토리 포스터 초기화
    poster = TistoryAutoPoster(BLOG_NAME, COOKIE)
    
    # 블로그 글 파일에서 포스팅
    blog_file = "blog_posts/blog_글로벌_기술_트렌드와_시장_동향_2025-07-05.md"
    
    if os.path.exists(blog_file):
        print(f"📝 블로그 글 포스팅 중: {blog_file}")
        result = poster.post_blog_from_file(
            blog_file,
            category_id=1157903,  # 카테고리 ID (선택사항)
            tags="BBC뉴스,글로벌트렌드,기술동향"  # 태그 (선택사항)
        )
        
        if result:
            print("🎉 티스토리 포스팅 완료!")
        else:
            print("❌ 포스팅 실패")
    else:
        print(f"❌ 파일을 찾을 수 없습니다: {blog_file}")

if __name__ == "__main__":
    main() 