from __future__ import annotations

import argparse
import sys
from pathlib import Path

from prism.corpus import load_corpus
from prism.export import export_archive
from prism.index import PrismIndex
from prism.lenses import run_lens

BENCH = [
    "Where did Eagle land, and who stayed in lunar orbit?",
    "Which instruments fly on the James Webb Space Telescope?",
    "Compare the orbits of Hubble and JWST.",
    "How does Aurora decide to rewrite a query?",
    "What is the AMOC, and why is a slowdown discussed?",
    "What did Ingenuity prove on Mars?",
    "How does PRISM fuse BM25 with dense retrieval?",
    "Why do coral reefs bleach?",
    "Who won the 2014 football world cup final?",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_corpus() -> Path:
    return repo_root() / "corpus"


def build_index(corpus: Path) -> PrismIndex:
    return PrismIndex(load_corpus(corpus))


def command_ask(args: argparse.Namespace) -> int:
    index = build_index(Path(args.corpus))
    result = run_lens(index, args.question, args.lens)
    print(f"lens: {result.lens}")
    print(f"route: {result.route}")
    print(f"supported: {result.supported}")
    print()
    print(result.answer)
    print()
    print("trace: " + " → ".join(step["node"] for step in result.trace))
    return 0


def command_bench(args: argparse.Namespace) -> int:
    index = build_index(Path(args.corpus))
    print(f"{'lens':<8} {'route':<14} {'ok':<5} {'rel':<4} answer")
    for question in BENCH:
        for lens in ("glass", "crystal", "aurora"):
            result = run_lens(index, question, lens)
            preview = " ".join(result.answer.split())[:72]
            flag = "yes" if result.supported else "no"
            print(f"{lens:<8} {result.route:<14} {flag:<5} {result.metrics['relevant']:<4} {preview}")
        print(f"Q: {question}")
        print()
    return 0


def command_export(args: argparse.Namespace) -> int:
    root = repo_root()
    destinations = [root / "data" / "archive.json", root / "dashboard" / "archive.json"]
    payload = export_archive(Path(args.corpus), destinations)
    print(f"Exported {len(payload['documents'])} documents and {len(payload['chunks'])} chunks.")
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="prism", description="Query the PRISM archives.")
    parser.add_argument("--corpus", default=str(default_corpus()))
    sub = parser.add_subparsers(dest="command", required=True)

    ask = sub.add_parser("ask")
    ask.add_argument("question")
    ask.add_argument("--lens", choices=("glass", "crystal", "aurora"), default="aurora")
    ask.set_defaults(func=command_ask)

    bench = sub.add_parser("bench")
    bench.set_defaults(func=command_bench)

    export = sub.add_parser("export")
    export.set_defaults(func=command_export)

    args = parser.parse_args(argv)
    try:
        code = args.func(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        code = 1
    raise SystemExit(code)
