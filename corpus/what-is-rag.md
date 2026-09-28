---
id: what-is-rag
title: Retrieval-Augmented Generation
archive: neural
summary: RAG retrieves passages first so the answer stays grounded instead of relying on memory alone.
entities: retrieval-augmented generation; grounding; hallucination
---

Retrieval-augmented generation, usually called RAG, answers a question in two movements. First it retrieves passages from a corpus you trust. Then it composes the answer from those passages. The point of the first movement is grounding. A claim should be traceable to a sentence the system actually fetched, which is why PRISM prints citation numbers beside the sentences it kept.

A model that answers only from memory can sound fluent and still invent a date, a name, or a citation. That failure is what people mean by hallucination in this setting: the words arrived without a retrieved source. RAG does not make invention impossible. It makes invention visible, because you can check the passage. If the passage is missing, the honest result is a refusal, not a guess.

PRISM's three archives are the only corpus the dashboard and the Python package read. Orbital covers flight, Neural covers the method itself, and Earth covers a handful of planetary systems. A question about a tournament score has no foothold there, so the router abstains. Grounding is a constraint, not a slogan.
