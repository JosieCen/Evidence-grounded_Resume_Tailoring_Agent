from __future__ import annotations

from dataclasses import replace
from typing import Any

from .guardrails import audit_bullets
from .models import DraftBullet
from .profile import claim_index, parse_entities


def run_guardrail_evaluation(profile: dict[str, Any]) -> dict[str, Any]:
    claims = claim_index(parse_entities(profile))
    verified_id = next(claim_id for claim_id, claim in claims.items() if claim.status == "verified" and claim.visible)
    verified = claims[verified_id]

    synthetic_cases: list[tuple[str, DraftBullet, str | None]] = [
        (
            "safe_verified_claim",
            DraftBullet(verified.text, [verified_id], ["req_01"], [m["id"] for m in verified.metrics if "id" in m]),
            None,
        ),
        (
            "missing_source",
            DraftBullet("Built a healthcare AI product.", [], ["req_01"], []),
            "missing_source",
        ),
        (
            "unknown_source",
            DraftBullet("Built a healthcare AI product.", ["claim_unknown"], ["req_01"], []),
            "unknown_source",
        ),
    ]

    unverified = next((claim for claim in claims.values() if claim.status != "verified"), None)
    if unverified:
        synthetic_cases.append(
            (
                "unverified_claim",
                DraftBullet(unverified.text, [unverified.id], ["req_01"], []),
                "unverified_claim",
            )
        )
    hidden = next((claim for claim in claims.values() if not claim.visible), None)
    if hidden:
        synthetic_cases.append(
            (
                "hidden_claim",
                DraftBullet(hidden.text, [hidden.id], ["req_01"], []),
                "hidden_claim",
            )
        )
    forbidden = next((claim for claim in claims.values() if claim.do_not_claim), None)
    if forbidden:
        synthetic_cases.append(
            (
                "forbidden_phrase",
                DraftBullet(
                    forbidden.text + " " + forbidden.do_not_claim[0],
                    [forbidden.id],
                    ["req_01"],
                    [],
                ),
                "forbidden_phrase",
            )
        )
    metric_claim = next((claim for claim in claims.values() if claim.metrics), None)
    if metric_claim:
        synthetic_cases.append(
            (
                "untraceable_number",
                DraftBullet(metric_claim.text + " Improved by 99%.", [metric_claim.id], ["req_01"], []),
                "untraceable_number",
            )
        )

    results = []
    passed = 0
    for name, bullet, expected_violation in synthetic_cases:
        violations = audit_bullets([bullet], claims)
        types = {item["type"] for item in violations}
        case_passed = (expected_violation is None and not types) or (
            expected_violation is not None and expected_violation in types
        )
        passed += int(case_passed)
        results.append(
            {
                "case": name,
                "expected": expected_violation or "no_violation",
                "observed": sorted(types) if types else ["no_violation"],
                "passed": case_passed,
            }
        )

    return {
        "cases": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": round(passed / len(results), 4) if results else 0.0,
        "results": results,
    }
