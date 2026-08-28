from pathlib import Path

from evidence_grounded_resume_agent.agent import ResumeTailoringAgent


ROOT = Path(__file__).resolve().parents[1]
result = ResumeTailoringAgent().run(
    ROOT / "examples" / "fictional_profile.yaml",
    ROOT / "examples" / "fictional_jd.md",
    ROOT / "outputs" / "demo",
)
print(f"status={result['status']} bullets={result['audit']['final_bullet_count']}")
