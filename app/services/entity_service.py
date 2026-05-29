import math
import re
from collections import Counter

import jieba.posseg as pseg

from app.models import EntityCount


ALLOWED_POS_PREFIXES = ("n", "nr", "ns", "nt", "nz", "eng")
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
    token = token.strip()
    token = re.sub(r"\s+", "", token)
    return token


def _guess_entity_type(word: str, flag: str) -> str:
    if flag.startswith("nr"):
        return "PERSON"
    if flag.startswith("ns"):
        return "LOCATION"
    if flag.startswith("nt"):
        return "ORGANIZATION"
    if re.search(r"(中華|台哥大|遠傳|亞太|電信|公司|集團)", word):
        return "ORGANIZATION"
    if re.search(r"(台灣|臺灣|台北|臺北|高雄|台中|臺中)", word):
        return "LOCATION"
    if re.search(r"[0-9]+G|吃到飽|資費|方案", word):
        return "CONSUMER_TERM"
    return "KEYWORD"


def analyze_entities(text: str) -> list[EntityCount]:
    counts: Counter[str] = Counter()
    flags: dict[str, str] = {}

    for word, flag in pseg.cut(text[:12000]):
        normalized = _normalize_token(word)
        if len(normalized) < 2:
            continue
        if normalized.isdigit():
            continue
        if normalized.lower() in STOPWORDS:
            continue
        if not flag.startswith(ALLOWED_POS_PREFIXES):
            continue
        if not re.search(r"[\u4e00-\u9fffA-Za-z0-9]", normalized):
            continue

        counts[normalized] += 1
        flags[normalized] = flag

    entities = []
    max_count = max(counts.values(), default=1)
    for word, mentions in counts.most_common(20):
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
