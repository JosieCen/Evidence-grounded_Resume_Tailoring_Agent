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

## Implemented work packages

Structured JD parsing; evidence registry; claim-owned authorized paraphrases; evidence-constrained drafting; rewrite-based revision; baseline-aware change logging; multilingual retrieval; unsupported-scope gate; multi-source metric ownership; 72-case evaluation; Streamlit review; and CI-generated reproducible outputs.

## Deliberately out of scope

Multi-agent orchestration, vector databases for the small fixture, ATS-score claims, candidate ranking, production PDF rendering, and unconstrained LLM rewriting before the evidence contract is validated.
