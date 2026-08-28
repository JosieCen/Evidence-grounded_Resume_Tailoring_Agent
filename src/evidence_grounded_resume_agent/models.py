from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Claim:
    id: str
    text: str
    evidence_refs: tuple[str, ...]
    tags: tuple[str, ...] = ()
    status: str = "verified"
    visible: bool = True
    do_not_claim: tuple[str, ...] = ()
    metrics: tuple[dict[str, Any], ...] = ()


@dataclass(frozen=True)
class Entity:
    id: str
    title: str
    organization: str
    category: str
    claims: tuple[Claim, ...]


@dataclass(frozen=True)
class Requirement:
    id: str
    text: str
    tokens: tuple[str, ...]


@dataclass
class Match:
    requirement_id: str
    requirement_text: str
    match_level: str
    source_claim_ids: list[str] = field(default_factory=list)
    overlap_tokens: list[str] = field(default_factory=list)
    retrieval_mode: str = "lexical"
    top_score: float = 0.0
    candidate_scores: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DraftBullet:
    text: str
    source_claim_ids: list[str]
    requirement_ids: list[str]
    metric_ids: list[str]


@dataclass
class AgentState:
    step: str = "initialized"
    requirements: list[Requirement] = field(default_factory=list)
    matches: list[Match] = field(default_factory=list)
    selected_claim_ids: list[str] = field(default_factory=list)
    bullets: list[DraftBullet] = field(default_factory=list)
    violations: list[dict[str, Any]] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    revision_count: int = 0
