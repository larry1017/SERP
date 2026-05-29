import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    secret_key: str
    serpapi_key: str
    supabase_url: str
    supabase_anon_key: str
    supabase_key: str
    google_client_email: str
    google_private_key: str
    google_sheet_key: str


def load_settings() -> Settings:
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
