---
id: langgraph-aurora
title: The Aurora Graph
archive: neural
summary: Aurora is a LangGraph StateGraph that routes, grades, rewrites, synthesizes, and verifies.
entities: LangGraph; Aurora; StateGraph
---

Aurora is the long lens, and it is a real LangGraph StateGraph, not a sketch of one. The nodes are router, planner, retrieve, grade, rewrite, synthesize, verify, and abstain. START enters the router. The router sends a comparative or multi-hop question to the planner, a factual question straight to retrieve, and a question with no foothold in the archives to abstain.

The planner may append neighbor entities, then always goes to retrieve. Retrieve goes to grade. Grade either loops to rewrite or continues to synthesize. Rewrite returns to retrieve, and it may do so only until the retry count hits two. Synthesize goes to verify, and verify ends the graph. Abstain also ends the graph, with the refusal sentence and an empty citation list.

State carries the question, the route, the documents, the grade, the retry count, the answer, the citations, the support flag, and a trace. Every node appends a trace entry so the dashboard can light the nodes that actually ran. Glass and Crystal are not this graph. Glass is one hybrid retrieval plus synthesis. Crystal adds entity-balanced retrieval and one expansion, then stops. Only Aurora loops.
