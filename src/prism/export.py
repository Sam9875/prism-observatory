from __future__ import annotations

import json
from pathlib import Path

from prism.corpus import load_corpus
from prism.index import PrismIndex

KICKERS = {"orbital": "Flight", "neural": "Method", "earth": "Planet"}


def export_archive(corpus_root: Path, destinations: list[Path]) -> dict:
    docs = load_corpus(corpus_root)
    index = PrismIndex(docs)
    archives = []
    seen: set[str] = set()
    for doc in docs:
        if doc.archive in seen:
            continue
        seen.add(doc.archive)
        archives.append(
            {
                "id": doc.archive,
                "title": {
                    "orbital": "Orbital Archive",
                    "neural": "Neural Archive",
                    "earth": "Earth Archive",
                }.get(doc.archive, doc.archive.title()),
                "kicker": KICKERS.get(doc.archive, "Archive"),
                "blurb": doc.summary,
            }
        )
    payload = {
        "project": "PRISM Observatory",
        "version": "1.0.0",
        "tagline": "Three archives, three lenses, answers that cite the passage they came from.",
        "archives": archives,
        "documents": [
            {
                "id": doc.id,
                "title": doc.title,
                "archive": doc.archive,
                "summary": doc.summary,
                "entities": doc.entities,
                "text": doc.text,
            }
            for doc in docs
        ],
        "chunks": [
            {
                "id": document.metadata["chunk_id"],
                "doc_id": document.metadata["doc_id"],
                "title": document.metadata["title"],
                "archive": document.metadata["archive"],
                "entities": document.metadata["entities"],
                "text": document.metadata.get("passage") or document.page_content,
                "index": document.metadata["index"],
            }
            for document in index.documents
        ],
    }
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    for destination in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(encoded + "\n", encoding="utf-8")
    return payload
