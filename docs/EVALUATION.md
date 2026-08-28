# Evaluation Strategy

The project evaluates **factual safety** separately from **semantic relevance**.

## 1. Guardrail evaluation

The committed fictional fixture is used to generate synthetic adversarial cases.

| Case | Expected behavior | Baseline |
| --- | --- | --- |
| Verified + sourced claim | Allow | Pass |
| Missing source | Block | Pass |
| Unknown source | Block | Pass |
| Unverified claim | Block | Pass |
| Hidden claim | Block | Pass |
| Forbidden wording | Block | Pass |
| Untraceable number | Block | Pass |

**Baseline: 7/7 passed (100%).**

The machine-readable result is committed at `examples/evaluation_baseline.json`.

## 2. End-to-end behavior

The fictional JD intentionally includes one unsupported requirement:

> Lead enterprise production deployments and own commercial revenue targets.

The demo profile does not contain authorized evidence for that responsibility. The agent therefore keeps it as a `GAP` rather than converting it into resume content.

Normal E2E baseline:

- selected verified claims: 5;
- final bullets: 5;
- explicit gaps: 1;
- remaining violations: 0.

## 3. Revision-loop test

`--simulate-unsafe-draft` intentionally injects:

> Led enterprise production deployment and increased revenue by 42%.

with no source claim.

Baseline behavior:

- audit detects the unsupported bullet;
- revision count: 1;
- unsafe bullet removed;
- re-audit passes;
- final remaining violations: 0.

## 4. Automated test suite

Current baseline: **7 tests passed**.

Tests cover:

- E2E traceability;
- explicit gap preservation;
- missing-source blocking;
- unverified-claim blocking;
- hidden-claim blocking;
- untraceable-number blocking;
- automatic agent revision;
- synthetic evaluation-suite integrity.

## 5. Metrics planned for v0.2

Once an LLM/embedding retriever is introduced, semantic matching should be measured independently:

- requirement-level precision;
- requirement-level recall;
- strong/partial/gap classification accuracy;
- unsupported-claim rate after rewriting;
- citation/claim traceability coverage;
- metric traceability coverage;
- revision rate;
- human preference for relevance/readability.

A better semantic model is only an improvement if unsupported-claim rate does not increase.
