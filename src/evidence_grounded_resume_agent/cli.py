from __future__ import annotations

import argparse
import json

from .agent import ResumeTailoringAgent
from .evaluation import run_guardrail_evaluation
from .io_utils import load_yaml, write_json
from .retrieval import DEFAULT_EMBEDDING_MODEL, SentenceTransformerEmbedder
from .retrieval_evaluation import run_retrieval_benchmark


RETRIEVER_CHOICES = ("lexical", "embedding", "hybrid")


def _add_retrieval_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--retriever",
        choices=RETRIEVER_CHOICES,
        default="lexical",
        help="Evidence retrieval mode. Embedding/hybrid require the optional embedding dependency.",
    )
    parser.add_argument(
        "--embedding-model",
        default=DEFAULT_EMBEDDING_MODEL,
        help="Sentence Transformers model used by embedding/hybrid retrieval.",
    )


def _build_embedder(mode: str, model_name: str):
    if mode == "lexical":
        return None
    return SentenceTransformerEmbedder(model_name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evidence-grounded resume tailoring agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run the agent on a profile and JD")
    run.add_argument("--profile", required=True)
    run.add_argument("--jd", required=True)
    run.add_argument("--output", default="outputs/demo")
    _add_retrieval_args(run)
    run.add_argument(
        "--simulate-unsafe-draft",
        action="store_true",
        help="Inject one unsupported draft bullet to demonstrate the audit/revision loop.",
    )

    evaluate = subparsers.add_parser("evaluate", help="Run synthetic guardrail evaluation")
    evaluate.add_argument("--profile", default="examples/fictional_profile.yaml")
    evaluate.add_argument("--output", default="outputs/evaluation.json")

    benchmark = subparsers.add_parser(
        "benchmark-retrieval", help="Evaluate requirement-to-claim retrieval on a labeled fixture"
    )
    benchmark.add_argument("--profile", default="examples/fictional_profile.yaml")
    benchmark.add_argument("--benchmark", default="examples/retrieval_benchmark.yaml")
    benchmark.add_argument("--output", default="outputs/retrieval_benchmark.json")
    _add_retrieval_args(benchmark)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "run":
        result = ResumeTailoringAgent(
            retriever_mode=args.retriever,
            embedding_model=args.embedding_model,
        ).run(
            args.profile,
            args.jd,
            args.output,
            simulate_unsafe_draft=args.simulate_unsafe_draft,
        )
        print(json.dumps({"status": result["status"], "audit": result["audit"]}, indent=2))
        return 0 if result["status"] == "passed" else 1

    if args.command == "evaluate":
        profile = load_yaml(args.profile)
        report = run_guardrail_evaluation(profile)
        write_json(args.output, report)
        print(json.dumps(report, indent=2))
        return 0 if report["failed"] == 0 else 1

    profile = load_yaml(args.profile)
    benchmark = load_yaml(args.benchmark)
    report = run_retrieval_benchmark(
        profile,
        benchmark,
        retriever_mode=args.retriever,
        embedder=_build_embedder(args.retriever, args.embedding_model),
    )
    write_json(args.output, report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
