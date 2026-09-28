from __future__ import annotations

from prism.textutil import content_tokens, entity_mentioned, sentences
from prism.types import Hit

REFUSAL = (
    "PRISM does not have grounded material for that in the Orbital, Neural, or Earth archives."
)


def synthesize(question: str, hits: list[Hit], route: str) -> tuple[str, list[dict], bool]:
    relevant = [hit for hit in hits if hit.relevant]
    if not relevant:
        return REFUSAL, [], False

    matched_docs = {
        hit.doc_id
        for hit in relevant
        if any(entity_mentioned(name, question) for name in hit.entities)
    }
    candidates: list[tuple[float, int, int, str, Hit]] = []
    for hit_index, hit in enumerate(relevant):
        for sentence_index, sentence in enumerate(sentences(hit.text)):
            if len(sentence) < 40 or sentence[:1].islower():
                continue
            overlap = len(set(content_tokens(question)).intersection(content_tokens(sentence)))
            bonus = 0
            if hit.doc_id in matched_docs:
                bonus = sum(
                    3
                    for name in hit.entities
                    if len(name) >= 4 and name.casefold() in sentence.casefold()
                )
            candidates.append((float(overlap + bonus), hit_index, sentence_index, sentence, hit))

    if not candidates:
        fallback = relevant[0]
        quote = fallback.text.strip()
        answer = f"{quote} [1]\n\nGrounded in 1 passage."
        citation = {
            "n": 1,
            "chunk_id": fallback.chunk_id,
            "doc_id": fallback.doc_id,
            "title": fallback.title,
            "archive": fallback.archive,
            "quote": quote[:180],
        }
        return answer, [citation], True

    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
    selected: list[tuple[int, int, str, Hit]] = []
    covered: set[str] = set()
    seen_sentences: set[str] = set()
    for score, hit_index, sentence_index, sentence, hit in candidates:
        key = " ".join(sentence.casefold().split())
        if key in seen_sentences:
            continue
        tokens = set(content_tokens(sentence))
        if selected and tokens:
            overlap_ratio = len(tokens & covered) / len(tokens)
            if overlap_ratio > 0.7 and len(selected) >= 2:
                continue
        selected.append((hit_index, sentence_index, sentence, hit))
        seen_sentences.add(key)
        covered.update(tokens)
        if len(selected) >= 5:
            break

    selected.sort(key=lambda item: (item[0], item[1]))
    numbers: dict[str, int] = {}
    citations: list[dict] = []
    rendered: list[str] = []
    for _, _, sentence, hit in selected:
        if hit.chunk_id not in numbers:
            numbers[hit.chunk_id] = len(numbers) + 1
            citations.append(
                {
                    "n": numbers[hit.chunk_id],
                    "chunk_id": hit.chunk_id,
                    "doc_id": hit.doc_id,
                    "title": hit.title,
                    "archive": hit.archive,
                    "quote": hit.text[:180],
                }
            )
        rendered.append(f"{sentence} [{numbers[hit.chunk_id]}]")

    prefix = "Set side by side, the archives say this. " if route == "comparative" else ""
    answer = prefix + " ".join(rendered) + f"\n\nGrounded in {len(citations)} passage(s)."
    return answer, citations, True
