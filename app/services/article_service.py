import requests
from bs4 import BeautifulSoup
from readability import Document


def extract_article_text(url: str) -> str:
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; Python-SERP-Entity-Analyzer/1.0)"
        },
        timeout=60,
    )
    response.raise_for_status()

    html = response.text
    article_html = Document(html).summary()
    text = BeautifulSoup(article_html, "html.parser").get_text(" ", strip=True)
    return " ".join(text.split())[:20000]
