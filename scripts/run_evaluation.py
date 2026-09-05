import json
from pathlib import Path

from evidence_grounded_resume_agent.evaluation import run_guardrail_evaluation
from evidence_grounded_resume_agent.io_utils import load_yaml


ROOT = Path(__file__).resolve().parents[1]
report = run_guardrail_evaluation(load_yaml(ROOT / "examples" / "fictional_profile.yaml"))
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["failed"] == 0 else 1)
