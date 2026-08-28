# Project Plan

## Product goal

Build a public, privacy-safe showcase that demonstrates how an AI agent can tailor resume content to a job description while preserving factual provenance and explicit gaps.

## Scope

### In scope for v0.1

- structured fictional candidate profile;
- plain-text JD parsing;
- requirement-to-claim evidence retrieval;
- evidence-based claim selection;
- tailored Markdown output;
- claim-level traceability;
- deterministic factual guardrails;
- automatic remove-and-re-audit revision loop;
- synthetic safety evaluation;
- automated tests and CI;
- optional Streamlit demo.

### Out of scope for v0.1

- real personal data;
- ATS vendor integration;
- candidate ranking;
- fully autonomous applications;
- production LLM provider dependency;
- claims of improved interview or offer rates.

## Delivery phases

| Phase | Deliverable | Status |
| --- | --- | --- |
| P0 | Clean public information model + fictional fixture | Complete |
| P1 | JD parsing, retrieval, planning and draft tools | Complete |
| P2 | Guardrail audit + automatic revision loop | Complete |
| P3 | CLI + inspectable artifacts | Complete |
| P4 | Synthetic evaluation + pytest suite | Complete |
| P5 | Streamlit demo + GitHub Actions | Complete |
| P6 | LLM/embedding semantic retriever | Roadmap |
| P7 | Larger benchmark + controlled paraphrasing | Roadmap |

## Definition of portfolio-ready

The repository is considered portfolio-ready when a reviewer can answer the following from the README and demo:

1. What user problem is being solved?
2. Why is this an agent rather than a one-shot prompt?
3. What information is allowed to enter the final output?
4. What happens when the JD asks for experience the candidate does not have?
5. How are hallucination and metric drift evaluated?
6. Can the system be run without private data?
7. What are the current limitations and next iteration?

v0.1 meets these conditions.
