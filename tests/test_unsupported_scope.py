from evidence_grounded_resume_agent.models import Claim, Requirement
from evidence_grounded_resume_agent.retrieval import RetrievalConfig, match_requirements
from evidence_grounded_resume_agent.tools import tokenize


def test_known_unsupported_scope_forces_gap_before_similarity_matching() -> None:
    req = Requirement(
        "req_sales",
        "Own commercial revenue targets and negotiate contracts.",
        tokenize("Own commercial revenue targets and negotiate contracts."),
    )
    claim = Claim(
        "claim_product",
        "Translated user needs into product requirements.",
        ("e1",),
        tags=("product", "commercial"),
    )
    match = match_requirements(
        [req],
        {claim.id: claim},
        config=RetrievalConfig(mode="lexical"),
        unsupported_phrases=("commercial revenue",),
    )[0]
    assert match.match_level == "GAP"
    assert match.authorization_note
