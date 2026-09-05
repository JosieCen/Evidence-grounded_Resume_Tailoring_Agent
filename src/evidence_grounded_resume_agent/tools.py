from __future__ import annotations

import re
from collections import defaultdict
from typing import Iterable

from .models import Claim, DraftBullet, Entity, Match, Requirement
from .profile import EvidenceRecord, evidence_issues


STOPWORDS = {
    "and", "or", "the", "a", "an", "to", "of", "in", "for", "with", "on",
    "as", "is", "are", "be", "will", "you", "your", "our", "we", "from",
    "using", "ability", "experience", "work", "role", "responsible", "skills",
}

SYNONYMS = {
    "llm": {"large language model", "language model", "generative ai", "genai"},
    "evaluation": {"assessment", "validation", "benchmark", "qa", "testing"},
    "product": {"prd", "requirement", "requirements", "mvp", "roadmap"},
    "clinical": {"medical", "healthcare", "patient", "clinician"},
    "evidence": {"literature", "source", "provenance", "citation"},
    "automation": {"pipeline", "workflow", "orchestration"},
    "python": {"scripting", "programming"},
    "communication": {"communicate", "communicated", "explain", "explained", "clear", "clearly", "presentation", "scientific writing", "stakeholder", "stakeholders", "training"},
    "analysis": {"analytics", "data", "insight"},
    "project": {"milestone", "planning", "coordination", "delivery"},
    "reproducibility": {"versioning", "testing", "traceability", "audit"},
    "research": {"study", "literature", "scientific"},
}

ZH_TERMS = {
    "产品需求": {"product", "requirement"},
    "临床": {"clinical", "medical"},
    "医疗": {"clinical", "healthcare"},
    "大模型": {"llm", "generative ai"},
    "生成式ai": {"llm", "generative ai"},
    "幻觉": {"hallucination", "llm"},
    "评估": {"evaluation", "validation"},
    "自动化": {"automation", "workflow"},
    "工作流": {"workflow", "automation"},
    "证据": {"evidence", "literature"},
    "科研": {"research", "scientific"},
    "沟通": {"communication", "stakeholder"},
    "跨团队": {"communication", "project"},
    "数据分析": {"analysis", "data"},
    "培训": {"training", "communication"},
    "复现": {"reproducibility", "traceability"},
    "版本": {"reproducibility", "versioning"},
    "里程碑": {"project", "milestone"},
    "用户": {"user", "product"},
    "医生": {"clinician", "clinical"},
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold().strip())


def tokenize(text: str) -> tuple[str, ...]:
    normalized = normalize_text(text)
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+.-]{1,}", normalized)
    clean = [word for word in words if word not in STOPWORDS and len(word) > 1]
    for phrase, expansions in ZH_TERMS.items():
        if phrase in normalized:
            clean.append(phrase)
            clean.extend(sorted(expansions))
    chinese_chunks = re.findall(r"[\u4e00-\u9fff]{2,8}", normalized)
    clean.extend(chinese_chunks)
    return tuple(dict.fromkeys(clean))


def expand_tokens(tokens: Iterable[str]) -> set[str]:
    expanded: set[str] = set(tokens)
    normalized = {item.casefold() for item in tokens}
    for key, synonyms in SYNONYMS.items():
        if key in normalized or normalized.intersection(synonyms):
            expanded.add(key)
            expanded.update(synonyms)
    return expanded


def eligible_claims(
    claims: dict[str, Claim],
    evidence: dict[str, EvidenceRecord] | None = None,
) -> dict[str, Claim]:
    return {
        claim_id: claim
        for claim_id, claim in claims.items()
        if claim.status == "verified"
        and claim.visible
        and claim.evidence_refs
        and not (evidence_issues(claim, evidence or {}) if evidence is not None else [])
    }


def select_claims(matches: list[Match], max_claims: int = 10) -> list[str]:
    """Select for requirement coverage first, then fill remaining slots by aggregate relevance."""

    selected: list[str] = []
    for match in matches:
        if match.match_level == "GAP" or not match.source_claim_ids:
            continue
        top = match.source_claim_ids[0]
        if top not in selected:
            selected.append(top)
        if len(selected) >= max_claims:
            return selected

    scores: defaultdict[str, int] = defaultdict(int)
    for match in matches:
        if match.match_level == "GAP":
            continue
        weight = 4 if match.match_level == "STRONG_MATCH" else 2
        if match.requirement_priority == "medium":
            weight = max(1, weight - 1)
        for rank, claim_id in enumerate(match.source_claim_ids):
            scores[claim_id] += max(1, weight - rank)

    for claim_id, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0])):
        if claim_id not in selected:
            selected.append(claim_id)
        if len(selected) >= max_claims:
            break
    return selected


def requirement_by_id(requirements: list[Requirement]) -> dict[str, Requirement]:
    return {item.id: item for item in requirements}


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
