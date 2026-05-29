from dataclasses import asdict, dataclass, field


@dataclass
class SearchResult:
    # Google 搜尋結果的排名。
    rank: int
    # 搜尋結果標題。
    title: str
    # 搜尋結果網址。
    url: str
    # 搜尋結果摘要。
    snippet: str


@dataclass
class EntityCount:
    # entity 名稱，例如「中華電信」。
    name: str
    # entity 類型，例如 PERSON / ORGANIZATION。
    entity_type: str
    # 在單篇文章中出現幾次。
    mentions: int
    # 相對重要度，這裡用簡化後的頻率比值表示。
    salience: float


@dataclass
class ArticleAnalysis:
    # 對應搜尋結果排名。
    rank: int
    title: str
    url: str
    snippet: str
    # 這篇文章所有 entity 的 mentions 加總。
    total_entity_mentions: int
    # 這篇文章一共有幾種不同 entity。
    unique_entity_count: int
    # 這篇文章分析出的 entity 明細。
    entities: list[EntityCount] = field(default_factory=list)

    def to_dict(self) -> dict:
        # dataclass 轉 dict，方便序列化或之後擴充 API 回傳。
        payload = asdict(self)
        payload["entities"] = [asdict(entity) for entity in self.entities]
        return payload


@dataclass
class AnalysisResponse:
    # 使用者輸入的查詢詞。
    query: str
    # 分析完成時間。
    analyzed_at: str
    # 這次總共分析幾篇文章。
    article_count: int
    # 所有文章分析結果。
    articles: list[ArticleAnalysis]
    # Google Sheet 同步狀態訊息。
    sheet_sync_message: str

    def to_dict(self) -> dict:
        # 統一輸出格式，前端或 API 都可以直接使用。
        return {
            "query": self.query,
            "analyzed_at": self.analyzed_at,
            "article_count": self.article_count,
            "sheet_sync_message": self.sheet_sync_message,
            "articles": [article.to_dict() for article in self.articles],
        }
