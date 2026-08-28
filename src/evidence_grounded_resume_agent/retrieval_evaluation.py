from __future__ import annotations

from typing import Any

from .models import Requirement
from .profile import claim_index, parse_entities
from .retrieval import RetrievalConfig, TextEmbedder, match_requirements
from .tools import eligible_claims, tokenize


def run_retrieval_benchmark(
    profile: dict[str, Any],
    benchmark: dict[str, Any],
    *,
    retriever_mode: str = "lexical",
    embedder: TextEmbedder | None = None,
) -> dict[str, Any]:
    claims = eligible_claims(claim_index(parse_entities(profile)))
    cases = benchmark.get("cases", [])
    requirements = [
        Requirement(
            id=str(case.get("id", f"case_{index:02d}")),
            text=str(case["requirement"]),
            tokens=tokenize(str(case["requirement"])),
        )
        for index, case in enumerate(cases, start=1)
    ]
    matches = match_requirements(
        requirements,
        claims,
        config=RetrievalConfig(mode=retriever_mode),
        embedder=embedder,
    )

    results: list[dict[str, Any]] = []
    top1_correct = 0
    recall_at_3_correct = 0
    gap_correct = 0
    gap_cases = 0

    for case, match in zip(cases, matches, strict=True):
        expected = {str(item) for item in case.get("expected_claim_ids", [])}
        expect_gap = bool(case.get("expect_gap", False))
        selected = match.source_claim_ids

        if expect_gap:
            gap_cases += 1
            top1_ok = match.match_level == "GAP"
            recall_ok = top1_ok
            gap_correct += int(top1_ok)
        else:
            top1_ok = bool(selected) and selected[0] in expected
            recall_ok = bool(expected.intersection(selected[:3]))

        top1_correct += int(top1_ok)
        recall_at_3_correct += int(recall_ok)
        results.append(
            {
                "id": case.get("id"),
                "requirement": case["requirement"],
                "expected_claim_ids": sorted(expected),
                "expect_gap": expect_gap,
                "observed_match_level": match.match_level,
                "observed_claim_ids": selected,
                "top_score": match.top_score,
                "top1_correct": top1_ok,
                "recall_at_3_correct": recall_ok,
            }
        )

    total = len(results)
    return {
        "retriever_mode": retriever_mode,
        "cases": total,
        "top1_accuracy": top1_correct / total if total else 0.0,
        "recall_at_3": recall_at_3_correct / total if total else 0.0,
        "gap_accuracy": gap_correct / gap_cases if gap_cases else None,
        "results": results,
    }
