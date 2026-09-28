from __future__ import annotations

import re

STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "what", "when",
    "where", "which", "how", "does", "did", "are", "was", "were", "have",
    "has", "its", "into", "about", "over", "than", "then", "them", "they",
    "their", "your", "not", "but", "you", "who", "why",
}

GENERIC_ENTITY_TOKENS = {
    "space", "telescope", "earth", "international", "station", "program",
    "archive", "graph", "search", "circulation", "summer", "island", "basin",
    "sheet", "system", "rover", "crater", "record", "orbit", "module",
    "atlantic", "meridional", "overturning",
}

_TOKEN = re.compile(r"[a-z0-9]+")
_SENTENCE = re.compile(r"(?<=[.!?])\s+")


def tokenize(text: str, min_len: int = 3) -> list[str]:
    return [
        token
        for token in _TOKEN.findall(text.lower())
        if len(token) >= min_len and token not in STOPWORDS
    ]


def content_tokens(text: str) -> list[str]:
    return tokenize(text, min_len=4)


def sentences(text: str) -> list[str]:
    parts = [part.strip() for part in _SENTENCE.split(text.strip()) if part.strip()]
    return parts or ([text.strip()] if text.strip() else [])


def entity_mentioned(name: str, query: str) -> bool:
    folded = name.casefold().strip()
    if len(folded) < 3:
        return False
    query_folded = query.casefold()
    if folded in query_folded:
        return True
    query_tokens = set(_TOKEN.findall(query_folded))
    for token in _TOKEN.findall(folded):
        if len(token) >= 4 and token not in GENERIC_ENTITY_TOKENS and token in query_tokens:
            return True
    return False


def coverage(query: str, text: str) -> float:
    terms = content_tokens(query)
    if not terms:
        return 0.0
    present = set(tokenize(text, min_len=3))
    return sum(1 for term in terms if term in present) / len(terms)
