from datetime import datetime, timezone

from app.models import AnalysisResponse, ArticleAnalysis
from app.services.article_service import extract_article_text
from app.services.entity_service import analyze_entities
from app.services.serp_service import search_google_first_page


def build_analysis(query: str, serpapi_key: str) -> AnalysisResponse:
    serp_results = search_google_first_page(query, serpapi_key)
    articles = []

    for result in serp_results:
        try:
            article_text = extract_article_text(result.url)
            entities = analyze_entities(article_text)[:20]
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
        articles.append(article)

    return AnalysisResponse(
        query=query,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
        article_count=len(articles),
        articles=articles,
        sheet_sync_message="Not synced yet.",
    )
