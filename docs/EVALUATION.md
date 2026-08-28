# Evaluation Strategy

The project evaluates **factual safety** separately from **semantic relevance**.

## 1. Factual-safety evaluation

The committed fictional fixture generates synthetic adversarial cases.

| Case | Expected behavior | Baseline |
| --- | --- | --- |
| Verified + sourced claim | Allow | Pass |
| Missing source | Block | Pass |
| Unknown source | Block | Pass |
| Unverified claim | Block | Pass |
| Hidden claim | Block | Pass |
| Forbidden wording | Block | Pass |
| Untraceable number | Block | Pass |

**Committed baseline: 7/7 passed (100%).**

The machine-readable result is committed at `examples/evaluation_baseline.json`.

## 2. End-to-end safety behavior

The fictional JD intentionally includes one unsupported requirement related to enterprise deployment/revenue ownership. The baseline agent keeps it as a `GAP` instead of fabricating supporting evidence.

The adversarial `--simulate-unsafe-draft` path injects an unsupported production/revenue bullet. The deterministic audit removes it and re-audits before finalization.

## 3. v0.2 semantic retrieval benchmark

`examples/retrieval_benchmark.yaml` adds six labeled fictional cases:

- semantic communication paraphrase;
- product/clinical requirement translation;
- LLM safety review paraphrase;
- provenance/automation paraphrase;
- lexical-overlap control;
- explicit unsupported gap control.

Run the lightweight lexical baseline:

```bash
resume-agent benchmark-retrieval \
  --profile examples/fictional_profile.yaml \
  --benchmark examples/retrieval_benchmark.yaml \
  --retriever lexical \
  --output outputs/lexical_benchmark.json
```

With the optional embedding dependency installed, compare:

```bash
resume-agent benchmark-retrieval --retriever embedding --output outputs/embedding_benchmark.json
resume-agent benchmark-retrieval --retriever hybrid --output outputs/hybrid_benchmark.json
```

The report contains:

- top-1 accuracy;
- recall@3;
- explicit-gap accuracy;
- per-case selected claim IDs;
- observed match level;
- top retrieval score.

## 4. What CI tests in v0.2

CI deliberately does **not** download a large embedding model for every push. Instead, semantic retrieval logic is tested with a deterministic embedding test double.

The tests verify that:

- lexical retrieval can remain a gap when wording has no token overlap;
- embedding retrieval can recover the intended semantically equivalent claim;
- hybrid retrieval can also recover the claim;
- an unrelated commercial requirement remains a gap;
- benchmark metrics are machine-readable;
- all original guardrail and E2E behavior remains intact.

A real embedding model is an integration dependency, while retrieval ranking and safety behavior remain unit-testable without network access.

## 5. Metrics for the next calibration cycle

The larger benchmark should track:

- requirement-level top-1 accuracy;
- recall@K;
- strong/partial/gap classification accuracy;
- false-positive semantic matches;
- unsupported-claim rate after drafting;
- claim traceability coverage;
- metric traceability coverage;
- revision rate;
- human preference for relevance/readability.

A better retriever is only an improvement if semantic recall rises **without increasing unsupported-claim leakage**.
