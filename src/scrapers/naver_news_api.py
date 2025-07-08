import requests
from datetime import datetime, timedelta
from config import config

# 네이버 뉴스 검색 API

def search_naver_news(query, display=10, start=1, sort="date"):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": config.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": config.NAVER_CLIENT_SECRET,
    }
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort,  # date(최신순), sim(정확도순)
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        print("네이버 뉴스 API 오류:", response.text)
        return []

# 네이버 데이터랩(트렌드) API

def get_naver_trend_keywords(date=None, top_n=10):
    url = "https://openapi.naver.com/v1/datalab/search"
    headers = {
        "X-Naver-Client-Id": config.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": config.NAVER_CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    if date is None:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=1)
    else:
        end_date = date
        start_date = date
    body = {
        "startDate": str(start_date),
        "endDate": str(end_date),
        "timeUnit": "date",
        "keywordGroups": [
            {"groupName": "트렌드", "keywords": [""]}
        ],
        "device": "",
        "ages": [],
        "gender": ""
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        # 실제 인기 검색어는 데이터랩에서 바로 제공하지 않으므로, 예시로 빈 리스트 반환
        # 실시간 인기 검색어는 크롤링이 필요함
        return []
    else:
        print("트렌드 API 오류:", response.text)
        return [] 