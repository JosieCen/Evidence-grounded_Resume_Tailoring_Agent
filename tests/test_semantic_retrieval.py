from pathlib import Path

from evidence_grounded_resume_agent.io_utils import load_yaml
from evidence_grounded_resume_agent.models import Claim, Requirement
from evidence_grounded_resume_agent.retrieval import RetrievalConfig, match_requirements
from evidence_grounded_resume_agent.retrieval_evaluation import run_retrieval_benchmark
from evidence_grounded_resume_agent.tools import tokenize


ROOT = Path(__file__).resolve().parents[1]


class ConceptEmbedder:
    """Deterministic test double: validates retrieval logic without downloading a model."""

    def encode(self, texts):
        vectors = []
        for text in texts:
            folded = text.casefold()
            if "non-specialist" in folded or "structured presentations" in folded:
                vectors.append([1.0, 0.0, 0.0])
            elif "commercial contracts" in folded or "sales revenue" in folded:
                vectors.append([0.0, 0.0, 1.0])
            else:
                vectors.append([0.0, 1.0, 0.0])
        return vectors


def test_embedding_retrieval_recovers_semantic_match_without_lexical_overlap() -> None:
    requirement_text = "Explain complex technical findings clearly to non-specialist audiences."
    requirement = Requirement("req_01", requirement_text, tokenize(requirement_text))
    claims = {
        "communication": Claim(
            id="communication",
            text="Synthesized biomedical literature into structured presentations and concise evidence summaries.",
            evidence_refs=("evidence_1",),
            tags=("communication", "presentation"),
        ),
        "automation": Claim(
            id="automation",
            text="Built a Python workflow for deterministic data processing.",
            evidence_refs=("evidence_2",),
            tags=("python", "automation"),
        ),
    }

    lexical = match_requirements([requirement], claims, config=RetrievalConfig(mode="lexical"))
    semantic = match_requirements(
        [requirement],
        claims,
        config=RetrievalConfig(mode="embedding"),
        embedder=ConceptEmbedder(),
    )
    hybrid = match_requirements(
        [requirement],
        claims,
        config=RetrievalConfig(mode="hybrid"),
        embedder=ConceptEmbedder(),
    )

    assert lexical[0].match_level == "GAP"
    assert semantic[0].match_level == "STRONG_MATCH"
    assert semantic[0].source_claim_ids[0] == "communication"
    assert semantic[0].candidate_scores[0]["semantic_score"] == 1.0
    assert hybrid[0].match_level == "STRONG_MATCH"
    assert hybrid[0].source_claim_ids[0] == "communication"


def test_embedding_retrieval_preserves_unrelated_gap() -> None:
    requirement_text = "Own enterprise sales revenue targets and negotiate commercial contracts."
    requirement = Requirement("req_01", requirement_text, tokenize(requirement_text))
    claims = {
        "communication": Claim(
            id="communication",
            text="Synthesized biomedical literature into structured presentations and concise evidence summaries.",
            evidence_refs=("evidence_1",),
        )
    }
    result = match_requirements(
        [requirement],
        claims,
        config=RetrievalConfig(mode="embedding"),
        embedder=ConceptEmbedder(),
    )
    assert result[0].match_level == "GAP"
    assert result[0].source_claim_ids == []


def test_retrieval_benchmark_emits_machine_readable_metrics() -> None:
    report = run_retrieval_benchmark(
        load_yaml(ROOT / "examples" / "fictional_profile.yaml"),
        load_yaml(ROOT / "examples" / "retrieval_benchmark.yaml"),
        retriever_mode="lexical",
    )
    assert report["retriever_mode"] == "lexical"
    assert report["cases"] == 6
    assert 0.0 <= report["top1_accuracy"] <= 1.0
    assert 0.0 <= report["recall_at_3"] <= 1.0
    assert report["gap_accuracy"] in {0.0, 1.0}
