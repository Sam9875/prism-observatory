---
id: corrective-rag
title: Corrective Retrieval
archive: neural
summary: The grader can send a weak retrieval to rewrite, and the rewrite may run at most twice.
entities: corrective RAG; document grader; query rewrite
---

Corrective retrieval is the idea that a bad first search should not be the last search. PRISM takes that pattern from the corrective RAG loop taught with LangGraph. After retrieve, a document grader marks each chunk relevant or not. A chunk is relevant when it shares at least two content words with the question, when it carries an entity the question named, or when a content word from its title appears in the question.

The grade is sufficient when two or more chunks are relevant, or when one relevant chunk covers at least half of the question's content words. If the grade is weak and fewer than two rewrites have already run, the rewrite node appends neighboring entity names from the co-occurrence graph and retrieve runs again. The retry counter stops at two. A third loop would wander.

Rewrite does not call a chat model. It adds names that share a source document with something the question already touched, and it refuses names that are already in the question. If the archive still has nothing relevant, synthesize refuses instead of padding an answer. That refusal is the corrective path's last honest move.
