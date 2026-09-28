from __future__ import annotations

from langchain_core.vectorstores import InMemoryVectorStore
from rank_bm25 import BM25Okapi

from prism.chunking import split_docs
from prism.textutil import content_tokens, entity_mentioned, tokenize
from prism.types import Hit, SourceDoc

RRF_K = 60


class PrismIndex:
    def __init__(self, docs: list[SourceDoc]) -> None:
        self.docs = docs
        self.documents = split_docs(docs)
        if not self.documents:
            raise ValueError("Corpus produced no chunks")
        self.chunks = self.documents
        tokenized = []
        for document in self.documents:
            tokens = tokenize(document.page_content, min_len=2)
            tokenized.append(tokens or ["empty"])
        self._bm25_tokens = tokenized
        self.bm25 = BM25Okapi(tokenized)
        self.all_tokens: set[str] = set()
        for tokens in tokenized:
            self.all_tokens.update(token for token in tokens if len(token) > 3)

        from prism.embeddings import TfidfEmbeddings

        self.embeddings = TfidfEmbeddings()
        self.embeddings.fit([document.page_content for document in self.documents])
        self.vectorstore = InMemoryVectorStore(embedding=self.embeddings)
        self.vectorstore.add_documents(self.documents)

        self.entity_names: dict[str, str] = {}
        self.entity_graph: dict[str, set[str]] = {}
        self.entity_docs: dict[str, set[str]] = {}
        for doc in docs:
            keys: list[str] = []
            for name in doc.entities:
                key = name.casefold().strip()
                if len(key) < 3:
                    continue
                self.entity_names.setdefault(key, name)
                keys.append(key)
                self.entity_docs.setdefault(key, set()).add(doc.id)
                self.entity_graph.setdefault(key, set())
            for left in keys:
                for right in keys:
                    if left != right:
                        self.entity_graph[left].add(right)

        self.chunk_ids = {document.metadata["chunk_id"] for document in self.documents}

    def entities_in_query(self, query: str) -> list[str]:
        found: list[str] = []
        seen: set[str] = set()
        for key, name in self.entity_names.items():
            if key in seen:
                continue
            if entity_mentioned(name, query):
                found.append(name)
                seen.add(key)
        return found

    def _hit_from(self, document, score: float, bm25: float, dense: float) -> Hit:
        meta = document.metadata
        return Hit(
            chunk_id=meta["chunk_id"],
            doc_id=meta["doc_id"],
            title=meta["title"],
            archive=meta["archive"],
            text=document.metadata.get("passage") or document.page_content,
            score=score,
            bm25=bm25,
            dense=dense,
            entities=list(meta.get("entities") or []),
        )

    def hybrid_search(self, query: str, k: int = 6) -> list[Hit]:
        bm25_scores = list(self.bm25.get_scores(tokenize(query, min_len=2)))
        lexical_order = sorted(
            range(len(bm25_scores)),
            key=lambda index: bm25_scores[index],
            reverse=True,
        )
        lexical_ranked = [index for index in lexical_order if bm25_scores[index] > 0][:12]

        dense_docs = self.vectorstore.similarity_search(query, k=12)
        dense_ids = [document.metadata["chunk_id"] for document in dense_docs]
        by_id = {document.metadata["chunk_id"]: document for document in self.documents}

        fused: dict[str, dict] = {}
        for rank, index in enumerate(lexical_ranked, start=1):
            document = self.documents[index]
            chunk_id = document.metadata["chunk_id"]
            fused.setdefault(chunk_id, {"bm25": 0.0, "dense": 0.0, "score": 0.0})
            contribution = 1.0 / (RRF_K + rank)
            fused[chunk_id]["bm25"] = contribution
            fused[chunk_id]["score"] += contribution
        for rank, chunk_id in enumerate(dense_ids, start=1):
            fused.setdefault(chunk_id, {"bm25": 0.0, "dense": 0.0, "score": 0.0})
            contribution = 1.0 / (RRF_K + rank)
            fused[chunk_id]["dense"] = contribution
            fused[chunk_id]["score"] += contribution

        ordered = sorted(fused.items(), key=lambda item: item[1]["score"], reverse=True)[:k]
        return [
            self._hit_from(by_id[chunk_id], payload["score"], payload["bm25"], payload["dense"])
            for chunk_id, payload in ordered
            if chunk_id in by_id
        ]

    def search_balanced(self, query: str, k: int = 6) -> list[Hit]:
        hits = self.hybrid_search(query, k=k)
        implied: dict[str, str] = {}
        for name in self.entities_in_query(query):
            for doc_id in self.entity_docs.get(name.casefold(), ()):
                implied.setdefault(doc_id, name)
        if len(implied) < 2:
            return hits
        merged = {hit.chunk_id: hit for hit in hits}
        for doc_id, name in implied.items():
            if any(hit.doc_id == doc_id for hit in merged.values()):
                continue
            for extra in self.hybrid_search(name, k=2):
                if extra.doc_id == doc_id:
                    merged[extra.chunk_id] = extra
                    break
        ordered = sorted(merged.values(), key=lambda hit: hit.score, reverse=True)
        limit = max(k, len(implied))
        return ordered[:limit]

    def expand_terms(self, query: str, seed_hits: list[Hit], limit: int = 4) -> list[str]:
        query_folded = query.casefold()
        seeds: set[str] = set()
        for name in self.entities_in_query(query):
            seeds.add(name.casefold())
        for hit in seed_hits:
            for name in hit.entities:
                if entity_mentioned(name, query) or name.casefold() in query_folded:
                    seeds.add(name.casefold())
            for key in self.entity_names:
                if key in hit.text.casefold():
                    seeds.add(key)
        neighbors: list[str] = []
        seen: set[str] = set()
        for seed in seeds:
            for neighbor in sorted(self.entity_graph.get(seed, ())):
                display = self.entity_names.get(neighbor, neighbor)
                if neighbor in seen or neighbor in query_folded or display.casefold() in query_folded:
                    continue
                neighbors.append(display)
                seen.add(neighbor)
                if len(neighbors) >= limit:
                    return neighbors
        return neighbors

    def grade(self, query: str, hits: list[Hit]) -> list[Hit]:
        query_terms = set(content_tokens(query))
        graded: list[Hit] = []
        for hit in hits:
            shared = query_terms.intersection(content_tokens(hit.text))
            entity_hit = any(entity_mentioned(name, query) for name in hit.entities)
            title_hit = bool(set(content_tokens(hit.title)).intersection(query_terms))
            relevant = len(shared) >= 2 or entity_hit or title_hit
            graded.append(
                Hit(
                    chunk_id=hit.chunk_id,
                    doc_id=hit.doc_id,
                    title=hit.title,
                    archive=hit.archive,
                    text=hit.text,
                    score=hit.score,
                    bm25=hit.bm25,
                    dense=hit.dense,
                    entities=list(hit.entities),
                    relevant=relevant,
                )
            )
        return graded
