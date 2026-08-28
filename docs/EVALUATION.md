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

**Baseline: 7/7 passed (100%).**

The E2E demo also keeps an unsupported enterprise deployment/revenue requirement as a `GAP`. The adversarial `--simulate-unsafe-draft` path injects an unsupported production/revenue bullet; the deterministic audit removes it and re-audits before finalization.

## 2. v0.2 retrieval benchmark

`examples/retrieval_benchmark.yaml` contains six labeled fictional cases covering semantic paraphrases, a lexical control, and an explicit unsupported gap.

### Aggregate results

| Retriever | Top-1 accuracy | Recall@3 | Gap accuracy |
| --- | ---: | ---: | ---: |
| Lexical | 66.7% | 83.3% | 100% |
| Embedding (`all-MiniLM-L6-v2`) | **83.3%** | **100%** | **100%** |
| Hybrid (35% lexical / 65% semantic) | **83.3%** | **100%** | **100%** |

The aggregate summary is committed at `examples/retrieval_baseline_summary.json`.

### Most informative recovery

Requirement:

> Explain complex technical findings clearly to non-specialist audiences.

- lexical: `GAP`;
- embedding: `PARTIAL_MATCH` → `claim_scientific_communication`, score 0.3414;
- hybrid: `PARTIAL_MATCH` → `claim_scientific_communication`, score 0.2219.

This is the intended v0.2 behavior: semantic retrieval recovers a plausible paraphrase without changing the evidence authorization rules.

### Remaining error

The real embedding and hybrid runs both miss Top-1 on the `semantic_llm_safety` case: `claim_workflow_eval` ranks ahead of the expected `claim_llm_review_120`, although the expected claim remains inside Top-3. This is why Recall@3 reaches 100% while Top-1 remains 83.3%.

That error is useful rather than hidden: the next calibration cycle should focus on reranking and threshold/weight tuning instead of claiming perfect retrieval.

## 3. Running the benchmark

Lexical:

```bash
resume-agent benchmark-retrieval \
  --profile examples/fictional_profile.yaml \
  --benchmark examples/retrieval_benchmark.yaml \
  --retriever lexical \
  --output outputs/lexical_benchmark.json
```

Embedding/hybrid:

```bash
pip install -e ".[embedding]"
resume-agent benchmark-retrieval --retriever embedding --output outputs/embedding_benchmark.json
resume-agent benchmark-retrieval --retriever hybrid --output outputs/hybrid_benchmark.json
```

Reports contain top-1 accuracy, recall@3, explicit-gap accuracy, selected claim IDs, observed match level, and retrieval scores.

## 4. CI strategy

The lightweight CI runs on every push and currently passes **10 automated tests**. It also executes:

- lexical E2E agent run;
- 7-case factual-safety evaluation;
- lexical retrieval benchmark.

Semantic retrieval logic is unit-tested with a deterministic embedding test double, verifying semantic recovery without requiring a network/model download.

A separate **Semantic Retrieval Benchmark** GitHub Actions workflow installs Sentence Transformers 6.0.0, runs the real embedding and hybrid benchmark, and uploads both result JSON files as an artifact. The real-model integration workflow completed successfully on the v0.2 implementation.

## 5. Next calibration metrics

A larger benchmark should track:

- top-1 accuracy and Recall@K;
- strong/partial/gap classification accuracy;
- false-positive semantic matches;
- per-domain retrieval performance;
- unsupported-claim rate after drafting;
- claim/metric traceability coverage;
- revision rate;
- human preference for relevance/readability.

A better retriever is only an improvement if semantic recall rises **without increasing unsupported-claim leakage**.
