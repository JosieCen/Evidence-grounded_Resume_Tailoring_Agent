# CARR Case Study

## C — Context

When tailoring a resume to different job descriptions, generative AI creates a tension between **relevance** and **truthfulness**. A model can quickly rewrite content into role-specific language, but free-form generation can also introduce responsibilities the candidate never performed, turn partial overlap into an apparent match, or detach metrics from their original evidence.

The product problem was therefore not simply "generate a better resume." It was:

> How can an agent optimize role relevance while maintaining a single factual source of truth and making unsupported requirements visible instead of hallucinating around them?

## A — Action

I designed the system around a structured evidence model rather than free-form source text.

Each career claim receives a stable ID, evidence references, verification/visibility status, optional blocked wording, semantic tags and metric metadata. The agent then runs a multi-step workflow:

1. parse the JD into requirements;
2. retrieve verified claims relevant to each requirement;
3. classify requirements as strong match, partial match or gap;
4. plan a compact evidence set;
5. draft tailored content using only authorized claims;
6. run deterministic guardrail checks;
7. revise and re-audit when a violation is detected;
8. emit the resume plus an evidence map, audit report and run trace.

I deliberately kept factual authorization outside the generative/reasoning layer. This makes it possible to replace the current local matcher with an LLM or embedding retriever later without changing the core safety contract.

## R — Results

The v0.1 showcase now includes:

- runnable CLI;
- optional Streamlit prototype;
- structured fictional profile and JD fixtures;
- requirement-to-evidence mapping;
- explicit gap handling;
- claim-level provenance;
- deterministic guardrails;
- automatic audit/revision loop;
- machine-readable audit and run trace;
- GitHub Actions CI;
- 7 automated tests passing;
- 7/7 synthetic guardrail cases passing.

In the baseline E2E demo, the agent selected 5 verified claims, produced 5 traceable bullets, preserved 1 intentionally unsupported JD requirement as a gap, and returned 0 final violations. In an adversarial demo, an injected unsupported "production deployment + 42% revenue" bullet was detected and removed in one revision cycle before finalization.

These are engineering/evaluation results rather than business KPIs; the project makes no claim about offer rate or recruiter conversion because it has not been deployed in a real hiring experiment.

## R — Reflection

The strongest aspect of v0.1 is not semantic matching quality; it is the separation between relevance generation and factual authorization. The current token/synonym retriever is intentionally interpretable but too simple for nuanced real-world JD semantics.

The next iteration should therefore focus on **semantic quality without weakening factual safety**:

1. introduce an LLM/embedding retriever behind the same claim-selection interface;
2. create a larger labeled synthetic benchmark for requirement-to-claim matching;
3. add controlled paraphrasing while preserving claim IDs and metric provenance;
4. compare relevance/readability improvements against unsupported-claim rate;
5. add human review controls for partial matches and style preferences.

The key product principle for iteration is: **better tailoring is only better if provenance remains intact.**
