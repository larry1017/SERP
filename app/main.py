from flask import Flask, redirect, request, session

from app.config import load_settings, validate_settings
from app.render import render_page
from app.services.analysis_service import build_analysis
from app.services.auth_service import sign_in_with_password, sign_up_with_password
from app.services.sheet_service import sync_analysis_to_sheet
from app.services.supabase_service import create_supabase_client, save_analysis

app = Flask(__name__)
settings = load_settings()
app.secret_key = settings.secret_key


@app.get("/")
def home():
    return render_page(
        message=request.args.get("message", ""),
        user_email=session.get("user_email"),
    )


@app.post("/signup")
def signup():
    try:
        result = sign_up_with_password(
            settings.supabase_url,
            settings.supabase_anon_key,
            request.form["email"],
            request.form["password"],
        )
        return redirect(f"/?message=註冊成功，帳號 {result['email']} 已建立")
    except Exception as error:
        return redirect(f"/?message=註冊失敗: {error}")


@app.post("/login")
def login():
    try:
        result = sign_in_with_password(
            settings.supabase_url,
            settings.supabase_anon_key,
            request.form["email"],
            request.form["password"],
        )
        session["access_token"] = result["access_token"]
        session["refresh_token"] = result["refresh_token"]
        session["user_id"] = result["user_id"]
        session["user_email"] = result["email"]
        return redirect("/?message=登入成功")
    except Exception as error:
        return redirect(f"/?message=登入失敗: {error}")


@app.post("/logout")
def logout():
    session.clear()
    return redirect("/?message=已登出")


@app.post("/analyze")
def analyze():
    missing = validate_settings(settings)
    if missing:
        return render_page(
            message=f"缺少環境變數: {', '.join(missing)}",
            user_email=session.get("user_email"),
        )
    if not session.get("user_id"):
        return render_page(message="請先登入再執行分析。")

    query = request.form.get("query", "").strip()
    if not query:
        return render_page(message="請輸入關鍵字。", user_email=session.get("user_email"))

    try:
        analysis = build_analysis(
            query,
            settings.serpapi_key,
        )
        analysis.sheet_sync_message = sync_analysis_to_sheet(
            analysis,
            settings.google_sheet_key,
            settings.google_client_email,
            settings.google_private_key,
        )
        supabase_client = create_supabase_client(settings.supabase_url, settings.supabase_key)
        save_analysis(supabase_client, analysis, session["user_id"])
        return render_page(
            message="分析完成，資料已寫入 Supabase 與 Google Sheet。",
            result=analysis,
            user_email=session.get("user_email"),
        )
    except Exception as error:
        return render_page(
            message=f"分析失敗: {error}",
            user_email=session.get("user_email"),
        )


@app.get("/health")
def health():
    return {"ok": True, "service": "python-serp-entity-analyzer"}
