from dataclasses import asdict, dataclass, field


@dataclass
class SearchResult:
    rank: int
    title: str
    url: str
    snippet: str


@dataclass
class EntityCount:
    name: str
    entity_type: str
    mentions: int
    salience: float


@dataclass
class ArticleAnalysis:
    rank: int
    title: str
    url: str
    snippet: str
    total_entity_mentions: int
    unique_entity_count: int
    entities: list[EntityCount] = field(default_factory=list)

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["entities"] = [asdict(entity) for entity in self.entities]
        return payload


@dataclass
class AnalysisResponse:
    query: str
    analyzed_at: str
    article_count: int
    articles: list[ArticleAnalysis]
    sheet_sync_message: str

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "analyzed_at": self.analyzed_at,
            "article_count": self.article_count,
            "sheet_sync_message": self.sheet_sync_message,
            "articles": [article.to_dict() for article in self.articles],
        }
