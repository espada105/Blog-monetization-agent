import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.scrapers.naver_news_api import search_naver_news
from config import config
import requests

def summarize_news_with_llm(news_list, keyword):
    prompt = f"다음은 '{keyword}'에 대한 최신 뉴스 기사 목록입니다. 각 기사의 주요 내용을 요약해 주세요.\n"
    for news in news_list:
        prompt += f"- {news['title']} ({news['link']})\n"
    # Ollama LLM API 호출
    response = requests.post(
        f"{config.OLLAMA_URL}/api/generate",
        json={
            "model": config.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1024
            }
        },
        timeout=60
    )
    if response.status_code == 200:
        return response.json()["response"].strip()
    else:
        return f"[LLM 오류] {response.text}"

def save_json(data, keyword):
    today_str = datetime.now().strftime('%Y-%m-%d')
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'naver_trend_json')
    os.makedirs(out_dir, exist_ok=True)
    filename = os.path.join(out_dir, f"naver_trend_{keyword}_{today_str}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename

def save_markdown(summary_dict):
    today_str = datetime.now().strftime('%Y-%m-%d')
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'naver_trend_blog_posts')
    os.makedirs(out_dir, exist_ok=True)
    filename = os.path.join(out_dir, f"naver_trend_blog_{today_str}.md")
    with open(filename, 'w', encoding='utf-8') as f:
        for keyword, info in summary_dict.items():
            f.write(f"# {keyword} 뉴스 요약\n\n")
            f.write("## 기사 목록\n")
            for news in info['news']:
                f.write(f"- [{news['title']}]({news['link']})\n")
            f.write("\n## LLM 요약\n")
            f.write(info['summary'] + "\n\n---\n\n")
    return filename

def post_to_tistory_with_selenium(md_file):
    # 셀레니움 포스터 실행
    poster_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src', 'posters', 'tistory_selenium_poster.py')
    import subprocess
    import sys
    cmd = [
        sys.executable, poster_path,
        "--file", md_file,
        "--auto"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("블로그 자동 업로드 완료!")
    else:
        print(f"블로그 업로드 오류: {result.stderr}")

def main():
    print("[사용자 지정 키워드 기반 뉴스 요약]")
    keywords = ["경제", "주식", "정치", "나스닥", "코스닥", "미국", "한국"]
    print(f"키워드: {keywords}")
    summary_dict = {}
    for keyword in keywords:
        print(f"\n[키워드: {keyword}] 뉴스 기사 수집 중...")
        news_list = search_naver_news(keyword, display=5)
        for news in news_list:
            print(f"- {news['title']} | {news['link']}")
        summary = summarize_news_with_llm(news_list, keyword)
        print("\n[LLM 요약 결과]")
        print(summary)
        # JSON 저장
        json_data = {
            "keyword": keyword,
            "news": news_list,
            "summary": summary
        }
        save_json(json_data, keyword)
        summary_dict[keyword] = {"news": news_list, "summary": summary}
        print("-"*60)
    # 마크다운 저장 및 블로그 업로드
    md_file = save_markdown(summary_dict)
    print(f"\n마크다운 저장 완료: {md_file}")
    post_to_tistory_with_selenium(md_file)

if __name__ == "__main__":
    main() 