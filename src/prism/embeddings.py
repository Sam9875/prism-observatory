from __future__ import annotations

import math
from collections import Counter

from langchain_core.embeddings import Embeddings

from prism.textutil import tokenize


class TfidfEmbeddings(Embeddings):
    """Fit-once TF-IDF vectors for LangChain's in-memory store."""

    def __init__(self) -> None:
        self.vocab: dict[str, int] = {}
        self.idf: list[float] = []
        self._fitted = False

    def fit(self, texts: list[str]) -> None:
        tokenized = [tokenize(text) for text in texts]
        document_frequency: Counter[str] = Counter()
        for tokens in tokenized:
            document_frequency.update(set(tokens))
        terms = sorted(document_frequency)
        count = max(len(tokenized), 1)
        self.vocab = {term: index for index, term in enumerate(terms)}
        self.idf = [
            math.log((1 + count) / (1 + document_frequency[term])) + 1.0 for term in terms
        ]
        self._fitted = True

    def _vector(self, text: str) -> list[float]:
        if not self._fitted:
            raise RuntimeError("TfidfEmbeddings.fit() must run before embedding")
        width = max(len(self.vocab), 1)
        vector = [0.0] * width
        if not self.vocab:
            return vector
        counts = Counter(tokenize(text))
        total = sum(counts.values()) or 1
        for term, seen in counts.items():
            index = self.vocab.get(term)
            if index is None:
                continue
            vector[index] = (seen / total) * self.idf[index]
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)
