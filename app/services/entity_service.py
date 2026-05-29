import re
from collections import Counter

import jieba.posseg as pseg

from app.models import EntityCount


# 只保留比較像名詞 / 實體的詞性，避免分析結果太雜。
ALLOWED_POS_PREFIXES = ("n", "nr", "ns", "nt", "nz", "eng")
# 常見但沒有分析價值的詞先過濾掉。
STOPWORDS = {
    "今天",
    "目前",
    "方案",
    "資費",
    "月租",
    "用戶",
    "網友",
    "內容",
    "服務",
    "網站",
    "文章",
    "表示",
    "可以",
    "以及",
    "如果",
    "提供",
}


def _normalize_token(token: str) -> str:
    # 去前後空白，並把詞內多餘空白壓成無空白。
    token = token.strip()
    token = re.sub(r"\s+", "", token)
    return token


def _guess_entity_type(word: str, flag: str) -> str:
    # 先根據 jieba 詞性做第一層分類。
    if flag.startswith("nr"):
        return "PERSON"
    if flag.startswith("ns"):
        return "LOCATION"
    if flag.startswith("nt"):
        return "ORGANIZATION"
    # 再用關鍵字規則補強，讓常見電信主題更容易落到對的類型。
    if re.search(r"(中華|台哥大|遠傳|亞太|電信|公司|集團)", word):
        return "ORGANIZATION"
    if re.search(r"(台灣|臺灣|台北|臺北|高雄|台中|臺中)", word):
        return "LOCATION"
    if re.search(r"[0-9]+G|吃到飽|資費|方案", word):
        return "CONSUMER_TERM"
    return "KEYWORD"


def analyze_entities(text: str) -> list[EntityCount]:
    # counts 統計每個詞出現幾次；flags 保留對應詞性。
    counts: Counter[str] = Counter()
    flags: dict[str, str] = {}

    # 限制分析長度，避免超長文章拖慢斷詞速度。
    for word, flag in pseg.cut(text[:12000]):
        normalized = _normalize_token(word)
        # 太短、純數字或在 stopwords 內的詞直接略過。
        if len(normalized) < 2:
            continue
        if normalized.isdigit():
            continue
        if normalized.lower() in STOPWORDS:
            continue
        # 只保留我們想要的詞性。
        if not flag.startswith(ALLOWED_POS_PREFIXES):
            continue
        # 至少要有中英文字或數字，不收純符號。
        if not re.search(r"[\u4e00-\u9fffA-Za-z0-9]", normalized):
            continue

        counts[normalized] += 1
        flags[normalized] = flag

    # 依出現次數排序，並把結果轉成 EntityCount 物件。
    entities = []
    max_count = max(counts.values(), default=1)
    for word, mentions in counts.most_common(20):
        # salience 簡化成相對最高頻詞的比例。
        salience = round(mentions / max_count, 4) if max_count else 0
        entities.append(
            EntityCount(
                name=word,
                entity_type=_guess_entity_type(word, flags[word]),
                mentions=mentions,
                salience=salience,
            )
        )

    return entities
