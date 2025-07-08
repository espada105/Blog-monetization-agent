import requests
from bs4 import BeautifulSoup

def get_naver_realtime_keywords(top_n=10):
    url = "https://datalab.naver.com/keyword/realtimeList.naver"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("네이버 실시간 트렌드 크롤링 오류:", response.text)
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    keywords = []
    for item in soup.select(".item_title")[:top_n]:
        keywords.append(item.get_text(strip=True))
    return keywords

if __name__ == "__main__":
    print(get_naver_realtime_keywords(10)) 