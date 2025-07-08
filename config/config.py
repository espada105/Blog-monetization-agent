# 티스토리 자동 포스팅 설정
# 이 파일을 수정하여 본인의 티스토리 정보를 입력하세요

# 티스토리 블로그 설정
TISTORY_BLOG_NAME = "your-blog.tistory.com"  # 본인의 블로그 주소로 변경
TISTORY_COOKIE = "your-cookie-here"  # 본인의 쿠키로 변경

# 카테고리 ID (선택사항)
# 티스토리 관리자 페이지에서 카테고리 ID를 확인할 수 있습니다
TISTORY_CATEGORY_ID = None  # 원하는 카테고리 ID 입력

# 태그 설정 (선택사항)
# TISTORY_TAGS = "BBC뉴스,글로벌트렌드,기술동향"

# Ollama 설정
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3:8b"

# BBC 뉴스 설정
BBC_CATEGORY = "all"  # all, world, technology, business, science, entertainment, health
BBC_LIMIT_PER_CATEGORY = 3

# 블로그 글 주제 설정
USE_AUTO_TOPIC = True  # True: LLM이 자동으로 주제 생성, False: 수동 설정 사용
BLOG_TOPIC = "글로벌 기술 트렌드와 시장 동향"  # USE_AUTO_TOPIC이 False일 때 사용

# 쿠키 얻는 방법:
# 1. 티스토리 관리자 페이지에 로그인
# 2. F12 개발자 도구 열기
# 3. Network 탭에서 아무 요청이나 클릭
# 4. Request Headers에서 Cookie 값을 복사
# 5. 위의 TISTORY_COOKIE에 붙여넣기 