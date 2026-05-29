import requests
from bs4 import BeautifulSoup
from readability import Document


def extract_article_text(url: str) -> str:
    # 以一般瀏覽器樣式抓文章，降低部分網站直接擋 request 的機率。
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; Python-SERP-Entity-Analyzer/1.0)"
        },
        timeout=60,
    )
    response.raise_for_status()

    # 先取得原始 HTML，再交給 readability 抽主要內容區塊。
    html = response.text
    article_html = Document(html).summary()
    # 用 BeautifulSoup 去掉 HTML 標籤，只保留文字。
    text = BeautifulSoup(article_html, "html.parser").get_text(" ", strip=True)
    # 壓縮多餘空白並限制長度，避免後續分析成本過高。
    return " ".join(text.split())[:20000]
