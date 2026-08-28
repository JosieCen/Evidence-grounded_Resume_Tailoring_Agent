# v0.2 Semantic Retrieval Plan

This document tracks the v0.2 implementation before merge.

## Goal

Improve requirement-to-evidence matching without weakening the factual safety contract.

## Scope

- keep deterministic provenance/guardrail authorization unchanged;
- add pluggable `lexical`, `embedding`, and `hybrid` retrieval modes;
- add optional Sentence Transformers embeddings;
- expose retrieval scores in the analysis trace;
- add semantic retrieval tests with deterministic fake embeddings;
- add a labeled retrieval benchmark command;
- keep the default demo API-key free and lightweight.

## Non-goals

- no autonomous factual rewriting;
- no claim generation from the JD;
- no production ranking of candidates;
- no business-outcome claims.
