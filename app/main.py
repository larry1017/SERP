from flask import Flask, redirect, request, session

from app.config import load_settings, validate_settings
from app.render import render_page
from app.services.analysis_service import build_analysis
from app.services.auth_service import sign_in_with_password, sign_up_with_password
from app.services.sheet_service import sync_analysis_to_sheet
from app.services.supabase_service import create_supabase_client, save_analysis

# 建立 Flask app 實例。
app = Flask(__name__)
# 啟動時讀一次設定。
settings = load_settings()
# session 需要 secret key 才能工作。
app.secret_key = settings.secret_key


@app.get("/")
def home():
    # 首頁只負責顯示目前訊息與登入狀態。
    return render_page(
        message=request.args.get("message", ""),
        user_email=session.get("user_email"),
    )


@app.post("/signup")
def signup():
    try:
        # 用 Supabase Auth 建立新帳號。
        result = sign_up_with_password(
            settings.supabase_url,
            settings.supabase_anon_key,
            request.form["email"],
            request.form["password"],
        )
        return redirect(f"/?message=註冊成功，帳號 {result['email']} 已建立")
    except Exception as error:
        # 任何註冊錯誤都回首頁並帶上訊息。
        return redirect(f"/?message=註冊失敗: {error}")


@app.post("/login")
def login():
    try:
        # 用 email/password 向 Supabase 驗證。
        result = sign_in_with_password(
            settings.supabase_url,
            settings.supabase_anon_key,
            request.form["email"],
            request.form["password"],
        )
        # 登入成功後，把必要使用者資訊放進 session。
        session["access_token"] = result["access_token"]
        session["refresh_token"] = result["refresh_token"]
        session["user_id"] = result["user_id"]
        session["user_email"] = result["email"]
        return redirect("/?message=登入成功")
    except Exception as error:
        return redirect(f"/?message=登入失敗: {error}")


@app.post("/logout")
def logout():
    # 清空 session 代表使用者登出。
    session.clear()
    return redirect("/?message=已登出")


@app.post("/analyze")
def analyze():
    # 先確認外部服務設定是否齊全。
    missing = validate_settings(settings)
    if missing:
        return render_page(
            message=f"缺少環境變數: {', '.join(missing)}",
            user_email=session.get("user_email"),
        )
    # 這個系統要求先登入才可執行分析。
    if not session.get("user_id"):
        return render_page(message="請先登入再執行分析。")

    # 讀取使用者輸入的搜尋詞，並去掉前後空白。
    query = request.form.get("query", "").strip()
    if not query:
        return render_page(message="請輸入關鍵字。", user_email=session.get("user_email"))

    try:
        # 第一步：建立整份 SERP / entity 分析結果。
        analysis = build_analysis(
            query,
            settings.serpapi_key,
        )
        # 第二步：把結果同步到 Google Sheet。
        analysis.sheet_sync_message = sync_analysis_to_sheet(
            analysis,
            settings.google_sheet_key,
            settings.google_client_email,
            settings.google_private_key,
        )
        # 第三步：把結果結構化寫進 Supabase。
        supabase_client = create_supabase_client(settings.supabase_url, settings.supabase_key)
        save_analysis(supabase_client, analysis, session["user_id"])
        # 最後把分析結果重新渲染回首頁。
        return render_page(
            message="分析完成，資料已寫入 Supabase 與 Google Sheet。",
            result=analysis,
            user_email=session.get("user_email"),
        )
    except Exception as error:
        # 任何分析流程中的錯誤都直接顯示給使用者看。
        return render_page(
            message=f"分析失敗: {error}",
            user_email=session.get("user_email"),
        )


@app.get("/health")
def health():
    # 給部署平台或本機檢查服務是否存活。
    return {"ok": True, "service": "python-serp-entity-analyzer"}
