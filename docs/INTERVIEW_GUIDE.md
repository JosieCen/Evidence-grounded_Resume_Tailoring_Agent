# Interview Guide

## 30-second project pitch

I built an evidence-grounded resume tailoring agent to solve a common LLM failure mode: making an application sound more relevant without inventing experience. I store candidate experience as verified claims with provenance, let the agent map JD requirements to those claims, and keep unsupported requirements as explicit gaps. Before finalizing, deterministic guardrails check sources, visibility, forbidden claims and numerical provenance; unsafe bullets are removed and re-audited. The public demo is fully fictional and reproducible.

## Why is this an agent rather than a pipeline?

It has an explicit controller state and a conditional loop. The system chooses evidence based on the current JD, creates a draft, observes validation results, and changes its next action: finalize on pass or revise and re-audit on failure. The tools themselves remain modular and deterministic where appropriate.

## Why not use one large prompt?

A single prompt mixes semantic interpretation, writing and factual authorization. That makes failures difficult to audit. I separated those responsibilities so the reasoning layer can evolve independently while the evidence contract remains stable.

## What would you replace with an LLM?

The requirement parser, semantic retriever and controlled paraphraser are good candidates. I would not delegate final factual authorization solely to the LLM; the deterministic audit should remain.

## How do you evaluate it?

v0.1 has a synthetic guardrail suite and E2E tests. The next step is a labeled requirement-to-claim benchmark measuring semantic precision/recall, while continuing to track unsupported-claim and traceability rates.

## What is the biggest limitation?

The current semantic matcher is lexical and synonym-based. It is transparent and sufficient to demonstrate the architecture, but it will miss nuanced transferable experience and can over-match broad terms. That is intentionally the next iteration target.

## What did you personally design?

A strong answer should focus on the decisions rather than only implementation: the source-of-truth model, claim-level provenance, gap preservation, deterministic safety boundary, revision loop, evaluation design and privacy-safe public/demo separation.
