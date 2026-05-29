from html import escape

from app.models import AnalysisResponse


def render_page(message: str = "", result: AnalysisResponse | None = None, user_email: str | None = None) -> str:
    result_html = '<div class="empty">登入後輸入關鍵字即可開始分析。</div>'
    if result:
        cards = []
        for article in result.articles:
            entities = "".join(
                f"""
                <div class="entity">
                    <strong>{escape(entity.name)}</strong>
                    <span>{escape(entity.entity_type)}</span>
                    <p>mentions {entity.mentions} | salience {entity.salience:.3f}</p>
                </div>
                """
                for entity in article.entities
            ) or "<p class='muted'>這篇文章沒有成功抓到 entity。</p>"
            cards.append(
                f"""
                <article class="card">
                    <div class="card-head">
                        <div>
                            <p class="eyebrow">Rank {article.rank}</p>
                            <h3>{escape(article.title)}</h3>
                            <a href="{escape(article.url)}" target="_blank" rel="noreferrer">{escape(article.url)}</a>
                        </div>
                        <div class="stat">
                            <p>總 mentions: {article.total_entity_mentions}</p>
                            <p>唯一 entity: {article.unique_entity_count}</p>
                        </div>
                    </div>
                    <p class="muted">{escape(article.snippet)}</p>
                    <div class="entities">{entities}</div>
                </article>
                """
            )
        result_html = f"""
        <section class="card">
            <p>查詢詞: <strong>{escape(result.query)}</strong></p>
            <p>Sheet 狀態: {escape(result.sheet_sync_message)}</p>
        </section>
        {''.join(cards)}
        """

    return f"""
    <!doctype html>
    <html lang="zh-Hant">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Python SERP Entity Analyzer</title>
        <style>
            body {{
                margin: 0;
                font-family: Georgia, "Noto Serif TC", serif;
                background:
                    radial-gradient(circle at top left, rgba(199, 92, 58, 0.16), transparent 30%),
                    radial-gradient(circle at top right, rgba(54, 125, 131, 0.18), transparent 28%),
                    linear-gradient(135deg, #f7f2e8 0%, #eef3f3 100%);
                color: #172126;
            }}
            .wrap {{ max-width: 1180px; margin: 0 auto; padding: 32px 16px 48px; }}
            .grid {{ display: grid; gap: 24px; }}
            .hero {{ display: grid; gap: 24px; grid-template-columns: 1.5fr 1fr; }}
            .card {{
                background: rgba(255, 252, 245, 0.82);
                border: 1px solid rgba(23, 33, 38, 0.14);
                border-radius: 28px;
                padding: 24px;
                box-shadow: 0 24px 60px rgba(23,33,38,0.08);
                backdrop-filter: blur(10px);
                margin-bottom: 16px;
            }}
            .eyebrow {{ text-transform: uppercase; letter-spacing: 0.3em; font-size: 12px; color: #7f2f1d; }}
            h1 {{ font-size: 52px; line-height: 1.1; margin: 12px 0; }}
            h2, h3, p {{ margin-top: 0; }}
            input {{
                width: 100%;
                box-sizing: border-box;
                border-radius: 999px;
                border: 1px solid rgba(23, 33, 38, 0.14);
                padding: 14px 18px;
                margin-bottom: 12px;
                background: rgba(255,255,255,0.78);
            }}
            button {{
                border: none;
                border-radius: 999px;
                padding: 12px 18px;
                background: #c75c3a;
                color: white;
                cursor: pointer;
            }}
            .secondary {{ background: #172126; }}
            .ghost {{ background: transparent; color: #172126; border: 1px solid rgba(23, 33, 38, 0.14); }}
            .row {{ display: flex; gap: 12px; flex-wrap: wrap; }}
            .muted {{ color: #63727a; }}
            .notice {{ margin-bottom: 16px; padding: 14px 18px; border-radius: 18px; background: #fff3cd; }}
            .card-head {{ display: flex; justify-content: space-between; gap: 16px; }}
            .stat {{ background: #f3efe5; border-radius: 18px; padding: 12px 16px; min-width: 160px; }}
            .entities {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
            .entity {{ border: 1px solid rgba(23,33,38,0.14); border-radius: 18px; padding: 14px; background: white; }}
            .entity span {{ float: right; color: #7f2f1d; font-size: 12px; }}
            .empty {{ padding: 48px; text-align: center; border: 1px dashed rgba(23,33,38,0.14); border-radius: 28px; }}
            @media (max-width: 900px) {{
                .hero {{ grid-template-columns: 1fr; }}
                h1 {{ font-size: 38px; }}
                .card-head {{ flex-direction: column; }}
            }}
        </style>
    </head>
    <body>
        <main class="wrap">
            <section class="hero">
                <div class="card">
                    <p class="eyebrow">Python Only</p>
                    <h1>自由輸入關鍵字，分析 Google 第一頁 entity，並寫入 Supabase / Google Sheet。</h1>
                    <p class="muted">目前整個專案邏輯都改成 Python。SERP 抓搜尋結果、文章解析、Google NLP entity、Google Sheet 寫入、Supabase 儲存與登入都在 Python 檔案內。</p>
                </div>
                <div class="card">
                    <p class="eyebrow">Login</p>
                    <h2>Supabase 帳密登入</h2>
                    <p class="muted">目前登入者: {escape(user_email or "尚未登入")}</p>
                    <form method="post" action="/login">
                        <input type="email" name="email" placeholder="Email" required>
                        <input type="password" name="password" placeholder="Password" required>
                        <div class="row">
                            <button class="secondary" type="submit">Sign In</button>
                        </div>
                    </form>
                    <form method="post" action="/signup">
                        <input type="email" name="email" placeholder="Email" required>
                        <input type="password" name="password" placeholder="Password" required>
                        <div class="row">
                            <button type="submit">Sign Up</button>
                            <button class="ghost" type="submit" formaction="/logout">Sign Out</button>
                        </div>
                    </form>
                </div>
            </section>
            <section class="card">
                <p class="eyebrow">Analyze</p>
                <h2>Google 第一頁前 10 名文章分析</h2>
                <form method="post" action="/analyze">
                    <input type="text" name="query" value="4G 吃到飽" required>
                    <button type="submit">開始分析</button>
                </form>
            </section>
            {f'<div class="notice">{escape(message)}</div>' if message else ''}
            <section class="grid">{result_html}</section>
        </main>
    </body>
    </html>
    """
