from __future__ import annotations

import re
from typing import Any

from .models import Claim, DraftBullet


NUMBER_PATTERN = re.compile(r"(?<![A-Za-z-])\d+(?:[.,]\d+)?%?")


def _metric_tokens(claim: Claim) -> set[str]:
    tokens: set[str] = set()
    for metric in claim.metrics:
        if "value" in metric:
            tokens.update(NUMBER_PATTERN.findall(str(metric["value"])))
    return tokens


def audit_bullets(bullets: list[DraftBullet], claims: dict[str, Claim]) -> list[dict[str, Any]]:
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

        for claim_id in bullet.source_claim_ids:
            claim = claims.get(claim_id)
            if claim is None:
                violations.append({"type": "unknown_source", "location": location, "claim_id": claim_id})
                continue
            if claim.status != "verified":
                violations.append({"type": "unverified_claim", "location": location, "claim_id": claim_id})
            if not claim.visible:
                violations.append({"type": "hidden_claim", "location": location, "claim_id": claim_id})
            if not claim.evidence_refs:
                violations.append({"type": "missing_evidence", "location": location, "claim_id": claim_id})
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

            numbers = NUMBER_PATTERN.findall(bullet.text)
            allowed_numbers = _metric_tokens(claim)
            for number in numbers:
                if number not in allowed_numbers:
                    violations.append(
                        {
                            "type": "untraceable_number",
                            "location": location,
                            "claim_id": claim_id,
                            "number": number,
                        }
                    )
    return violations


def remove_invalid_bullets(
    bullets: list[DraftBullet], violations: list[dict[str, Any]]
) -> list[DraftBullet]:
    blocked_locations = {item["location"] for item in violations}
    return [
        bullet
        for index, bullet in enumerate(bullets)
        if f"bullet_{index+1:02d}" not in blocked_locations
    ]
