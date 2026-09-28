from __future__ import annotations

import time
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from prism.index import PrismIndex
from prism.rails import screen_input, screen_output
from prism.synthesize import REFUSAL, synthesize
from prism.textutil import content_tokens, coverage
from prism.types import Hit, LensResult


class PrismState(TypedDict, total=False):
    question: str
    route: str
    documents: list
    graded: list
    retries: int
    expanded_query: str
    answer: str
    citations: list
    supported: bool
    trace: list
    metrics: dict


def classify(index: PrismIndex, question: str) -> str:
    folded = question.casefold()
    entities = index.entities_in_query(question)
    lexical = any(token in index.all_tokens for token in content_tokens(question))
    if not entities and not lexical:
        return "abstain"
    if any(word in folded for word in ("compare", "versus", "difference", "differ", "side by side")) or " vs " in f" {folded} ":
        return "comparative"
    if len(entities) >= 2 or "relationship" in folded or ("how does" in folded and "affect" in folded):
        return "multihop"
    return "factual"


def _hits_from_state(rows: list[dict]) -> list[Hit]:
    hits: list[Hit] = []
    for row in rows:
        hits.append(
            Hit(
                chunk_id=row["chunk_id"],
                doc_id=row["doc_id"],
                title=row["title"],
                archive=row["archive"],
                text=row["text"],
                score=row.get("score", 0.0),
                bm25=row.get("bm25", 0.0),
                dense=row.get("dense", 0.0),
                entities=list(row.get("entities") or []),
                relevant=bool(row.get("relevant", False)),
            )
        )
    return hits


def _trace(state: PrismState, node: str, detail: str) -> list[dict]:
    trace = list(state.get("trace") or [])
    trace.append({"node": node, "detail": detail})
    return trace


