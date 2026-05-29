import os
from collections import defaultdict

import gspread
import matplotlib.pyplot as plt
import pandas as pd
from google.oauth2.service_account import Credentials
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


def build_credentials_from_env():
    return Credentials.from_service_account_info(
        {
            "type": "service_account",
            "client_email": os.environ["GOOGLE_CLOUD_CLIENT_EMAIL"],
            "private_key": os.environ["GOOGLE_CLOUD_PRIVATE_KEY"].replace("\\n", "\n"),
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=SCOPE,
    )


def load_sheet(sheet_key: str, worksheet_name: str) -> pd.DataFrame:
    client = gspread.authorize(build_credentials_from_env())
    worksheet = client.open_by_key(sheet_key).worksheet(worksheet_name)
    return pd.DataFrame(worksheet.get_all_records())


def write_sheet(sheet_key: str, worksheet_name: str, df: pd.DataFrame):
    client = gspread.authorize(build_credentials_from_env())
    spreadsheet = client.open_by_key(sheet_key)

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
        worksheet.clear()
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)

    rows = [df.columns.tolist()] + df.astype(str).values.tolist()
    worksheet.update(rows)


def cluster_entities(df: pd.DataFrame, cluster_count: int = 5) -> pd.DataFrame:
    grouped = defaultdict(list)
    for _, row in df.iterrows():
        grouped[str(row["entity_name"])].append(str(row["article_title"]))

    entities = list(grouped.keys())
    if not entities:
        return pd.DataFrame(columns=["entity_name", "cluster"])

    corpus = [" ".join(grouped[entity]) for entity in entities]
    matrix = TfidfVectorizer().fit_transform(corpus)
    model = KMeans(n_clusters=min(cluster_count, len(entities)), random_state=42, n_init="auto")
    labels = model.fit_predict(matrix)

    return pd.DataFrame({"entity_name": entities, "cluster": labels})


def draw_cluster_chart(cluster_df: pd.DataFrame, output_path: str):
    if cluster_df.empty:
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, "No entities available for clustering", ha="center", va="center")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        return

    counts = cluster_df.groupby("cluster")["entity_name"].count().reset_index(name="entity_count")
    plt.figure(figsize=(10, 6))
    plt.bar(counts["cluster"].astype(str), counts["entity_count"], color="#c75c3a")
    plt.title("Entity Topic Clusters")
    plt.xlabel("Cluster")
    plt.ylabel("Entity Count")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)


def main():
    sheet_key = os.environ["GOOGLE_SHEET_KEY"]
    cluster_df = cluster_entities(load_sheet(sheet_key, "entities"))
    cluster_df.to_csv("entity_clusters.csv", index=False)
    write_sheet(sheet_key, "clusters", cluster_df)
    draw_cluster_chart(cluster_df, "entity_clusters.png")
    print("Generated entity_clusters.csv and entity_clusters.png, then wrote clusters worksheet.")


if __name__ == "__main__":
    main()
