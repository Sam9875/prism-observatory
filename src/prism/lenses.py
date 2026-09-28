from __future__ import annotations

import time

from prism.graph import classify, run_aurora
from prism.index import PrismIndex
from prism.rails import screen_input, screen_output
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


def _blocked(lens: str, question: str, detail: str, message: str, started: float) -> LensResult:
    return LensResult(
        lens=lens,
        question=question,
        route="blocked",
        answer=message,
        citations=[],
        chunks=[],
        trace=[{"node": "input_guard", "detail": detail}],
        supported=False,
        metrics={
            "retries": 0,
            "relevant": 0,
            "retrieved": 0,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "context_precision": 0.0,
            "input_rail": "blocked",
            "output_rail": "skipped",
        },
    )


def _apply_output(result: LensResult, hits: list[Hit], input_detail: str) -> LensResult:
    result.trace = [{"node": "input_guard", "detail": input_detail}, *result.trace]
    report = screen_output(result.answer, result.citations, [hit.as_dict() for hit in hits])
    result.trace.append({"node": "output_guard", "detail": report.detail})
    result.metrics["input_rail"] = "clear"
    result.metrics["output_rail"] = report.rail
    if not report.passed:
        result.answer = report.message
        result.supported = False
        result.citations = []
    elif report.repaired:
        result.answer = report.text
        result.citations = list(report.citations or [])
    return result


def run_glass(index: PrismIndex, question: str) -> LensResult:
    started = time.perf_counter()
    incoming = screen_input(question)
    if not incoming.passed:
        return _blocked("glass", question, incoming.detail, incoming.message, started)
    route = classify(index, question)
    if route == "abstain":
        hits: list[Hit] = []
        trace = [{"node": "glass", "detail": "No archive foothold, so Glass does not retrieve."}]
    else:
        hits = index.grade(question, index.hybrid_search(question, k=6))
        trace = [{"node": "glass", "detail": f"Hybrid retrieval graded {sum(h.relevant for h in hits)} chunks relevant."}]
    return _apply_output(_result("glass", question, route, hits, trace, started), hits, incoming.detail)


def run_crystal(index: PrismIndex, question: str) -> LensResult:
    started = time.perf_counter()
    incoming = screen_input(question)
    if not incoming.passed:
        return _blocked("crystal", question, incoming.detail, incoming.message, started)
    route = classify(index, question)
    trace: list[dict] = []
    if route == "abstain":
        trace.append({"node": "crystal", "detail": "No archive foothold, so Crystal does not retrieve."})
        return _apply_output(_result("crystal", question, route, [], trace, started), [], incoming.detail)
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
    return _apply_output(_result("crystal", question, route, graded, trace, started), graded, incoming.detail)


def run_lens(index: PrismIndex, question: str, lens: str) -> LensResult:
    if lens == "glass":
        return run_glass(index, question)
    if lens == "crystal":
        return run_crystal(index, question)
    if lens == "aurora":
        return run_aurora(index, question)
    raise ValueError(f"Unknown lens: {lens}")
