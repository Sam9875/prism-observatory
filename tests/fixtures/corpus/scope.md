---
id: scope
title: Aurora Rewrite Rule
archive: neural
summary: Aurora sends weak retrieval from the grade node to rewrite, then retrieves again.
entities: Aurora; LangGraph; rewrite
---

Aurora is a LangGraph state machine used by PRISM. The grade node inspects retrieved passages and sends weak retrieval to rewrite. Rewrite appends neighbor entities that were not already in the question, and retrieve runs again on the expanded wording. Retries stop at two so the loop cannot continue forever. After that, synthesize writes an answer only from passages the grader kept.
