from __future__ import annotations

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


def render_analysis(matches: list[Match]) -> dict:
    return {
        "requirements": [
            {
                "id": match.requirement_id,
                "text": match.requirement_text,
                "match_level": match.match_level,
                "source_claim_ids": match.source_claim_ids,
                "overlap_tokens": match.overlap_tokens,
            }
            for match in matches
        ],
        "gaps": [match.requirement_text for match in matches if match.match_level == "GAP"],
    }