def build_aurora(index: PrismIndex):
    def input_guard(state: PrismState) -> dict:
        report = screen_input(state["question"])
        update = {"trace": _trace(state, "input_guard", report.detail)}
        if not report.passed:
            update.update(
                {
                    "route": "blocked",
                    "answer": report.message,
                    "citations": [],
                    "supported": False,
                    "documents": [],
                    "graded": [],
                }
            )
        return update

    def output_guard(state: PrismState) -> dict:
        chunks = list(state.get("graded") or state.get("documents") or [])
        report = screen_output(state.get("answer") or "", list(state.get("citations") or []), chunks)
        update = {
            "answer": report.text or state.get("answer") or "",
            "trace": _trace(state, "output_guard", report.detail),
        }
        if report.citations is not None:
            update["citations"] = report.citations
        if not report.passed:
            update["supported"] = False
            update["citations"] = []
        return update

    def router(state: PrismState) -> dict:
        route = classify(index, state["question"])
        return {"route": route, "retries": state.get("retries") or 0, "trace": _trace(state, "router", f"Classified the question as {route}.")}

    def planner(state: PrismState) -> dict:
        seeds = index.hybrid_search(state["question"], k=4)
        terms = index.expand_terms(state["question"], seeds, limit=4)
        expanded = state["question"] if not terms else f"{state['question']} {' '.join(terms)}"
        detail = "No extra entity names added." if not terms else "Added neighbor terms: " + ", ".join(terms)
        return {"expanded_query": expanded, "trace": _trace(state, "planner", detail)}

    def retrieve(state: PrismState) -> dict:
        query = state.get("expanded_query") or state["question"]
        route = state.get("route") or "factual"
        if route in {"comparative", "multihop"}:
            hits = index.search_balanced(query, k=6)
            kind = "entity-balanced"
        else:
            hits = index.hybrid_search(query, k=6)
            kind = "hybrid"
        rows = [hit.as_dict() for hit in hits]
        return {
            "documents": rows,
            "trace": _trace(state, "retrieve", f"{kind} retrieval kept {len(rows)} chunks."),
        }

    def grade(state: PrismState) -> dict:
        hits = index.grade(state["question"], _hits_from_state(state.get("documents") or []))
        rows = [hit.as_dict() for hit in hits]
        kept = sum(1 for hit in hits if hit.relevant)
        return {"graded": rows, "trace": _trace(state, "grade", f"{kept} of {len(rows)} chunks graded relevant.")}

    def rewrite(state: PrismState) -> dict:
        retries = int(state.get("retries") or 0) + 1
        seeds = _hits_from_state(state.get("graded") or [])
        terms = index.expand_terms(state["question"], seeds, limit=4)
        expanded = state["question"] if not terms else f"{state['question']} {' '.join(terms)}"
        detail = "Rewrote the query" + (f" with {', '.join(terms)}." if terms else " without new neighbor names.")
        return {"retries": retries, "expanded_query": expanded, "trace": _trace(state, "rewrite", detail + f" Retry {retries}.")}

    def synthesize_node(state: PrismState) -> dict:
        hits = _hits_from_state(state.get("graded") or [])
        answer, citations, supported = synthesize(state["question"], hits, state.get("route") or "factual")
        return {
            "answer": answer,
            "citations": citations,
            "supported": supported,
            "trace": _trace(state, "synthesize", f"Composed an answer with {len(citations)} citation(s)."),
        }

    def verify(state: PrismState) -> dict:
        missing = [item["chunk_id"] for item in state.get("citations") or [] if item["chunk_id"] not in index.chunk_ids]
        supported = bool(state.get("supported")) and not missing
        answer = state.get("answer") or ""
        if missing:
            answer = answer + " Citation check failed for " + ", ".join(missing) + "."
            detail = "Citation check failed."
        elif supported:
            detail = "Citations resolve to retrieved chunks."
        else:
            detail = "Answer is unsupported."
        return {"answer": answer, "supported": supported, "trace": _trace(state, "verify", detail)}

    def abstain(state: PrismState) -> dict:
        return {
            "answer": REFUSAL,
            "citations": [],
            "supported": False,
            "documents": [],
            "graded": [],
            "trace": _trace(state, "abstain", "The question has no foothold in the three archives."),
        }

    def after_input(state: PrismState) -> Literal["router", "end"]:
        if state.get("route") == "blocked":
            return "end"
        return "router"

    def after_router(state: PrismState) -> Literal["planner", "retrieve", "abstain"]:
        route = state.get("route")
        if route == "abstain":
            return "abstain"
        if route in {"comparative", "multihop"}:
            return "planner"
        return "retrieve"

    def after_grade(state: PrismState) -> Literal["rewrite", "synthesize"]:
        relevant = [row for row in state.get("graded") or [] if row.get("relevant")]
        retries = int(state.get("retries") or 0)
        if len(relevant) >= 2:
            return "synthesize"
        if len(relevant) == 1 and coverage(state["question"], relevant[0]["text"]) >= 0.5:
            return "synthesize"
        if retries < 2:
            return "rewrite"
        return "synthesize"

    graph = StateGraph(PrismState)
    graph.add_node("input_guard", input_guard)
    graph.add_node("router", router)
    graph.add_node("planner", planner)
    graph.add_node("retrieve", retrieve)
    graph.add_node("grade", grade)
    graph.add_node("rewrite", rewrite)
    graph.add_node("synthesize", synthesize_node)
    graph.add_node("verify", verify)
    graph.add_node("abstain", abstain)
    graph.add_node("output_guard", output_guard)
    graph.add_edge(START, "input_guard")
    graph.add_conditional_edges("input_guard", after_input, {"router": "router", "end": END})
    graph.add_conditional_edges("router", after_router, {"planner": "planner", "retrieve": "retrieve", "abstain": "abstain"})
    graph.add_edge("planner", "retrieve")
    graph.add_edge("retrieve", "grade")
    graph.add_conditional_edges("grade", after_grade, {"rewrite": "rewrite", "synthesize": "synthesize"})
    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("synthesize", "verify")
    graph.add_edge("verify", "output_guard")
    graph.add_edge("output_guard", END)
    graph.add_edge("abstain", END)
    return graph.compile()


def run_aurora(index: PrismIndex, question: str) -> LensResult:
    started = time.perf_counter()
    app = build_aurora(index)
    state = app.invoke(
        {
            "question": question,
            "route": "",
            "documents": [],
            "graded": [],
            "retries": 0,
            "expanded_query": "",
            "answer": "",
            "citations": [],
            "supported": False,
            "trace": [],
            "metrics": {},
        }
    )
    elapsed = (time.perf_counter() - started) * 1000
    graded = state.get("graded") or []
    relevant = sum(1 for row in graded if row.get("relevant"))
    retrieved = len(state.get("documents") or [])
    return LensResult(
        lens="aurora",
        question=question,
        route=state.get("route") or "",
        answer=state.get("answer") or "",
        citations=list(state.get("citations") or []),
        chunks=graded,
        trace=list(state.get("trace") or []),
        supported=bool(state.get("supported")),
        metrics={
            "retries": int(state.get("retries") or 0),
            "relevant": relevant,
            "retrieved": retrieved,
            "latency_ms": round(elapsed, 1),
            "context_precision": (relevant / retrieved) if retrieved else 0.0,
        },
    )
