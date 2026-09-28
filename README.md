# PRISM Observatory

Three archives. Three lenses. Answers that cite the passage they came from.

PRISM is a retrieval-augmented generation workbench. It reads a local corpus, searches with a lexical index and a dense index, and answers only from the passages it kept. The long path, Aurora, is a real [LangGraph](https://github.com/langchain-ai/langgraph) state machine: guard the question, route, plan, retrieve, grade, rewrite, synthesize, verify, then guard the answer. [Guardrails AI](https://github.com/guardrails-ai/guardrails) runs those two checks in Python. The browser dashboard applies the same rails with no API key.

**Live dashboard:** https://topaz-ritual-z5y4.here.now/

**Repository:** https://github.com/Sam9875/prism-observatory

## What you can do on the dashboard

| View | What it shows |
| --- | --- |
| Ask | Run Glass, Crystal, Aurora, or all three. Read the cited answer, the chunks, and the node trace. |
| Lenses | How the short path, the expanded path, and the LangGraph path differ. |
| Graph | The Aurora state machine, including the input and output rails, lit with the nodes from the last run. |
| Rails | What the input rail blocks, and how the output rail checks citations. |
| Archives | Orbital, Neural, and Earth documents, plus the entity neighborhood. |
| Blueprint | Package map, why synthesis is extractive, and the projects that shaped the design. |
| Bench | Eight questions through all three lenses, with support, precision, and latency. |

Sample questions are on the Ask view. A football-score question is there on purpose: PRISM should refuse it.

## Lenses

- **Glass** — one hybrid retrieval, then an answer. No rewrite.
- **Crystal** — entity-balanced hybrid search, one neighborhood expansion, then an answer.
- **Aurora** — LangGraph. The grader can send a weak retrieval back through rewrite, at most twice, before synthesis and a citation check.

## Frameworks

LangChain supplies `Document`, `RecursiveCharacterTextSplitter`, the `Embeddings` interface, and `InMemoryVectorStore`. LangGraph supplies the Aurora `StateGraph`. Guardrails AI supplies the `Guard` that runs `prism/input-safety` before retrieval and `prism/grounded-output` after the answer is written. BM25 is Okapi via `rank_bm25`. The two ranked lists meet by reciprocal rank fusion. A small co-occurrence graph adds neighboring entity names when a query is thin.

The input rail blocks an empty question, a question longer than 400 characters, an attempt to override the instructions, and personal data such as an email, phone number, or card number. The output rail keeps a cited sentence only when that sentence appears in the passage it cites.

There is no hosted chat model. The synthesizer picks sentences from graded chunks and numbers them. That is a deliberate choice: the live dashboard and the Python package stay in lockstep, and both run without a key. Swap in a chat model later behind `synthesize` if you want abstractive wording; keep the grader and the citation check in front of it.

## Inspiration

The design borrows patterns, not code, from public RAG systems:

- [LangChain](https://github.com/langchain-ai/langchain) retrieval components and text splitting
- The [LangGraph corrective RAG](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_crag/) grade-and-rewrite loop
- Hybrid lexical plus dense search, as practiced in the [Haystack](https://github.com/deepset-ai/haystack) ecosystem
- Entity-neighborhood retrieval, the idea behind [GraphRAG](https://github.com/microsoft/graphrag) and [LightRAG](https://github.com/HKUDS/LightRAG)
- Support and context-precision proxies in the spirit of [RAGAS](https://github.com/explodinggradients/ragas)

## Layout

```
corpus/            source documents the indexes read
src/prism/         loader, splitter, embeddings, fusion, lenses, LangGraph
dashboard/         static observatory (index, styles, engine, archive)
tests/             fixture corpus and engine tests
scripts/           archive export
```

## Run it locally

```bash
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m prism.cli ask "Where did Eagle land, and who stayed in lunar orbit?"
.venv\Scripts\python -m prism.cli ask "Compare the orbits of Hubble and JWST." --lens aurora
.venv\Scripts\python -m prism.cli bench
```

On macOS or Linux, use `.venv/bin/python` instead.

Export the browser archive after editing the corpus:

```bash
.venv\Scripts\python -m prism.cli export
```

That rewrites `dashboard/archive.json` with the LangChain chunks.

## Archives

- **Orbital** — Apollo 11, Voyager, JWST, Hubble, the ISS, Artemis, Mars rovers, orbits
- **Neural** — how this project chunks, fuses, grades, rewrites, and cites
- **Earth** — AMOC, coral bleaching, the Amazon, Antarctic ice, monsoons, urban heat

## License

MIT. See [LICENSE](LICENSE).
