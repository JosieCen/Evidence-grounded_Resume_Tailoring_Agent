from __future__ import annotations

from collections import defaultdict
from typing import Protocol

from .models import Claim, DraftBullet, Match, Requirement
from .tools import expand_tokens, tokenize


class BulletGenerator(Protocol):
    def draft(
        self,
        selected_claim_ids: list[str],
        matches: list[Match],
        claims: dict[str, Claim],
        requirements: list[Requirement],
    ) -> list[DraftBullet]:
        ...


def _candidate_score(text: str, requirement: Requirement | None) -> int:
    if requirement is None:
        return 0
    left = expand_tokens(tokenize(text))
    right = expand_tokens(requirement.tokens)
    return len(left.intersection(right))


class EvidenceConstrainedGenerator:
    """Selects only pre-authorized evidence-preserving wording.

    The generator never creates a new factual proposition. It can choose between the
    canonical claim and pre-approved paraphrases, then keeps provenance attached.
    """

    def draft(
        self,
        selected_claim_ids: list[str],
        matches: list[Match],
        claims: dict[str, Claim],
        requirements: list[Requirement],
    ) -> list[DraftBullet]:
        req_by_id = {item.id: item for item in requirements}
        requirement_by_claim: defaultdict[str, list[str]] = defaultdict(list)
        for match in matches:
            if match.match_level == "GAP":
                continue
            for claim_id in match.source_claim_ids:
                requirement_by_claim[claim_id].append(match.requirement_id)

        bullets: list[DraftBullet] = []
        for claim_id in selected_claim_ids:
            claim = claims[claim_id]
            req_ids = sorted(set(requirement_by_claim[claim_id]))
            primary_req = req_by_id.get(req_ids[0]) if req_ids else None
            candidates = [claim.text, *claim.paraphrases]
            selected_text = max(
                candidates,
                key=lambda text: (_candidate_score(text, primary_req), -candidates.index(text)),
            )
            reason = (
                f"Selected authorized wording for {primary_req.id} based on JD overlap."
                if primary_req
                else "Selected canonical verified wording."
            )
            bullets.append(
                DraftBullet(
                    text=selected_text,
                    source_claim_ids=[claim_id],
                    requirement_ids=req_ids,
                    metric_ids=[str(metric["id"]) for metric in claim.metrics if "id" in metric],
                    original_text=claim.text,
                    change_reason=reason,
                )
            )
        return bullets


def revise_bullet_from_evidence(
    bullet: DraftBullet,
    claims: dict[str, Claim],
    requirements: dict[str, Requirement],
    violation_types: set[str],
) -> DraftBullet | None:
    """Repair a draft using authorized source wording; return None if no valid source exists."""

    valid_claims = [
        claims[claim_id]
        for claim_id in bullet.source_claim_ids
        if claim_id in claims
        and claims[claim_id].status == "verified"
        and claims[claim_id].visible
        and claims[claim_id].evidence_refs
    ]
    if not valid_claims:
        return None

    primary = valid_claims[0]
    requirement = next(
        (requirements[req_id] for req_id in bullet.requirement_ids if req_id in requirements),
        None,
    )
    candidates = [primary.text, *primary.paraphrases]
    safe_candidates = [
        text
        for text in candidates
        if not any(forbidden.casefold() in text.casefold() for forbidden in primary.do_not_claim)
    ]
    if not safe_candidates:
        safe_candidates = [primary.text]

    selected_text = max(
        safe_candidates,
        key=lambda text: (_candidate_score(text, requirement), -safe_candidates.index(text)),
    )
    note = "Rewritten from authorized evidence after: " + ", ".join(sorted(violation_types))
    return DraftBullet(
        text=selected_text,
        source_claim_ids=list(bullet.source_claim_ids),
        requirement_ids=list(bullet.requirement_ids),
        metric_ids=[str(metric["id"]) for metric in primary.metrics if "id" in metric],
        original_text=bullet.original_text or primary.text,
        change_reason=bullet.change_reason,
        revision_notes=[*bullet.revision_notes, note],
    )
