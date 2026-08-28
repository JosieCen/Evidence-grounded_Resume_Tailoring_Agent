from __future__ import annotations

import re
from collections import defaultdict
from typing import Iterable

from .models import Claim, DraftBullet, Entity, Match, Requirement


STOPWORDS = {
    "and", "or", "the", "a", "an", "to", "of", "in", "for", "with", "on",
    "as", "is", "are", "be", "will", "you", "your", "our", "we", "from",
    "using", "ability", "experience", "work", "role", "responsible", "skills",
}

SYNONYMS = {
    "llm": {"large language model", "language model", "generative ai"},
    "evaluation": {"assessment", "validation", "benchmark", "qa"},
    "product": {"prd", "requirement", "mvp", "roadmap"},
    "clinical": {"medical", "healthcare", "patient"},
    "evidence": {"literature", "source", "provenance", "citation"},
    "automation": {"pipeline", "workflow", "orchestration"},
    "python": {"scripting", "programming"},
    "communication": {"presentation", "scientific writing", "stakeholder"},
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold().strip())


def tokenize(text: str) -> tuple[str, ...]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+.-]{1,}|[\u4e00-\u9fff]{2,}", normalize_text(text))
    clean = [word for word in words if word not in STOPWORDS and len(word) > 1]
    return tuple(dict.fromkeys(clean))


def expand_tokens(tokens: Iterable[str]) -> set[str]:
    expanded: set[str] = set(tokens)
    normalized = {item.casefold() for item in tokens}
    for key, synonyms in SYNONYMS.items():
        if key in normalized or normalized.intersection(synonyms):
            expanded.add(key)
            expanded.update(synonyms)
    return expanded


def parse_jd(jd_text: str) -> list[Requirement]:
    requirements: list[Requirement] = []
    for raw_line in jd_text.splitlines():
        line = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", raw_line).strip()
        if not line or line.startswith("#") or len(line) < 12:
            continue
        requirements.append(
            Requirement(
                id=f"req_{len(requirements)+1:02d}",
                text=line,
                tokens=tokenize(line),
            )
        )
    return requirements[:30]


def eligible_claims(claims: dict[str, Claim]) -> dict[str, Claim]:
    return {
        claim_id: claim
        for claim_id, claim in claims.items()
        if claim.status == "verified" and claim.visible and claim.evidence_refs
    }


def match_requirements(requirements: list[Requirement], claims: dict[str, Claim]) -> list[Match]:
    matches: list[Match] = []
    for requirement in requirements:
        req_tokens = expand_tokens(requirement.tokens)
        ranked: list[tuple[float, str, list[str]]] = []
        for claim_id, claim in claims.items():
            claim_tokens = expand_tokens(tokenize(" ".join([claim.text, *claim.tags])))
            overlap = sorted(req_tokens.intersection(claim_tokens))
            if not overlap:
                continue
            denominator = max(3, min(len(req_tokens), 10))
            score = min(1.0, len(overlap) / denominator)
            ranked.append((score, claim_id, overlap))
        ranked.sort(reverse=True)
        selected = ranked[:3]
        if not selected:
            level = "GAP"
        elif selected[0][0] >= 0.45 or len(selected[0][2]) >= 3:
            level = "STRONG_MATCH"
        else:
            level = "PARTIAL_MATCH"
        matches.append(
            Match(
                requirement_id=requirement.id,
                requirement_text=requirement.text,
                match_level=level,
                source_claim_ids=[item[1] for item in selected],
                overlap_tokens=selected[0][2] if selected else [],
            )
        )
    return matches


def select_claims(matches: list[Match], max_claims: int = 6) -> list[str]:
    scores: defaultdict[str, int] = defaultdict(int)
    for match in matches:
        if match.match_level == "GAP":
            continue
        weight = 3 if match.match_level == "STRONG_MATCH" else 1
        for rank, claim_id in enumerate(match.source_claim_ids):
            scores[claim_id] += max(1, weight - rank)
    return [claim_id for claim_id, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:max_claims]]


def compose_bullets(
    selected_claim_ids: list[str],
    matches: list[Match],
    claims: dict[str, Claim],
) -> list[DraftBullet]:
    requirement_by_claim: defaultdict[str, list[str]] = defaultdict(list)
    for match in matches:
        for claim_id in match.source_claim_ids:
            requirement_by_claim[claim_id].append(match.requirement_id)

    bullets: list[DraftBullet] = []
    for claim_id in selected_claim_ids:
        claim = claims[claim_id]
        bullets.append(
            DraftBullet(
                text=claim.text,
                source_claim_ids=[claim_id],
                requirement_ids=sorted(set(requirement_by_claim[claim_id])),
                metric_ids=[str(metric["id"]) for metric in claim.metrics if "id" in metric],
            )
        )
    return bullets


def group_bullets_by_entity(
    bullets: list[DraftBullet],
    entity_lookup: dict[str, Entity],
) -> list[tuple[Entity, list[DraftBullet]]]:
    grouped: dict[str, tuple[Entity, list[DraftBullet]]] = {}
    for bullet in bullets:
        if not bullet.source_claim_ids:
            continue
        entity = entity_lookup[bullet.source_claim_ids[0]]
        if entity.id not in grouped:
            grouped[entity.id] = (entity, [])
        grouped[entity.id][1].append(bullet)
    return list(grouped.values())
