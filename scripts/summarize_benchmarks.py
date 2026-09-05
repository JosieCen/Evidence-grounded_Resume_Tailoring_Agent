from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lexical", required=True)
    parser.add_argument("--embedding", required=True)
    parser.add_argument("--hybrid", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    reports = {}
    for name, path in {
        "lexical": args.lexical,
        "embedding": args.embedding,
        "hybrid": args.hybrid,
    }.items():
        report = json.loads(Path(path).read_text(encoding="utf-8"))
        reports[name] = {
            key: report.get(key)
            for key in (
                "cases",
                "positive_cases",
                "gap_cases",
                "top1_accuracy",
                "recall_at_3",
                "gap_accuracy",
                "false_positive_rate_on_gaps",
                "forbidden_top1_rate",
                "overall_case_accuracy",
            )
        }
        reports[name]["by_category"] = report.get("by_category", {})

    output = {
        "meta": {
            "benchmark": "examples/retrieval_benchmark.yaml",
            "fixture_version": "0.3.0",
            "note": "Fictional retrieval fixture; metrics are not hiring outcomes.",
        },
        "retrievers": reports,
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
