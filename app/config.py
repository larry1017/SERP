import os
from dataclasses import dataclass

from dotenv import load_dotenv


# 啟動時先嘗試把 .env 載入到環境變數中。
load_dotenv()


@dataclass
class Settings:
    # Flask session 用的密鑰。
    secret_key: str
    # SerpAPI 金鑰，用來抓 Google 搜尋結果。
    serpapi_key: str
    # Supabase 專案 URL。
    supabase_url: str
    # 給前端登入 / 註冊用的 anon key。
    supabase_anon_key: str
    # 給後端寫資料庫用的 service role key。
    supabase_key: str
    # Google service account 的 client email。
    google_client_email: str
    # Google service account 的 private key。
    google_private_key: str
    # 要寫入的 Google Sheet ID。
    google_sheet_key: str


def load_settings() -> Settings:
    # 把所有設定集中整理成單一物件，方便其他模組使用。
    return Settings(
        secret_key=os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me"),
        serpapi_key=os.getenv("SERPAPI_KEY", ""),
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY", ""),
        supabase_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        google_client_email=os.getenv("GOOGLE_CLOUD_CLIENT_EMAIL", ""),
        google_private_key=os.getenv("GOOGLE_CLOUD_PRIVATE_KEY", "").replace("\\n", "\n"),
        google_sheet_key=os.getenv("GOOGLE_SHEET_KEY", ""),
    )


def validate_settings(settings: Settings) -> list[str]:
    # 啟動分析前，先檢查必要設定是否都已經提供。
    missing = []
    if not settings.serpapi_key:
        missing.append("SERPAPI_KEY")
    if not settings.supabase_url:
        missing.append("SUPABASE_URL")
    if not settings.supabase_anon_key:
        missing.append("SUPABASE_ANON_KEY")
    if not settings.supabase_key:
        missing.append("SUPABASE_SERVICE_ROLE_KEY")
    if not settings.google_client_email:
        missing.append("GOOGLE_CLOUD_CLIENT_EMAIL")
    if not settings.google_private_key:
        missing.append("GOOGLE_CLOUD_PRIVATE_KEY")
    if not settings.google_sheet_key:
        missing.append("GOOGLE_SHEET_KEY")
    return missing
