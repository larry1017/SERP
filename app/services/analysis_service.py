from datetime import datetime, timezone

from app.models import AnalysisResponse, ArticleAnalysis
from app.services.article_service import extract_article_text
from app.services.entity_service import analyze_entities
from app.services.serp_service import search_google_first_page


def build_analysis(query: str, serpapi_key: str) -> AnalysisResponse:
    # 先抓 Google 第一頁搜尋結果。
    serp_results = search_google_first_page(query, serpapi_key)
    # 存放每篇文章分析結果。
    articles = []

    for result in serp_results:
        try:
            # 先把搜尋結果網址轉成乾淨正文文字。
            article_text = extract_article_text(result.url)
            # 再從正文中擷取 entity，最多保留前 20 個。
            entities = analyze_entities(article_text)[:20]
            # 把單篇文章的分析結果包成結構化物件。
            article = ArticleAnalysis(
                rank=result.rank,
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                total_entity_mentions=sum(entity.mentions for entity in entities),
                unique_entity_count=len(entities),
                entities=entities,
            )
        except Exception as error:
            # 某篇文章失敗時不要整批中斷，保留錯誤資訊繼續往下跑。
            article = ArticleAnalysis(
                rank=result.rank,
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                total_entity_mentions=0,
                unique_entity_count=0,
                entities=[],
            )
            article.snippet = f"{result.snippet} | analysis_error: {error}"
        # 不管成功或失敗，都把這篇結果收進清單。
        articles.append(article)

    # 全部完成後，再回傳整次查詢的總結果。
    return AnalysisResponse(
        query=query,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
        article_count=len(articles),
        articles=articles,
        sheet_sync_message="Not synced yet.",
    )
