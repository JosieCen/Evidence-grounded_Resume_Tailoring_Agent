from evidence_grounded_resume_agent.models import Claim, Requirement
from evidence_grounded_resume_agent.retrieval import RetrievalConfig, match_requirements


class FakeEmbedder:
    def encode(self, texts):
        vectors = []
        for text in texts:
            lower = text.lower()
            if "non-specialist" in lower or "structured presentations" in lower:
                vectors.append([1.0, 0.0, 0.0])
            elif "commercial revenue" in lower:
                vectors.append([0.0, 1.0, 0.0])
            else:
                vectors.append([0.0, 0.0, 1.0])
        return vectors


def test_embedding_can_recover_semantic_transfer_without_authorizing_gap() -> None:
    reqs = [
        Requirement("req_comm", "Explain complex technical findings clearly to non-specialist audiences.", ()),
        Requirement("req_sales", "Own commercial revenue targets.", ()),
    ]
    claims = {
        "claim_comm": Claim(
            "claim_comm",
            "Synthesized biomedical literature into structured presentations.",
            ("e1",),
            tags=("communication",),
        )
    }
    matches = match_requirements(
        reqs,
        claims,
        config=RetrievalConfig(mode="embedding", min_semantic_score=0.5, strong_semantic_score=0.8),
        embedder=FakeEmbedder(),
    )
    assert matches[0].source_claim_ids == ["claim_comm"]
    assert matches[1].match_level == "GAP"
