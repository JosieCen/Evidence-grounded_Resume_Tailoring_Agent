from __future__ import annotations

from typing import Any

from .models import DraftBullet


def baseline_index(document: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not document:
        return {}
    index: dict[str, dict[str, Any]] = {}
    for entry in document.get("entries", []):
        for bullet in entry.get("bullets", []):
            source_ids = [str(item) for item in bullet.get("source_claim_ids", [])]
            if not source_ids:
                continue
            index[source_ids[0]] = {
                "text": str(bullet.get("text", "")),
                "bullet_id": str(bullet.get("id", "")),
                "entity_id": str(entry.get("entity_id", "")),
            }
    return index


def build_change_log(
    bullets: list[DraftBullet],
    baseline: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    before = baseline_index(baseline)
    seen: set[str] = set()
    changes: list[dict[str, Any]] = []
    for bullet in bullets:
        claim_id = bullet.source_claim_ids[0] if bullet.source_claim_ids else ""
        seen.add(claim_id)
        previous = before.get(claim_id)
        old_text = previous["text"] if previous else None
        if old_text is None:
            status = "added"
        elif old_text.strip() == bullet.text.strip():
            status = "unchanged"
        else:
            status = "rephrased"
        changes.append(
            {
                "claim_id": claim_id,
                "status": status,
                "before": old_text,
                "after": bullet.text,
                "requirement_ids": bullet.requirement_ids,
                "reason": bullet.change_reason,
                "revision_notes": bullet.revision_notes,
            }
        )

    for claim_id, previous in before.items():
        if claim_id not in seen:
            changes.append(
                {
                    "claim_id": claim_id,
                    "status": "not_selected",
                    "before": previous["text"],
                    "after": None,
                    "requirement_ids": [],
                    "reason": "Not selected for the target JD.",
                    "revision_notes": [],
                }
            )
    return changes
