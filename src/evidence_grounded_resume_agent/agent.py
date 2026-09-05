from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .application import build_change_log
from .generation import EvidenceConstrainedGenerator, revise_bullet_from_evidence
from .guardrails import audit_bullets, violation_types_by_location
from .io_utils import load_yaml, write_json, write_text, write_yaml
from .jd import parse_jd
from .models import AgentState, DraftBullet
from .profile import claim_index, entity_by_claim, parse_entities, parse_evidence
from .render import render_analysis, render_resume_document, render_resume_markdown
from .retrieval import (
    DEFAULT_EMBEDDING_MODEL,
    RetrievalConfig,
    SentenceTransformerEmbedder,
    TextEmbedder,
    match_requirements,
)
from .tools import eligible_claims, select_claims


class ResumeTailoringAgent:
    """Evidence-grounded tailoring with semantic retrieval and deterministic safety gates."""

    def __init__(
        self,
        max_revisions: int = 2,
        *,
        retriever_mode: str = "lexical",
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        embedder: TextEmbedder | None = None,
    ) -> None:
        self.max_revisions = max_revisions
        self.retrieval_config = RetrievalConfig(mode=retriever_mode)
        self.embedding_model = embedding_model
        if retriever_mode in {"embedding", "hybrid"}:
            self.embedder = embedder or SentenceTransformerEmbedder(embedding_model)
        else:
            self.embedder = None
        self.generator = EvidenceConstrainedGenerator()

    @staticmethod
    def _trace(state: AgentState, action: str, detail: dict[str, Any]) -> None:
        state.trace.append(
            {
                "step": len(state.trace) + 1,
                "action": action,
                "detail": detail,
            }
        )

    def run(
        self,
        profile_path: str | Path,
        jd_path: str | Path,
        output_dir: str | Path,
        simulate_unsafe_draft: bool = False,
        baseline_path: str | Path | None = None,
    ) -> dict[str, Any]:
        profile = load_yaml(profile_path)
        entities = parse_entities(profile)
        claims = claim_index(entities)
        evidence = parse_evidence(profile)
        safe_claims = eligible_claims(claims, evidence if evidence else None)
        entity_lookup = entity_by_claim(entities)
        jd_text = Path(jd_path).read_text(encoding="utf-8")
        baseline = load_yaml(baseline_path) if baseline_path else None
        state = AgentState()

        state.step = "parse_jd"
        state.requirements = parse_jd(jd_text)
        self._trace(
            state,
            "parse_jd",
            {
                "requirements": len(state.requirements),
                "stable_ids": [item.id for item in state.requirements],
                "types": {
                    kind: sum(item.kind == kind for item in state.requirements)
                    for kind in {"responsibility", "must_have", "nice_to_have"}
                },
            },
        )
        if not state.requirements:
            raise ValueError("No job requirements could be parsed from the JD.")

        state.step = "retrieve_evidence"
        state.matches = match_requirements(
            state.requirements,
            safe_claims,
            config=self.retrieval_config,
            embedder=self.embedder,
            unsupported_phrases=tuple(str(item) for item in profile.get("do_not_claim", [])),
        )
        self._trace(
            state,
            "retrieve_evidence",
            {
                "retrieval_mode": self.retrieval_config.mode,
                "embedding_model": self.embedding_model if self.embedder is not None else None,
                "eligible_claims": len(safe_claims),
                "strong": sum(item.match_level == "STRONG_MATCH" for item in state.matches),
                "partial": sum(item.match_level == "PARTIAL_MATCH" for item in state.matches),
                "gaps": sum(item.match_level == "GAP" for item in state.matches),
            },
        )

        state.step = "plan_claims"
        state.selected_claim_ids = select_claims(state.matches)
        self._trace(state, "plan_claims", {"selected_claim_ids": state.selected_claim_ids})

        state.step = "draft"
        state.bullets = self.generator.draft(
            state.selected_claim_ids,
            state.matches,
            claims,
            state.requirements,
        )
        if simulate_unsafe_draft and state.bullets:
            first = state.bullets[0]
            first_claim = claims[first.source_claim_ids[0]]
            unsafe_phrase = first_claim.do_not_claim[0] if first_claim.do_not_claim else "enterprise deployment"
            first.text = f"Led {unsafe_phrase} and increased revenue by 42%."
        self._trace(
            state,
            "draft",
            {
                "draft_bullets": len(state.bullets),
                "unsafe_demo_injected": simulate_unsafe_draft,
                "tailoring_mode": "authorized_paraphrase_selection",
            },
        )

        state.step = "audit"
        state.violations = audit_bullets(state.bullets, claims, evidence if evidence else None)
        self._trace(state, "audit", {"violations": state.violations})

        requirements = {item.id: item for item in state.requirements}
        while state.violations and state.revision_count < self.max_revisions:
            state.step = "revise"
            state.revision_count += 1
            by_location = violation_types_by_location(state.violations)
            revised: list[DraftBullet] = []
            actions: list[dict[str, Any]] = []
            for index, bullet in enumerate(state.bullets):
                location = f"bullet_{index+1:02d}"
                types = by_location.get(location)
                if not types:
                    revised.append(bullet)
                    continue
                replacement = revise_bullet_from_evidence(bullet, claims, requirements, types)
                if replacement is None:
                    actions.append({"location": location, "action": "removed_unrecoverable", "violations": sorted(types)})
                    continue
                revised.append(replacement)
                actions.append({"location": location, "action": "rewritten_from_evidence", "violations": sorted(types)})
            state.bullets = revised
            self._trace(
                state,
                "revise",
                {"revision": state.revision_count, "actions": actions},
            )
            state.violations = audit_bullets(state.bullets, claims, evidence if evidence else None)
            self._trace(state, "re_audit", {"violations": state.violations})

        state.step = "finalize"
        status = "passed" if not state.violations else "failed"
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        analysis = render_analysis(state.matches)
        candidate_name = str(profile.get("candidate", {}).get("name", "Fictional Candidate"))
        target_role = str(profile.get("target_role_label", "Target Role"))
        resume_md = render_resume_markdown(
            candidate_name=candidate_name,
            target_role=target_role,
            bullets=state.bullets,
            entity_lookup=entity_lookup,
        )
        resume_document = render_resume_document(
            candidate_name=candidate_name,
            target_role=target_role,
            bullets=state.bullets,
            entity_lookup=entity_lookup,
        )
        changes = build_change_log(state.bullets, baseline)
        audit = {
            "status": status,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "retrieval_mode": self.retrieval_config.mode,
            "embedding_model": self.embedding_model if self.embedder is not None else None,
            "selected_claim_count": len(state.selected_claim_ids),
            "final_bullet_count": len(state.bullets),
            "revision_count": state.revision_count,
            "violations": state.violations,
            "traceability": [asdict(item) for item in state.bullets],
            "gap_count": len(analysis["gaps"]),
            "baseline_used": baseline_path is not None,
            "change_summary": {
                status_name: sum(item["status"] == status_name for item in changes)
                for status_name in {"added", "rephrased", "unchanged", "not_selected"}
            },
        }

        write_yaml(output / "jd_analysis.yaml", analysis)
        write_yaml(output / "resume.yaml", resume_document)
        write_text(output / "resume.md", resume_md)
        write_json(output / "change_log.json", changes)
        write_json(output / "audit.json", audit)
        write_json(output / "run_trace.json", state.trace)
        return {
            "status": status,
            "analysis": analysis,
            "resume_markdown": resume_md,
            "resume": resume_document,
            "change_log": changes,
            "audit": audit,
            "trace": state.trace,
        }
