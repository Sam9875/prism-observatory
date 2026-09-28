---
id: guardrails
title: PRISM Guardrails
archive: neural
summary: Two Guardrails AI checks stop unsafe questions before retrieval and unsupported sentences after synthesis.
entities: Guardrails; input rail; output rail; InputSafety; GroundedOutput
---

PRISM puts two rails around every lens. They are Guardrails AI validators, registered as prism/input-safety and prism/grounded-output. Each one is attached to a Guard, and the guard's validate call is what decides. Aurora is a LangGraph, so the rails are real nodes: input_guard runs immediately after START, and output_guard runs after verify. Glass and Crystal call the same two guards even though they are not graphs.

The input rail runs before any retrieval. It blocks an empty question. It blocks a question longer than 400 characters. It blocks wording that tries to override the observatory, such as a request to discard earlier rules or to print a hidden prompt. It blocks personal data in the question: an email address, a phone number with separators, a long card-shaped number, or a three-two-four digit identifier. A blocked question returns a short refusal and an empty citation list. The archives are not searched.

The output rail runs after synthesis. It walks each cited sentence and keeps the sentence only when the same words appear in the passage named by that citation. A sentence that fails is removed, and the citation count is rewritten. If no cited sentence survives, the answer is replaced with a refusal from the output rail. A deliberate refusal, the one that says the archives do not contain grounded material, is allowed through. The rail does not invent a new fact to fill a gap.

The browser observatory applies the same decisions so the live page matches the Python package. The library call itself stays in Python, because that is where Guard.validate runs.
