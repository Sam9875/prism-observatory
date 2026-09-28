from __future__ import annotations

import time

from prism.graph import classify, run_aurora
from prism.index import PrismIndex
from prism.synthesize import synthesize
from prism.types import Hit, LensResult


def _result(lens: str, question: str, route: str, hits: list[Hit], trace: list[dict], started: float, retries: int = 0) -> LensResult:
    answer, citations, supported = synthesize(question, hits, route)
    relevant = sum(1 for hit in hits if hit.relevant)
    retrieved = len(hits)
    return LensResult(
        lens=lens,
        question=question,
        route=route,
        answer=answer,
        citations=citations,
        chunks=[hit.as_dict() for hit in hits],
        trace=trace,
        supported=supported,
        metrics={
            "retries": retries,
            "relevant": relevant,
            "retrieved": retrieved,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "context_precision": (relevant / retrieved) if retrieved else 0.0,
        },
    )


def run_glass(index: PrismIndex, question: str) -> LensResult:
    started = time.perf_counter()
    route = classify(index, question)
    if route == "abstain":
        hits: list[Hit] = []
        trace = [{"node": "glass", "detail": "No archive foothold, so Glass does not retrieve."}]
    else:
        hits = index.grade(question, index.hybrid_search(question, k=6))
        trace = [{"node": "glass", "detail": f"Hybrid retrieval graded {sum(h.relevant for h in hits)} chunks relevant."}]
    return _result("glass", question, route, hits, trace, started)


def run_crystal(index: PrismIndex, question: str) -> LensResult:
    started = time.perf_counter()
    route = classify(index, question)
    trace: list[dict] = []
    if route == "abstain":
        trace.append({"node": "crystal", "detail": "No archive foothold, so Crystal does not retrieve."})
        return _result("crystal", question, route, [], trace, started)
    first = index.search_balanced(question, k=6)
    terms = index.expand_terms(question, first, limit=4)
    trace.append({"node": "crystal", "detail": "Balanced hybrid search on the original question."})
    if terms:
        expanded = f"{question} {' '.join(terms)}"
        second = index.search_balanced(expanded, k=6)
        trace.append({"node": "crystal", "detail": "Expanded once with " + ", ".join(terms) + "."})
    else:
        second = []
        trace.append({"node": "crystal", "detail": "No neighbor terms to expand."})
    merged: dict[str, Hit] = {}
    for hit in first + second:
        current = merged.get(hit.chunk_id)
        if current is None or hit.score > current.score:
            merged[hit.chunk_id] = hit
    ordered = sorted(merged.values(), key=lambda hit: hit.score, reverse=True)[:6]
    graded = index.grade(question, ordered)
    trace.append({"node": "crystal", "detail": f"Merged to {len(graded)} unique chunks."})
    return _result("crystal", question, route, graded, trace, started)


def run_lens(index: PrismIndex, question: str, lens: str) -> LensResult:
    if lens == "glass":
        return run_glass(index, question)
    if lens == "crystal":
        return run_crystal(index, question)
    if lens == "aurora":
        return run_aurora(index, question)
    raise ValueError(f"Unknown lens: {lens}")
