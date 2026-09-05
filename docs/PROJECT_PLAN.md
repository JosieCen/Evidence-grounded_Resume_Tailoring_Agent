# Project Plan

## v0.3 — implemented

- Structured JD parser with stable requirement IDs and type/priority.
- Multilingual semantic-retrieval default and weighted lexical baseline.
- Evidence registry and claim-owned authorized paraphrases.
- Evidence-constrained tailoring and rewrite-based revision.
- Baseline-to-application change log.
- Requirement-level unsupported-scope gate.
- Multi-source metric ownership.
- 72-case benchmark and per-category evaluation.
- Streamlit before/after review and expanded CI tests.

## Next

1. Build a second independently authored benchmark to reduce fixture leakage.
2. Calibrate embedding/hybrid thresholds on that independent set.
3. Add optional LLM drafting behind the existing provenance/audit interface.
4. Add human review labels for semantic equivalence and rewrite quality.
