from evidence_grounded_resume_agent.evaluation import run_guardrail_evaluation
from evidence_grounded_resume_agent.io_utils import load_yaml


def test_synthetic_guardrail_suite_passes() -> None:
    report = run_guardrail_evaluation(load_yaml("examples/fictional_profile.yaml"))
    assert report["cases"] >= 6
    assert report["failed"] == 0
    assert report["pass_rate"] == 1.0
