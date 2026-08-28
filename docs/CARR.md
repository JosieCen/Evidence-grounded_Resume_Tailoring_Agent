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

For v0.2, I added a minimal `TextEmbedder` interface and an optional Sentence Transformers adapter using `all-MiniLM-L6-v2`. The hybrid retriever currently combines 35% lexical and 65% semantic score. These weights and thresholds are explicit and benchmarkable rather than hidden inside a prompt.

I deliberately did **not** let semantic similarity bypass verification, visibility, provenance, blocked wording, or metric ownership rules.

## R — Results

The v0.2 showcase now includes:

- runnable CLI and Streamlit UI;
- `lexical`, `embedding`, and `hybrid` retriever modes;
- optional Sentence Transformers integration;
- candidate-level lexical, semantic, and combined scores;
- a six-case labeled fictional retrieval benchmark;
- deterministic semantic-retrieval tests plus real-model integration CI;
- claim-level provenance and explicit gaps;
- deterministic guardrails and automatic audit/revision;
- machine-readable audit, run trace, benchmark reports, and GitHub Actions artifacts.

On the six-case benchmark:

| Retriever | Top-1 | Recall@3 | Gap accuracy |
| --- | ---: | ---: | ---: |
| Lexical | 66.7% | 83.3% | 100% |
| Embedding | **83.3%** | **100%** | **100%** |
| Hybrid | **83.3%** | **100%** | **100%** |

The semantic communication paraphrase was a lexical `GAP` but was correctly recovered by embedding and hybrid retrieval. At the same time, the intentionally unsupported enterprise sales/revenue case remained a `GAP` in all modes.

The factual-safety layer also remained unchanged: **7/7 synthetic safety cases pass**, and the lightweight CI currently passes **10 automated tests**.

These are engineering and retrieval-evaluation results, not hiring KPIs. The project does not claim improved interview rate, offer rate, ATS score, or recruiter conversion.

## R — Reflection

v0.2 demonstrates that semantic retrieval can improve recall without weakening factual safety, but the benchmark also reveals an important remaining error: both embedding and hybrid retrieval rank `claim_workflow_eval` above the expected `claim_llm_review_120` for one LLM-safety paraphrase. The expected evidence is still retrieved within Top-3, which is why Recall@3 reaches 100% while Top-1 remains 83.3%.

The next iteration should therefore focus on **calibration and reranking**, not on claiming perfect retrieval:

1. expand the labeled benchmark;
2. inspect false-positive semantic matches by error category;
3. calibrate hybrid weights and strong/partial/gap thresholds;
4. add an optional LLM reranker that can explain semantic equivalence but cannot create evidence;
5. add controlled paraphrasing while preserving source claim IDs and metrics;
6. include human review for ambiguous partial matches.

The product principle remains:

> **Better tailoring is only better if provenance remains intact.**
