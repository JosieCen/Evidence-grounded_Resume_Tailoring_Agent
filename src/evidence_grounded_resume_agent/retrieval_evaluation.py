from __future__ import annotations

from collections import defaultdict
from typing import Any

from .models import Requirement
from .profile import claim_index, parse_entities, parse_evidence
from .retrieval import RetrievalConfig, TextEmbedder, match_requirements
from .tools import eligible_claims, tokenize


def _rate(value: int, total: int) -> float | None:
    return value / total if total else None


def run_retrieval_benchmark(
    profile: dict[str, Any],
    benchmark: dict[str, Any],
    *,
    retriever_mode: str = "lexical",
    embedder: TextEmbedder | None = None,
) -> dict[str, Any]:
    evidence = parse_evidence(profile)
    claims = eligible_claims(
        claim_index(parse_entities(profile)),
        evidence if evidence else None,
    )
    cases = benchmark.get("cases", [])
    requirements = [
        Requirement(
            id=str(case.get("id", f"case_{index:03d}")),
            text=str(case["requirement"]),
            tokens=tokenize(str(case["requirement"])),
            kind=str(case.get("kind", "responsibility")),
            priority=str(case.get("priority", "high")),
        )
        for index, case in enumerate(cases, start=1)
    ]
    matches = match_requirements(
        requirements,
        claims,
        config=RetrievalConfig(mode=retriever_mode),
        embedder=embedder,
        unsupported_phrases=tuple(str(item) for item in profile.get("do_not_claim", [])),
    )

    results: list[dict[str, Any]] = []
    positive_cases = 0
    positive_top1 = 0
    positive_recall3 = 0
    gap_cases = 0
    gap_correct = 0
    overall_correct = 0
    forbidden_top1 = 0
    forbidden_cases = 0
    category_stats: defaultdict[str, dict[str, int]] = defaultdict(
        lambda: {
            "cases": 0,
            "positive": 0,
            "top1": 0,
            "recall3": 0,
            "gaps": 0,
            "gap_correct": 0,
            "overall_correct": 0,
        }
    )

    for case, match in zip(cases, matches, strict=True):
        expected = {str(item) for item in case.get("expected_claim_ids", [])}
        forbidden = {str(item) for item in case.get("forbidden_claim_ids", [])}
        expect_gap = bool(case.get("expect_gap", False))
        selected = match.source_claim_ids
        category = str(case.get("category", "uncategorized"))
        stat = category_stats[category]
        stat["cases"] += 1

        if expect_gap:
            gap_cases += 1
            stat["gaps"] += 1
            top1_ok = match.match_level == "GAP"
            recall_ok = top1_ok
            gap_correct += int(top1_ok)
            stat["gap_correct"] += int(top1_ok)
        else:
            positive_cases += 1
            stat["positive"] += 1
            top1_ok = bool(selected) and selected[0] in expected
            recall_ok = bool(expected.intersection(selected[:3]))
            positive_top1 += int(top1_ok)
            positive_recall3 += int(recall_ok)
            stat["top1"] += int(top1_ok)
            stat["recall3"] += int(recall_ok)

        case_correct = top1_ok if not expect_gap else match.match_level == "GAP"
        overall_correct += int(case_correct)
        stat["overall_correct"] += int(case_correct)

        if forbidden:
            forbidden_cases += 1
            forbidden_top1 += int(bool(selected) and selected[0] in forbidden)

        results.append(
            {
                "id": case.get("id"),
                "category": category,
                "language": case.get("language", "en"),
                "requirement": case["requirement"],
                "expected_claim_ids": sorted(expected),
                "forbidden_claim_ids": sorted(forbidden),
                "expect_gap": expect_gap,
                "observed_match_level": match.match_level,
                "observed_claim_ids": selected,
                "top_score": match.top_score,
                "top1_correct": top1_ok,
                "recall_at_3_correct": recall_ok,
            }
        )

    by_category: dict[str, Any] = {}
    for category, stat in sorted(category_stats.items()):
        by_category[category] = {
            "cases": stat["cases"],
            "top1_accuracy": _rate(stat["top1"], stat["positive"]),
            "recall_at_3": _rate(stat["recall3"], stat["positive"]),
            "gap_accuracy": _rate(stat["gap_correct"], stat["gaps"]),
            "overall_case_accuracy": _rate(stat["overall_correct"], stat["cases"]),
        }

    total = len(results)
    return {
        "retriever_mode": retriever_mode,
        "cases": total,
        "positive_cases": positive_cases,
        "gap_cases": gap_cases,
        "top1_accuracy": _rate(positive_top1, positive_cases),
        "recall_at_3": _rate(positive_recall3, positive_cases),
        "gap_accuracy": _rate(gap_correct, gap_cases),
        "false_positive_rate_on_gaps": (
            1 - gap_correct / gap_cases if gap_cases else None
        ),
        "forbidden_top1_rate": _rate(forbidden_top1, forbidden_cases),
        "overall_case_accuracy": _rate(overall_correct, total),
        "by_category": by_category,
        "results": results,
    }
