---
id: evaluation
title: How a Run Is Judged
archive: neural
summary: PRISM reports a support flag, context precision, citation coverage, and latency.
entities: context precision; faithfulness; support flag
---

PRISM reports a few numbers on every run, as proxies in the spirit of RAGAS rather than as the RAGAS library itself. Context precision is the fraction of retrieved chunks the grader kept. A run that fetches six chunks and keeps one is less precise than a run that fetches four and keeps three, even if both eventually answer.

The support flag is stricter than a fluent paragraph. It is true only when the answer cites at least one passage that survived grading, and Aurora's verify node also checks that every citation chunk id exists in the index. Citation coverage counts the distinct documents those citations came from. A comparison that cites only one document can be supported and still be incomplete, which is why the balanced retriever exists.

Latency is the wall time around the lens call, reported in milliseconds. The Bench view runs a fixed set of questions through Glass, Crystal, and Aurora and shows route, support, precision, and latency side by side. One question in that set sits outside every archive on purpose. A grounded system should refuse it.
