from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class SourceDoc:
    id: str
    title: str
    archive: str
    summary: str
    entities: list[str]
    text: str
    path: str


@dataclass
class Chunk:
    id: str
    doc_id: str
    title: str
    archive: str
    entities: list[str]
    text: str
    index: int


@dataclass
class Hit:
    chunk_id: str
    doc_id: str
    title: str
    archive: str
    text: str
    score: float
    bm25: float
    dense: float
    entities: list[str]
    relevant: bool = False

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class LensResult:
    lens: str
    question: str
    route: str
    answer: str
    citations: list[dict] = field(default_factory=list)
    chunks: list[dict] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)
    supported: bool = False
    metrics: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)
