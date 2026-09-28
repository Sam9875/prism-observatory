---
id: hybrid-search
title: Hybrid Retrieval
archive: neural
summary: PRISM fuses BM25 with TF-IDF cosine using reciprocal rank fusion.
entities: BM25; TF-IDF; reciprocal rank fusion; InMemoryVectorStore
---

PRISM keeps two indexes over the same chunks. The lexical index is BM25, Okapi scoring from the rank_bm25 library. BM25 rewards words that are rare in the corpus and frequent in the chunk, which is how a proper name such as NIRCam, Tranquility, or Ingenuity surfaces even when the rest of the question is ordinary. The dense index is a LangChain Embeddings implementation fit with TF-IDF over those chunks and stored in LangChain's InMemoryVectorStore. Cosine similarity on L2-normalized vectors finds passages that share a pattern of terms even when the ranking of exact rare words would have buried them.

The two ranked lists are not averaged in raw score. BM25 scores and cosine scores do not live on the same scale. PRISM fuses them with reciprocal rank fusion. A chunk at rank r contributes 1/(60+r), and a chunk that appears on both lists adds both contributions. The constant 60 keeps a single first-place hit from drowning out a chunk that both methods liked.

Crystal and Aurora also balance a comparison. If the question names two entities that live in different documents, retrieval must bring back at least one chunk from each document when such a chunk exists. A comparison of Hubble and JWST that only quotes Hubble is a failed comparison, however high the score.
