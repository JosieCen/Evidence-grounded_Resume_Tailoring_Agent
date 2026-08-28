from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import ResumeTailoringAgent
from .evaluation import run_guardrail_evaluation
from .io_utils import load_yaml, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evidence-grounded resume tailoring agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run the agent on a profile and JD")
    run.add_argument("--profile", required=True)
    run.add_argument("--jd", required=True)
    run.add_argument("--output", default="outputs/demo")
    run.add_argument(
        "--simulate-unsafe-draft",
        action="store_true",
        help="Inject one unsupported draft bullet to demonstrate the audit/revision loop.",
    )

    evaluate = subparsers.add_parser("evaluate", help="Run synthetic guardrail evaluation")
    evaluate.add_argument("--profile", default="examples/fictional_profile.yaml")
    evaluate.add_argument("--output", default="outputs/evaluation.json")

    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "run":
        result = ResumeTailoringAgent().run(
            args.profile, args.jd, args.output, simulate_unsafe_draft=args.simulate_unsafe_draft
        )
        print(json.dumps({"status": result["status"], "audit": result["audit"]}, indent=2))
        return 0 if result["status"] == "passed" else 1

    profile = load_yaml(args.profile)
    report = run_guardrail_evaluation(profile)
    write_json(args.output, report)
    print(json.dumps(report, indent=2))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
