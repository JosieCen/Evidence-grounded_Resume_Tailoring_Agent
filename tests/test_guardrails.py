from evidence_grounded_resume_agent.guardrails import audit_bullets
from evidence_grounded_resume_agent.io_utils import load_yaml
from evidence_grounded_resume_agent.models import DraftBullet
from evidence_grounded_resume_agent.profile import claim_index, parse_entities, parse_evidence


def _profile():
    return load_yaml("examples/fictional_profile.yaml")


def _claims():
    return claim_index(parse_entities(_profile()))


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


def test_multi_source_metrics_are_a_union_not_checked_claim_by_claim() -> None:
    claims = _claims()
    a = claims["claim_llm_review_120"]
    b = claims["claim_clinician_interviews_8"]
    bullet = DraftBullet(
        f"{a.text} {b.text}",
        [a.id, b.id],
        [],
        ["metric_records_120", "metric_interviews_8"],
    )
    violations = audit_bullets([bullet], claims)
    assert not {item["type"] for item in violations}.intersection(
        {"untraceable_number", "metric_not_owned_by_source"}
    )


def test_evidence_reference_must_resolve_when_registry_is_present() -> None:
    profile = _profile()
    claims = _claims()
    evidence = parse_evidence(profile)
    claim = claims["claim_python_pipeline"]
    assert not audit_bullets([DraftBullet(claim.text, [claim.id], [], [])], claims, evidence)
