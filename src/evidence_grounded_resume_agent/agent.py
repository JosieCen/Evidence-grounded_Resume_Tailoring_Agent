from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .guardrails import audit_bullets, remove_invalid_bullets
from .io_utils import load_yaml, write_json, write_text, write_yaml
from .models import AgentState, DraftBullet
from .profile import claim_index, entity_by_claim, parse_entities
from .render import render_analysis, render_resume_markdown
from .retrieval import (
    DEFAULT_EMBEDDING_MODEL,
    RetrievalConfig,
    SentenceTransformerEmbedder,
    TextEmbedder,
    match_requirements,
)
from .tools import compose_bullets, eligible_claims, parse_jd, select_claims


class ResumeTailoringAgent:
    """A small tool-using agent with deterministic safety gates.

    Semantic retrieval proposes candidate evidence. Deterministic authorization
    still decides whether a claim is eligible to appear in the final output.
    """

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
    ) -> dict[str, Any]:
        profile = load_yaml(profile_path)
        entities = parse_entities(profile)
        claims = claim_index(entities)
        safe_claims = eligible_claims(claims)
        entity_lookup = entity_by_claim(entities)
        jd_text = Path(jd_path).read_text(encoding="utf-8")
        state = AgentState()

        state.step = "parse_jd"
        state.requirements = parse_jd(jd_text)
        self._trace(state, "parse_jd", {"requirements": len(state.requirements)})
        if not state.requirements:
            raise ValueError("No job requirements could be parsed from the JD.")

        state.step = "retrieve_evidence"
        state.matches = match_requirements(
            state.requirements,
            safe_claims,
            config=self.retrieval_config,
            embedder=self.embedder,
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
        state.bullets = compose_bullets(state.selected_claim_ids, state.matches, claims)
        if simulate_unsafe_draft:
            state.bullets.append(
                DraftBullet(
                    text="Led enterprise production deployment and increased revenue by 42%.",
                    source_claim_ids=[],
                    requirement_ids=[state.requirements[-1].id],
                    metric_ids=[],
                )
            )
        self._trace(
            state,
            "draft",
            {"draft_bullets": len(state.bullets), "unsafe_demo_injected": simulate_unsafe_draft},
        )

        state.step = "audit"
        state.violations = audit_bullets(state.bullets, claims)
        self._trace(state, "audit", {"violations": state.violations})

        while state.violations and state.revision_count < self.max_revisions:
            state.step = "revise"
            state.revision_count += 1
            before = len(state.bullets)
            state.bullets = remove_invalid_bullets(state.bullets, state.violations)
            self._trace(
                state,
                "revise",
                {"revision": state.revision_count, "removed": before - len(state.bullets)},
            )
            state.violations = audit_bullets(state.bullets, claims)
            self._trace(state, "re_audit", {"violations": state.violations})

        state.step = "finalize"
        status = "passed" if not state.violations else "failed"
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        analysis = render_analysis(state.matches)
        resume_md = render_resume_markdown(
            candidate_name=str(profile.get("candidate", {}).get("name", "Fictional Candidate")),
            target_role=str(profile.get("target_role_label", "Target Role")),
            bullets=state.bullets,
            entity_lookup=entity_lookup,
        )
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
        }

        write_yaml(output / "jd_analysis.yaml", analysis)
        write_text(output / "resume.md", resume_md)
        write_json(output / "audit.json", audit)
        write_json(output / "run_trace.json", state.trace)
        return {
            "status": status,
            "analysis": analysis,
            "resume_markdown": resume_md,
            "audit": audit,
            "trace": state.trace,
        }
