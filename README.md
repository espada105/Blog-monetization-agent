# BBC 뉴스 자동 블로그 포스터

BBC 뉴스를 수집하여 자동으로 티스토리 블로그에 포스팅하는 시스템입니다.

## 📁 프로젝트 구조

```
Blog-monetization-agent/
├── src/                    # 소스 코드
│   ├── core/              # 핵심 모듈
│   │   ├── bbc_news_processor.py
│   │   ├── auto_blog_poster.py
│   │   ├── run_auto_posting.py
│   │   └── test_upload.py
│   ├── scrapers/          # 스크래핑 관련
│   │   ├── bbc_rss_crawler.py
│   │   └── bbc_api_client.py
│   └── posters/           # 포스팅 관련
│       ├── tistory_selenium_poster.py
│       └── tistory_auto_poster.py
├── config/                 # 설정 파일들
│   ├── config.py
│   └── tistory_config.json
├── scripts/               # 실행 스크립트들
│   ├── run_bbc_processor.bat
│   ├── run_tistory_poster.bat
│   ├── run_ollama_server.bat
│   └── create_shortcuts.ps1
├── data/                  # 데이터 폴더들
│   ├── bbc_news/
│   ├── bbc_news_json/
│   └── blog_posts/
├── logs/                  # 로그 파일들
├── docs/                  # 문서
├── main.py               # 메인 실행 파일
└── requirements.txt      # 의존성 파일
```

## 🚀 사용법

### 1. 환경 설정

1. **가상환경 생성 및 활성화**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

2. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **설정 파일 수정**
   - `config/config.py`: 티스토리 블로그 정보 및 Ollama 설정
   - `config/tistory_config.json`: 티스토리 자동 로그인 정보

### 2. 실행 방법

#### 방법 1: 메인 실행 파일 사용
```bash
python main.py
```

#### 방법 2: 개별 스크립트 사용
```bash
# BBC 뉴스 수집 및 블로그 글 생성
python src/core/bbc_news_processor.py

# 티스토리 자동 포스팅
python src/posters/tistory_selenium_poster.py --auto
```

#### 방법 3: 배치 파일 사용 (Windows)
```bash
# BBC 뉴스 프로세서 실행
scripts/run_bbc_processor.bat

# 티스토리 자동 포스터 실행
scripts/run_tistory_poster.bat
```

### 3. 설정 파일 설명

#### config/config.py
```python
# 티스토리 블로그 설정
TISTORY_BLOG_NAME = "your-blog.tistory.com"
TISTORY_COOKIE = "your-cookie-here"

# Ollama 설정
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3:8b"

# BBC 뉴스 설정
BBC_CATEGORY = "all"  # all, world, technology, business, science
BBC_LIMIT_PER_CATEGORY = 3
```

#### config/tistory_config.json
```json
{
  "blog_url": "https://your-blog.tistory.com",
  "kakao_email": "your-email@example.com",
  "kakao_password": "your-password",
  "default_category": "IT",
  "default_tags": "BBC뉴스,글로벌트렌드,기술동향"
}
```

## 🔧 주요 기능

1. **BBC 뉴스 수집**: RSS 피드를 통해 최신 BBC 뉴스 수집
2. **LLM 기반 글 생성**: Ollama를 사용한 자동 블로그 글 생성
3. **티스토리 자동 포스팅**: 셀레니움을 사용한 자동 포스팅
4. **마크다운 지원**: 전문적인 마크다운 형식의 글 작성

## 📝 로그 확인

- 실행 로그는 콘솔에 출력됩니다
- 생성된 파일들은 `data/` 폴더에 저장됩니다
  - `data/bbc_news_json/`: 수집된 뉴스 데이터
  - `data/blog_posts/`: 생성된 블로그 글

## ⚠️ 주의사항

1. **Ollama 서버 실행**: LLM 기능을 사용하려면 Ollama 서버가 실행 중이어야 합니다
2. **티스토리 로그인**: 자동 포스팅을 위해 티스토리 계정 정보가 필요합니다
3. **Chrome 브라우저**: 셀레니움 자동화를 위해 Chrome 브라우저가 설치되어 있어야 합니다

## 🛠️ 문제 해결

### 경로 문제
- 모든 파일 경로는 상대 경로로 설정되어 있어 프로젝트 루트에서 실행해야 합니다
- 가상환경이 활성화되어 있는지 확인하세요

### 의존성 문제
```bash
pip install --upgrade -r requirements.txt
```

### Ollama 연결 문제
```bash
# Ollama 서버 시작
ollama serve

# 모델 다운로드
ollama pull llama3:8b
``` 