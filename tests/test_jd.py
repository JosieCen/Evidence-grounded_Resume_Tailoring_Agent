from evidence_grounded_resume_agent.jd import parse_jd


def test_structured_jd_parser_assigns_type_priority_and_stable_ids() -> None:
    text = """# Role
## Responsibilities
- Translate clinical needs into product requirements.
## Requirements
- Use Python for analysis automation.
## Preferred
- Experience with enterprise deployment.
"""
    first = parse_jd(text)
    second = parse_jd("# unrelated title change\n" + "\n".join(text.splitlines()[1:]))
    assert [item.id for item in first] == [item.id for item in second]
    assert [item.kind for item in first] == ["responsibility", "must_have", "nice_to_have"]
    assert [item.priority for item in first] == ["high", "high", "medium"]
