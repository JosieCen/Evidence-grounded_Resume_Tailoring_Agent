# CARR Case Study

## C — Context

Resume tailoring with generative AI creates two different failure modes.

First, unconstrained generation can make a candidate sound more relevant by inventing responsibilities, inflating partial matches, or detaching metrics from their original evidence. Second, a purely lexical matcher can be too conservative: transferable experience and semantically equivalent wording may be missed when the JD and profile use different vocabulary.

The product problem therefore became:

> How can an agent increase semantic recall while preserving a single factual source of truth and keeping unsupported requirements visible?

## A — Action

I designed the system so **retrieval and authorization are separate responsibilities**.

Each career claim has a stable ID, evidence references, verification/visibility state, optional blocked wording, semantic tags, and metric metadata. The agent then runs:

1. parse the JD into requirements;
2. retrieve only evidence-eligible claims;
3. rank candidates with lexical, embedding, or hybrid retrieval;
4. expose lexical/semantic/combined retrieval scores;
5. classify each requirement as strong match, partial match, or gap;
6. plan a compact evidence set;
7. draft content using cited claims;
8. run deterministic factual guardrails;
9. revise and re-audit unsafe bullets;
10. emit the resume, evidence map, audit report, and run trace.

For v0.2, I added a minimal `TextEmbedder` interface and an optional Sentence Transformers adapter. The default demo remains dependency-light, while users can opt into semantic or hybrid retrieval. The hybrid retriever currently weights semantic similarity more heavily than lexical overlap, but the weights and thresholds remain explicit and benchmarkable rather than hidden inside a prompt.

I deliberately did **not** let semantic similarity bypass verification, visibility, provenance, blocked wording, or metric ownership rules.

## R — Results

The v0.2 showcase now includes:

- runnable CLI and Streamlit UI;
- `lexical`, `embedding`, and `hybrid` retriever modes;
- optional Sentence Transformers integration;
- candidate-level lexical, semantic, and combined scores;
- structured fictional profile and JD fixtures;
- a six-case labeled semantic retrieval benchmark;
- requirement-to-evidence mapping and explicit gaps;
- claim-level provenance;
- deterministic guardrails;
- automatic audit/revision loop;
- machine-readable audit and run trace;
- GitHub Actions CI;
- deterministic tests showing semantic recovery without lexical overlap while preserving an unrelated gap;
- the original 7/7 synthetic factual-safety baseline.

The existing E2E behavior remains intact: unsupported requirements stay gaps, and an injected unsupported production/revenue bullet is removed before finalization.

These are engineering and evaluation results, not hiring KPIs. The project does not claim improved interview rate, offer rate, ATS score, or recruiter conversion.

## R — Reflection

v0.2 solves the architectural problem of introducing semantic retrieval without weakening factual safety, but it does not prove that the current embedding model or thresholds are optimal.

The next iteration should focus on **calibration and error analysis**:

1. run a larger labeled requirement-to-claim benchmark with a real embedding model;
2. inspect false-positive semantic matches and missed transferable experience;
3. calibrate hybrid weights and strong/partial/gap thresholds;
4. optionally add an LLM reranker that explains semantic equivalence but cannot create evidence;
5. add controlled paraphrasing while preserving source claim IDs and metrics;
6. include human review for ambiguous partial matches.

The product principle remains:

> **Better tailoring is only better if provenance remains intact.**
