from pathlib import Path

from evidence_grounded_resume_agent.agent import ResumeTailoringAgent


ROOT = Path(__file__).resolve().parents[1]


def test_end_to_end_outputs_are_traceable(tmp_path: Path) -> None:
    result = ResumeTailoringAgent().run(
        ROOT / "examples" / "fictional_profile.yaml",
        ROOT / "examples" / "fictional_jd.md",
        tmp_path,
    )
    assert result["status"] == "passed"
    assert result["audit"]["final_bullet_count"] > 0
    assert all(item["source_claim_ids"] for item in result["audit"]["traceability"])
    assert any(match["match_level"] == "GAP" for match in result["analysis"]["requirements"])
    assert (tmp_path / "resume.md").is_file()
    assert (tmp_path / "audit.json").is_file()
    assert (tmp_path / "run_trace.json").is_file()


def test_agent_revises_an_unsupported_draft(tmp_path: Path) -> None:
    result = ResumeTailoringAgent().run(
        ROOT / "examples" / "fictional_profile.yaml",
        ROOT / "examples" / "fictional_jd.md",
        tmp_path,
        simulate_unsafe_draft=True,
    )
    assert result["status"] == "passed"
    assert result["audit"]["revision_count"] == 1
    assert "42%" not in result["resume_markdown"]
    assert any(step["action"] == "revise" for step in result["trace"])
