from __future__ import annotations

from typing import Any

from .models import Claim, Entity


def _metric_tuple(raw: Any) -> tuple[dict[str, Any], ...]:
    if not raw:
        return ()
    if not isinstance(raw, list):
        raise ValueError("metrics must be a list")
    return tuple(item for item in raw if isinstance(item, dict))


def parse_entities(profile: dict[str, Any]) -> list[Entity]:
    entities: list[Entity] = []
    for raw in profile.get("entities", []):
        claims: list[Claim] = []
        for claim in raw.get("claims", []):
            claims.append(
                Claim(
                    id=str(claim["id"]),
                    text=str(claim["text"]),
                    evidence_refs=tuple(str(x) for x in claim.get("evidence_refs", [])),
                    tags=tuple(str(x) for x in claim.get("tags", [])),
                    status=str(claim.get("status", "verified")),
                    visible=bool(claim.get("visible", True)),
                    do_not_claim=tuple(str(x) for x in claim.get("do_not_claim", [])),
                    metrics=_metric_tuple(claim.get("metrics", [])),
                )
            )
        entities.append(
            Entity(
                id=str(raw["id"]),
                title=str(raw["title"]),
                organization=str(raw.get("organization", "")),
                category=str(raw.get("category", "experience")),
                claims=tuple(claims),
            )
        )
    return entities


def claim_index(entities: list[Entity]) -> dict[str, Claim]:
    index: dict[str, Claim] = {}
    for entity in entities:
        for claim in entity.claims:
            if claim.id in index:
                raise ValueError(f"Duplicate claim id: {claim.id}")
            index[claim.id] = claim
    return index


def entity_by_claim(entities: list[Entity]) -> dict[str, Entity]:
    output: dict[str, Entity] = {}
    for entity in entities:
        for claim in entity.claims:
            output[claim.id] = entity
    return output
