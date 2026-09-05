# v0.3 Implementation Plan

## Goal

Turn the public prototype from a retrieval-and-filtering demo into a credible evidence-grounded resume tailoring workflow while keeping the repository small enough to understand in an interview.

## Acceptance criteria

1. Tailoring changes wording without creating unsupported factual propositions.
2. Revision rewrites a sourced unsafe draft from authorized evidence instead of only deleting it.
3. JD requirements have stable IDs and basic requirement type/priority.
4. A baseline resume can be compared with the tailored application output.
5. Evidence references resolve against a structured public evidence registry.
6. Numeric checks work across multiple source claims.
7. Known unsupported scope remains an explicit gap before similarity ranking.
8. The labeled retrieval benchmark contains at least 60 cases and reports category-level metrics.
9. English/Chinese matching is represented in the public fixture.
10. Lightweight CI remains dependency-light; real embedding evaluation runs separately.

## Work packages

1. Structured JD layer: classify responsibilities, must-haves, nice-to-haves; use content-stable IDs.
2. Evidence model: add evidence registry and claim-owned authorized paraphrases.
3. Controlled drafting/revision: preserve provenance and repair unsafe sourced bullets from evidence.
4. Baseline-aware workflow: emit a before/after change log.
5. Retrieval/safety: multilingual model, weighted lexical matching, unsupported-scope gate, multi-source metric ownership.
6. Evaluation: expand 6 → 72 cases with semantic, bilingual, numeric, overclaim, gap, and seniority categories.
7. Product surface: update Streamlit, docs, CI, and public demos.

## Deliberately out of scope

Multi-agent orchestration, vector databases for the small fixture, ATS-score claims, candidate ranking, production PDF rendering, and unconstrained LLM rewriting before the evidence contract is validated.
