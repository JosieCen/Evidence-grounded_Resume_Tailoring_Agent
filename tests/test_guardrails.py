from evidence_grounded_resume_agent.guardrails import audit_bullets
from evidence_grounded_resume_agent.models import DraftBullet
from evidence_grounded_resume_agent.profile import claim_index, parse_entities
from evidence_grounded_resume_agent.io_utils import load_yaml


def _claims():
    profile = load_yaml("examples/fictional_profile.yaml")
    return claim_index(parse_entities(profile))


def test_missing_source_is_blocked() -> None:
    violations = audit_bullets([DraftBullet("Unsafe generated claim", [], [], [])], _claims())
    assert "missing_source" in {item["type"] for item in violations}


def test_unverified_claim_is_blocked() -> None:
    claims = _claims()
    claim = claims["claim_unverified_revenue"]
    violations = audit_bullets([DraftBullet(claim.text, [claim.id], [], [])], claims)
    assert "unverified_claim" in {item["type"] for item in violations}


def test_hidden_claim_is_blocked() -> None:
    claims = _claims()
    claim = claims["claim_private_draft"]
    violations = audit_bullets([DraftBullet(claim.text, [claim.id], [], [])], claims)
    assert "hidden_claim" in {item["type"] for item in violations}


def test_untraceable_number_is_blocked() -> None:
    claims = _claims()
    claim = claims["claim_llm_review_120"]
    text = claim.text + " Increased performance by 99%."
    violations = audit_bullets([DraftBullet(text, [claim.id], [], [])], claims)
    assert "untraceable_number" in {item["type"] for item in violations}
