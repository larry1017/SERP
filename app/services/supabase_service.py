from supabase import Client, create_client

from app.models import AnalysisResponse


def create_supabase_client(url: str, key: str) -> Client:
    # 建立後端使用的 Supabase client。
    return create_client(url, key)


def save_analysis(client: Client, analysis: AnalysisResponse, user_id: str) -> str:
    # 先存一筆「這次查詢」到 analysis_runs。
    run_response = (
        client.table("analysis_runs")
        .insert(
            {
                "user_id": user_id,
                "query": analysis.query,
                "analyzed_at": analysis.analyzed_at,
                "article_count": analysis.article_count,
            }
        )
        .execute()
    )
    run_id = run_response.data[0]["id"]

    # 再逐篇存文章，並把 run_id 關聯回這次查詢。
    for article in analysis.articles:
        article_response = (
            client.table("analysis_articles")
            .insert(
                {
                    "run_id": run_id,
                    "rank": article.rank,
                    "title": article.title,
                    "url": article.url,
                    "snippet": article.snippet,
                    "total_entity_mentions": article.total_entity_mentions,
                    "unique_entity_count": article.unique_entity_count,
                }
            )
            .execute()
        )
        article_id = article_response.data[0]["id"]
        # 如果有 entity，就把每個 entity 再展開成獨立資料列。
        if article.entities:
            client.table("analysis_entities").insert(
                [
                    {
                        "article_id": article_id,
                        "name": entity.name,
                        "entity_type": entity.entity_type,
                        "mentions": entity.mentions,
                        "salience": entity.salience,
                    }
                    for entity in article.entities
                ]
            ).execute()

    return run_id
