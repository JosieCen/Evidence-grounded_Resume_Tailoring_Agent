from pathlib import Path

from evidence_grounded_resume_agent.agent import ResumeTailoringAgent


ROOT = Path(__file__).resolve().parents[1]


def test_end_to_end_outputs_are_traceable(tmp_path: Path) -> None:
    result = ResumeTailoringAgent().run(
        ROOT / "examples" / "fictional_profile.yaml",
        ROOT / "examples" / "fictional_jd.md",
        tmp_path,
        baseline_path=ROOT / "examples" / "fictional_baseline_resume.yaml",
    )
    assert result["status"] == "passed"
    assert result["audit"]["final_bullet_count"] > 0
    assert all(item["source_claim_ids"] for item in result["audit"]["traceability"])
    assert any(match["match_level"] == "GAP" for match in result["analysis"]["requirements"])
    assert any(item["status"] == "rephrased" for item in result["change_log"])
    for filename in ("resume.md", "resume.yaml", "audit.json", "change_log.json", "run_trace.json"):
        assert (tmp_path / filename).is_file()


def test_agent_rewrites_unsafe_sourced_draft_instead_of_only_deleting(tmp_path: Path) -> None:
    result = ResumeTailoringAgent().run(
        ROOT / "examples" / "fictional_profile.yaml",
        ROOT / "examples" / "fictional_jd.md",
        tmp_path,
        simulate_unsafe_draft=True,
    )
    assert result["status"] == "passed"
    assert result["audit"]["revision_count"] == 1
    assert "42%" not in result["resume_markdown"]
    revise_steps = [step for step in result["trace"] if step["action"] == "revise"]
    assert revise_steps
    assert any(
        action["action"] == "rewritten_from_evidence"
        for action in revise_steps[0]["detail"]["actions"]
    )
