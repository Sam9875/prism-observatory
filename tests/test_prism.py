from pathlib import Path

import pytest

from prism.export import export_archive
from prism.graph import build_aurora
from prism.index import PrismIndex
from prism.lenses import run_lens

FIXTURE = Path(__file__).parent / "fixtures" / "corpus"
ROOT = Path(__file__).resolve().parents[1]


def index() -> PrismIndex:
    from prism.corpus import load_corpus

    return PrismIndex(load_corpus(FIXTURE))


def test_apollo_like_retrieval():
    result = run_lens(index(), "Where did Eagle land and who stayed in Columbia?", "glass")
    assert "Tranquility" in result.answer
    assert "Collins" in result.answer
    assert result.supported


def test_jwst_instruments():
    result = run_lens(index(), "Which instruments fly on the James Webb Space Telescope?", "aurora")
    assert "NIRCam" in result.answer
    assert "MIRI" in result.answer


def test_comparative_route():
    result = run_lens(index(), "Compare Eagle and JWST", "aurora")
    assert result.route == "comparative"
    names = [step["node"] for step in result.trace]
    assert "router" in names
    assert "verify" in names or "abstain" in names


def test_rewrite_trace_or_grade():
    result = run_lens(index(), "How does Aurora decide to rewrite a query?", "aurora")
    assert "router" in [step["node"] for step in result.trace]
    lowered = result.answer.casefold()
    assert "rewrite" in lowered or "grade" in lowered


def test_abstain():
    result = run_lens(index(), "Who won the 2014 football world cup final?", "aurora")
    assert result.supported is False
    assert "does not have grounded" in result.answer


def test_citations_resolve():
    built = index()
    result = run_lens(built, "Where did Eagle land and who stayed in Columbia?", "aurora")
    assert result.citations
    for citation in result.citations:
        assert citation["chunk_id"] in built.chunk_ids


def test_graph_is_langgraph():
    compiled = build_aurora(index())
    assert hasattr(compiled, "invoke")
    drawn = compiled.get_graph()
    names = set(drawn.nodes)
    for required in ("router", "retrieve", "grade", "rewrite", "synthesize", "verify", "abstain"):
        assert required in names


def test_export_archive(tmp_path: Path):
    destination = tmp_path / "archive.json"
    payload = export_archive(FIXTURE, [destination])
    assert destination.exists()
    assert len(payload["documents"]) >= 4
    assert payload["chunks"]


@pytest.mark.skipif(len(list((ROOT / "corpus").glob("*.md"))) < 10, reason="full corpus not written yet")
def test_full_corpus_jwst_and_amoc():
    from prism.corpus import load_corpus

    built = PrismIndex(load_corpus(ROOT / "corpus"))
    webb = run_lens(built, "Which instruments fly on the James Webb Space Telescope?", "glass")
    amoc = run_lens(built, "What is the AMOC, and why is a slowdown discussed?", "aurora")
    assert "NIRCam" in webb.answer or "MIRI" in webb.answer
    assert "Atlantic" in amoc.answer
