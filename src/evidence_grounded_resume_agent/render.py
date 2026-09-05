from __future__ import annotations

from dataclasses import asdict

from .models import DraftBullet, Entity, Match
from .tools import group_bullets_by_entity


def render_resume_markdown(
    candidate_name: str,
    target_role: str,
    bullets: list[DraftBullet],
    entity_lookup: dict[str, Entity],
) -> str:
    lines = [f"# {candidate_name}", "", f"**Target role:** {target_role}", ""]
    for entity, entity_bullets in group_bullets_by_entity(bullets, entity_lookup):
        lines.extend([f"## {entity.title}", f"*{entity.organization}*", ""])
        for bullet in entity_bullets:
            lines.append(f"- {bullet.text}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_resume_document(
    candidate_name: str,
    target_role: str,
    bullets: list[DraftBullet],
    entity_lookup: dict[str, Entity],
) -> dict:
    entries = []
    for entity, entity_bullets in group_bullets_by_entity(bullets, entity_lookup):
        entries.append(
            {
                "entity_id": entity.id,
                "title": entity.title,
                "organization": entity.organization,
                "category": entity.category,
                "bullets": [asdict(item) for item in entity_bullets],
            }
        )
    return {
        "candidate": {"name": candidate_name},
        "target_role": target_role,
        "entries": entries,
    }


def render_analysis(matches: list[Match]) -> dict:
    return {
        "retrieval_mode": matches[0].retrieval_mode if matches else "unknown",
        "requirements": [
            {
                "id": match.requirement_id,
                "text": match.requirement_text,
                "kind": match.requirement_kind,
                "priority": match.requirement_priority,
                "match_level": match.match_level,
                "retrieval_mode": match.retrieval_mode,
                "top_score": match.top_score,
                "source_claim_ids": match.source_claim_ids,
                "overlap_tokens": match.overlap_tokens,
                "candidate_scores": match.candidate_scores,
                "authorization_note": match.authorization_note,
            }
            for match in matches
        ],
        "gaps": [
            {
                "id": match.requirement_id,
                "text": match.requirement_text,
                "kind": match.requirement_kind,
                "priority": match.requirement_priority,
            }
            for match in matches
            if match.match_level == "GAP"
        ],
    }
