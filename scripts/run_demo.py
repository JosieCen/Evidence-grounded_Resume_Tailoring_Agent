from pathlib import Path

from evidence_grounded_resume_agent.agent import ResumeTailoringAgent


ROOT = Path(__file__).resolve().parents[1]

ResumeTailoringAgent().run(
    ROOT / "examples" / "fictional_profile.yaml",
    ROOT / "examples" / "fictional_jd.md",
    ROOT / "outputs" / "demo",
    baseline_path=ROOT / "examples" / "fictional_baseline_resume.yaml",
)
