from evidence_grounded_resume_agent.io_utils import load_yaml
from evidence_grounded_resume_agent.retrieval_evaluation import run_retrieval_benchmark


def test_public_benchmark_has_at_least_sixty_labeled_cases() -> None:
    benchmark = load_yaml("examples/retrieval_benchmark.yaml")
    assert len(benchmark["cases"]) >= 60
    categories = {item["category"] for item in benchmark["cases"]}
    assert {
        "semantic_transfer",
        "bilingual_zh",
        "explicit_gap",
        "overclaim_trap",
        "seniority_hard_negative",
        "numeric_provenance",
    }.issubset(categories)


def test_lexical_benchmark_returns_category_and_safety_metrics() -> None:
    profile = load_yaml("examples/fictional_profile.yaml")
    benchmark = load_yaml("examples/retrieval_benchmark.yaml")
    report = run_retrieval_benchmark(profile, benchmark, retriever_mode="lexical")
    assert report["cases"] >= 60
    assert report["positive_cases"] > 0
    assert report["gap_cases"] > 0
    assert "false_positive_rate_on_gaps" in report
    assert "forbidden_top1_rate" in report
    assert report["by_category"]["semantic_transfer"]["cases"] == 12
