import requests

from app.models import SearchResult


def search_google_first_page(query: str, serpapi_key: str) -> list[SearchResult]:
    response = requests.get(
        "https://serpapi.com/search.json",
        params={
            "engine": "google",
            "q": query,
            "num": 10,
            "hl": "zh-tw",
            "gl": "tw",
            "api_key": serpapi_key,
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    results = []
    for index, item in enumerate(payload.get("organic_results", [])[:10], start=1):
        results.append(
            SearchResult(
                rank=index,
                title=item.get("title", "Untitled"),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
            )
        )
    return results
