import gspread
from google.oauth2.service_account import Credentials

from app.models import AnalysisResponse


SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


def _get_client(client_email: str, private_key: str) -> gspread.Client:
    credentials = Credentials.from_service_account_info(
        {
            "type": "service_account",
            "client_email": client_email,
            "private_key": private_key,
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=SCOPE,
    )
    return gspread.authorize(credentials)


def _get_or_create_worksheet(spreadsheet: gspread.Spreadsheet, name: str) -> gspread.Worksheet:
    try:
        return spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=name, rows=1000, cols=20)


def sync_analysis_to_sheet(
    analysis: AnalysisResponse, sheet_key: str, client_email: str, private_key: str
) -> str:
    client = _get_client(client_email, private_key)
    spreadsheet = client.open_by_key(sheet_key)

    summary_sheet = _get_or_create_worksheet(spreadsheet, "summary")
    entities_sheet = _get_or_create_worksheet(spreadsheet, "entities")

    summary_rows = [[
        "query",
        "analyzed_at",
        "rank",
        "title",
        "url",
        "snippet",
        "total_mentions",
        "unique_entities",
    ]]
    entity_rows = [[
        "query",
        "rank",
        "article_title",
        "entity_name",
        "entity_type",
        "mentions",
        "salience",
    ]]

    for article in analysis.articles:
        summary_rows.append([
            analysis.query,
            analysis.analyzed_at,
            article.rank,
            article.title,
            article.url,
            article.snippet,
            article.total_entity_mentions,
            article.unique_entity_count,
        ])
        for entity in article.entities:
            entity_rows.append([
                analysis.query,
                article.rank,
                article.title,
                entity.name,
                entity.entity_type,
                entity.mentions,
                entity.salience,
            ])

    summary_sheet.clear()
    summary_sheet.update(summary_rows)
    entities_sheet.clear()
    entities_sheet.update(entity_rows)
    return "Google Sheet sync completed."
