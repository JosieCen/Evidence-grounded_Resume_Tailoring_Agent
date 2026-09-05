from __future__ import annotations

import hashlib
import re

from .models import Requirement
from .tools import normalize_text, tokenize


SECTION_HINTS = {
    "must_have": {
        "requirements", "required", "qualifications", "must have", "what you bring",
        "任职资格", "岗位要求", "基本要求", "必备条件",
    },
    "nice_to_have": {
        "preferred", "nice to have", "bonus", "preferred qualifications",
        "加分项", "优先", "优先条件",
    },
    "responsibility": {
        "responsibilities", "what you will do", "role responsibilities", "duties",
        "工作职责", "岗位职责", "主要职责", "工作内容",
    },
}


def stable_requirement_id(text: str) -> str:
    normalized = normalize_text(text)
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:10]
    return f"req_{digest}"


def _classify_heading(heading: str) -> str | None:
    normalized = normalize_text(re.sub(r"^#+\s*", "", heading))
    for kind, phrases in SECTION_HINTS.items():
        if any(phrase in normalized for phrase in phrases):
            return kind
    return None


def _priority(kind: str) -> str:
    return "medium" if kind == "nice_to_have" else "high"


def _split_candidate_text(raw_line: str) -> list[str]:
    line = re.sub(r"^\s*(?:[-*•]|(?:\d+|[A-Za-z])[.)])\s*", "", raw_line).strip()
    if not line:
        return []
    parts = re.split(r"(?<=[.!?。！？])\s+(?=[A-Z\u4e00-\u9fff])", line)
    return [part.strip() for part in parts if len(part.strip()) >= 12]


def parse_jd(jd_text: str) -> list[Requirement]:
    requirements: list[Requirement] = []
    current_kind = "responsibility"
    current_section = ""

    for raw_line in jd_text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            heading_kind = _classify_heading(stripped)
            if heading_kind:
                current_kind = heading_kind
                current_section = re.sub(r"^#+\s*", "", stripped).strip()
            continue

        is_bullet = bool(re.match(r"^\s*(?:[-*•]|(?:\d+|[A-Za-z])[.)])\s+", raw_line))
        if not is_bullet and len(stripped) < 24:
            heading_kind = _classify_heading(stripped.rstrip(":："))
            if heading_kind:
                current_kind = heading_kind
                current_section = stripped.rstrip(":：")
                continue

        for text in _split_candidate_text(raw_line):
            requirement = Requirement(
                id=stable_requirement_id(text),
                text=text,
                tokens=tokenize(text),
                kind=current_kind,
                priority=_priority(current_kind),
                section=current_section,
            )
            if all(existing.id != requirement.id for existing in requirements):
                requirements.append(requirement)

    return requirements[:40]
