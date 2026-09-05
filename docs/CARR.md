# CARR Case Study — v0.3

## Context

The first public version solved a useful but narrower problem than its name implied. It could retrieve verified evidence and filter unsupported output, yet drafting mostly copied existing claim text and revision mostly deleted invalid bullets. The six-case benchmark was also too small to support confident conclusions.

## Action

I rebuilt the workflow around four product constraints. Tailoring must change emphasis without changing facts; safety should repair sourced content when possible; a real application starts from an existing resume; and evaluation must expose failure modes. Claims now expose canonical wording plus evidence-preserving paraphrases, revision reconstructs invalid sourced bullets from evidence, a baseline resume emits a before/after change log, and the benchmark grew from 6 to 72 labeled cases including Chinese requirements, semantic transfer, numbers, explicit gaps, overclaim traps, and seniority hard negatives.

I also added structured JD classification with stable IDs, an evidence registry, multilingual semantic retrieval, a profile-level unsupported-scope gate, coverage-first claim planning, and multi-source metric ownership.

## Results

On the committed 72-case lexical fixture: positive Top-1 accuracy **83.3%**, positive Recall@3 **100%**, explicit-gap accuracy **100%**, overall case accuracy **88.9%**. The unsafe sourced-draft demo now passes by **rewriting from evidence**, not merely dropping the bullet.

## Reflection

The most useful improvements came from modeling the actual workflow rather than adding more AI components: an existing baseline, explicit evidence boundaries, visible gaps, repairable revisions, and evaluation by failure category. A future LLM generator is only worth adding if it can live behind the same evidence contract.
