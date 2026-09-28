---
id: entity-graph
title: The Entity Neighborhood
archive: neural
summary: Entities that share a document become neighbors, and rewrite uses those neighbors.
entities: entity graph; co-occurrence; GraphRAG; LightRAG
---

PRISM builds a small entity graph while it indexes. Two entities become neighbors when they are listed on the same source document. Eagle and Columbia share the Apollo document, so each can suggest the other. NIRCam and Sun-Earth L2 share the JWST document. The graph is co-occurrence, not a claim that one entity causes the other.

Query rewrite and Crystal's single expansion step use that neighborhood. They look at entities mentioned in the question or sitting on the passages already retrieved, then add a few neighboring names the question did not already contain. The added names give BM25 another exact token to hunt for. They do not invent a new corpus.

This is an original local implementation of a neighborhood idea that also shows up in Microsoft GraphRAG and in HKUDS LightRAG. PRISM does not import those projects, does not build their community summaries, and does not require a model to extract triples. The archive view lets you click an entity and see the other documents that share it, which is the same graph the rewrite node walks.
