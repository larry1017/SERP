# SERP Entity Analyzer Python 版

這個版本把原本的前後端都改成 Python，方便直接閱讀：

- `api/index.py`: Vercel 入口
- `app/main.py`: Flask 網頁與路由
- `app/services/*.py`: SERP、文章解析、Google NLP、Google Sheet、Supabase、登入
- `scripts/python/entity_cluster.py`: entity 主題分群與畫圖
- `scripts/python/supabase_schema.py`: Supabase SQL schema 字串

## 功能

- 自由輸入關鍵字，例如 `4G 吃到飽`
- 用 `SerpAPI` 抓 Google 第一頁前 10 名自然搜尋結果
- 抓文章內容並用本地 Python NLP 計算每篇文章的 entity 數量與各 entity mentions
- 直接用 Python 寫入 `Google Sheet`
- 儲存到 `Supabase`
- 支援 `Supabase email/password` 登入
- 用 Python 腳本做 entity 分群並畫圖

## 安裝

```bash
pip install -r requirements.txt
```

建議在專案根目錄建立 `.env`，之後就不用每次手動 `set`。

## 環境變數

```env
FLASK_SECRET_KEY=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
SERPAPI_KEY=
GOOGLE_CLOUD_CLIENT_EMAIL=
GOOGLE_CLOUD_PRIVATE_KEY=
GOOGLE_SHEET_KEY=
```

`GOOGLE_CLOUD_CLIENT_EMAIL` 與 `GOOGLE_CLOUD_PRIVATE_KEY` 現在只拿來寫 Google Sheet，不再呼叫 Google Cloud 付費 NLP API。
`GOOGLE_CLOUD_PRIVATE_KEY` 在 Vercel 可用 `\n` 保存換行。

你可以直接複製 `.env.example` 成 `.env`，再把值補上。

## 本機啟動

```bash
cmd /c run.cmd
```

開啟 `http://127.0.0.1:5000`。

如果你想手動執行，也可以：

```cmd
cd /d C:\Users\andy9\Desktop\面
.venv\Scripts\activate.bat
set FLASK_APP=app.main
flask run
```

## Supabase 設定

1. 建立 Supabase 專案
2. 到 SQL Editor 執行 `python scripts/python/supabase_schema.py` 印出的 SQL
3. 在 Authentication 開啟 Email / Password
4. 填好 `SUPABASE_URL`、`SUPABASE_ANON_KEY` 與 `SUPABASE_SERVICE_ROLE_KEY`

## Google Sheet 設定

1. 建立 Google Sheet
2. 取得 Sheet ID 填進 `GOOGLE_SHEET_KEY`
3. 建立 Google Service Account，下載 JSON，從中取出 `client_email` 與 `private_key`
4. 將 Google Service Account 加入這份 Sheet 的共用名單
5. 程式會自動建立或覆蓋 `summary`、`entities`、`clusters` 工作表

## Vercel 部署

1. 推到 GitHub
2. 在 Vercel 匯入 repo
3. 把 `.env.example` 的環境變數填進 Vercel
4. 直接部署，Vercel 會從 [api/index.py](api/index.py) 啟動 Flask app

## Entity 分群

```bash
python scripts/python/entity_cluster.py
```

會輸出：

- `entity_clusters.csv`
- `entity_clusters.png`
- 回寫 `clusters` worksheet

## 備註

- 若網站阻擋內容抓取，該篇文章會保留搜尋結果但 entity 可能為 0。
- 這版已移除 AppScript、Next.js、TypeScript，核心程式都改成 Python。
- entity 抽取現在採本地 `jieba` 規則式方法，不需要開通 Google Cloud Natural Language API。
