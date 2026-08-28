from pathlib import Path

from evidence_grounded_resume_agent.evaluation import run_guardrail_evaluation
from evidence_grounded_resume_agent.io_utils import load_yaml, write_json


ROOT = Path(__file__).resolve().parents[1]
profile = load_yaml(ROOT / "examples" / "fictional_profile.yaml")
report = run_guardrail_evaluation(profile)
write_json(ROOT / "outputs" / "evaluation.json", report)
print(f"cases={report['cases']} passed={report['passed']} failed={report['failed']}")
