# Evaluation

v0.3 separates three questions that are often collapsed into one score.

## 1. Retrieval relevance

`examples/retrieval_benchmark.yaml` contains 72 fictional labeled cases: 48 positive and 24 explicit gaps/hard negatives.

Metrics: positive Top-1 accuracy; positive Recall@3; explicit-gap accuracy; false-positive rate on gap cases; forbidden-top1 rate; overall case accuracy; and the same metrics split by category.

The committed lexical baseline is 83.3% Top-1, 100% Recall@3, 100% gap accuracy, and 88.9% overall case accuracy on this fixture. The real embedding/hybrid benchmark runs in GitHub Actions with `paraphrase-multilingual-MiniLM-L12-v2`.

## 2. Factual authorization

`resume-agent evaluate` exercises missing/unknown sources, unverified/hidden claims, forbidden phrases, untraceable numbers, metric ownership, valid multi-source numeric union, and safe verified content. This suite tests deterministic safety rules, not semantic retrieval.

## 3. Workflow integrity

Pytest covers stable JD IDs, requirement type/priority, controlled wording selection, unsupported-scope forced gaps, evidence-registry validation, multi-source metric ownership, true rewrite-based revision, baseline change logging, and minimum benchmark size/category coverage.

## Interpretation

A high retrieval score does not mean the resume is factually safe. A passing guardrail suite does not mean retrieval is semantically good. The project keeps those evaluations separate on purpose.
