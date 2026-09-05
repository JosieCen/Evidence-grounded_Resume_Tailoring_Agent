from evidence_grounded_resume_agent.generation import EvidenceConstrainedGenerator
from evidence_grounded_resume_agent.models import Claim, Match, Requirement
from evidence_grounded_resume_agent.tools import tokenize


def test_generator_selects_authorized_jd_aligned_paraphrase() -> None:
    claim = Claim(
        id="claim_x",
        text="Synthesized biomedical literature into structured presentations.",
        evidence_refs=("e1",),
        tags=("communication",),
        paraphrases=("Explained complex biomedical evidence clearly to cross-functional stakeholders.",),
    )
    req = Requirement(
        id="req_x",
        text="Communicate complex biomedical evidence to cross-functional stakeholders.",
        tokens=tokenize("Communicate complex biomedical evidence to cross-functional stakeholders."),
    )
    match = Match(
        requirement_id=req.id,
        requirement_text=req.text,
        match_level="STRONG_MATCH",
        source_claim_ids=[claim.id],
        requirement_kind=req.kind,
        requirement_priority=req.priority,
    )
    bullet = EvidenceConstrainedGenerator().draft([claim.id], [match], {claim.id: claim}, [req])[0]
    assert bullet.text == claim.paraphrases[0]
    assert bullet.source_claim_ids == [claim.id]
