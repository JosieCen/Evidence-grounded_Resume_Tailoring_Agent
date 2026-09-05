# Architecture

## Boundary

The public repository models one narrow problem: evidence-grounded tailoring. It does not attempt to be a complete resume management platform.

```text
Evidence registry + claims
          |
          v
  eligibility / policy
          |
JD -> structured requirements -> retrieval -> coverage-first plan
                                      |
baseline -----------------------------+
                                      v
                         authorized wording selection
                                      |
                                      v
                             deterministic audit
                              /             \
                           pass           violation
                            |                 |
                            |      rewrite from evidence
                            |                 |
                            +<----------------+
                            |
                            v
              resume + analysis + change log + trace
```

## Why the generator is constrained

v0.2 copied claim text directly, so the project demonstrated retrieval more strongly than tailoring. v0.3 adds JD-aware rewriting without pretending that free-form generation is already safe. The default `EvidenceConstrainedGenerator` can select only canonical verified claim text or claim-owned, pre-authorized paraphrases. A future LLM generator can implement the same interface, but the final deterministic audit remains mandatory.

## Requirement identity

`jd.py` computes IDs from normalized requirement text. The ID follows the requirement rather than its position in the JD.

## Authorization order

1. Profile-level unsupported scope can force a requirement to `GAP`.
2. Only verified, visible claims with evidence are retrievable.
3. Retrieval ranks candidates.
4. Generated wording retains claim provenance.
5. Audit checks source validity, evidence references, forbidden phrases, metric ownership, and numeric traceability.
6. Revision rebuilds a sourced invalid bullet from authorized wording.
7. Remaining violations fail the run.

## Human-in-the-loop boundary

The baseline resume remains an editable user artifact. The agent produces a tailored copy and a change log rather than overwriting the baseline.
