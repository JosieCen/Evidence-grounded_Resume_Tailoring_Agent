from __future__ import annotations

import re
from typing import Any

from .models import Claim, DraftBullet, EvidenceRecord


NUMBER_PATTERN = re.compile(r"(?<![A-Za-z-])\d+(?:[.,]\d+)?%?")


def _canonical_number(value: str) -> str:
    return value.rstrip("%").replace(",", "")


def _metric_tokens(claim: Claim) -> set[str]:
    tokens: set[str] = set()
    for metric in claim.metrics:
        if "value" in metric:
            tokens.update(_canonical_number(item) for item in NUMBER_PATTERN.findall(str(metric["value"])))
    return tokens


def _metric_ids(claim: Claim) -> set[str]:
    return {str(metric["id"]) for metric in claim.metrics if "id" in metric}


def audit_bullets(
    bullets: list[DraftBullet],
    claims: dict[str, Claim],
    evidence: dict[str, EvidenceRecord] | None = None,
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    seen_text: set[str] = set()

    for index, bullet in enumerate(bullets):
        location = f"bullet_{index+1:02d}"
        normalized_text = bullet.text.casefold().strip()
        if normalized_text in seen_text:
            violations.append({"type": "duplicate_bullet", "location": location})
        seen_text.add(normalized_text)

        if not bullet.source_claim_ids:
            violations.append({"type": "missing_source", "location": location})
            continue

        source_claims: list[Claim] = []
        for claim_id in bullet.source_claim_ids:
            claim = claims.get(claim_id)
            if claim is None:
                violations.append({"type": "unknown_source", "location": location, "claim_id": claim_id})
                continue
            source_claims.append(claim)
            if claim.status != "verified":
                violations.append({"type": "unverified_claim", "location": location, "claim_id": claim_id})
            if not claim.visible:
                violations.append({"type": "hidden_claim", "location": location, "claim_id": claim_id})
            if not claim.evidence_refs:
                violations.append({"type": "missing_evidence", "location": location, "claim_id": claim_id})
            if evidence is not None:
                for ref in claim.evidence_refs:
                    record = evidence.get(ref)
                    if record is None:
                        violations.append(
                            {"type": "unknown_evidence", "location": location, "claim_id": claim_id, "evidence_ref": ref}
                        )
                    elif record.status != "verified":
                        violations.append(
                            {"type": "unverified_evidence", "location": location, "claim_id": claim_id, "evidence_ref": ref}
                        )
            for forbidden in claim.do_not_claim:
                if forbidden.casefold() in normalized_text:
                    violations.append(
                        {
                            "type": "forbidden_phrase",
                            "location": location,
                            "claim_id": claim_id,
                            "phrase": forbidden,
                        }
                    )

        allowed_numbers = set().union(*(_metric_tokens(claim) for claim in source_claims)) if source_claims else set()
        for number in NUMBER_PATTERN.findall(bullet.text):
            if _canonical_number(number) not in allowed_numbers:
                violations.append(
                    {"type": "untraceable_number", "location": location, "number": number}
                )

        allowed_metric_ids = set().union(*(_metric_ids(claim) for claim in source_claims)) if source_claims else set()
        for metric_id in bullet.metric_ids:
            if metric_id not in allowed_metric_ids:
                violations.append(
                    {"type": "metric_not_owned_by_source", "location": location, "metric_id": metric_id}
                )

    return violations


def violation_types_by_location(violations: list[dict[str, Any]]) -> dict[str, set[str]]:
    output: dict[str, set[str]] = {}
    for item in violations:
        output.setdefault(str(item["location"]), set()).add(str(item["type"]))
    return output
