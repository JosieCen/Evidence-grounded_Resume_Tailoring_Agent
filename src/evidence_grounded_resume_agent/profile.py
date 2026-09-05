from __future__ import annotations

from typing import Any

from .models import Claim, Entity, EvidenceRecord


def _metric_tuple(raw: Any) -> tuple[dict[str, Any], ...]:
    if not raw:
        return ()
    if not isinstance(raw, list):
        raise ValueError("metrics must be a list")
    return tuple(item for item in raw if isinstance(item, dict))


def _string_tuple(raw: Any) -> tuple[str, ...]:
    if not raw:
        return ()
    if not isinstance(raw, list):
        raise ValueError("expected a list of strings")
    return tuple(str(item) for item in raw)


def parse_evidence(profile: dict[str, Any]) -> dict[str, EvidenceRecord]:
    records: dict[str, EvidenceRecord] = {}
    for raw in profile.get("evidence", []):
        record = EvidenceRecord(
            id=str(raw["id"]),
            type=str(raw.get("type", "artifact")),
            description=str(raw.get("description", "")),
            status=str(raw.get("status", "verified")),
        )
        if record.id in records:
            raise ValueError(f"Duplicate evidence id: {record.id}")
        records[record.id] = record
    return records


def parse_entities(profile: dict[str, Any]) -> list[Entity]:
    entities: list[Entity] = []
    for raw in profile.get("entities", []):
        claims: list[Claim] = []
        for claim in raw.get("claims", []):
            claims.append(
                Claim(
                    id=str(claim["id"]),
                    text=str(claim["text"]),
                    evidence_refs=_string_tuple(claim.get("evidence_refs", [])),
                    tags=_string_tuple(claim.get("tags", [])),
                    status=str(claim.get("status", "verified")),
                    visible=bool(claim.get("visible", True)),
                    do_not_claim=_string_tuple(claim.get("do_not_claim", [])),
                    metrics=_metric_tuple(claim.get("metrics", [])),
                    paraphrases=_string_tuple(claim.get("paraphrases", [])),
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


def evidence_issues(claim: Claim, evidence: dict[str, EvidenceRecord]) -> list[str]:
    if not claim.evidence_refs:
        return ["missing_evidence"]
    if not evidence:
        return []
    issues: list[str] = []
    for ref in claim.evidence_refs:
        record = evidence.get(ref)
        if record is None:
            issues.append(f"unknown_evidence:{ref}")
        elif record.status != "verified":
            issues.append(f"unverified_evidence:{ref}")
    return issues
