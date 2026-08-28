from __future__ import annotations

from pathlib import Path
import tempfile

import streamlit as st

from evidence_grounded_resume_agent.agent import ResumeTailoringAgent


st.set_page_config(page_title="Evidence-Grounded Resume Agent", layout="wide")
st.title("Evidence-Grounded Resume Tailoring Agent")
st.caption("Privacy-safe showcase using fictional profile data and deterministic safety gates.")

root = Path(__file__).parent
profile_path = root / "examples" / "fictional_profile.yaml"
default_jd = (root / "examples" / "fictional_jd.md").read_text(encoding="utf-8")

jd_text = st.text_area("Job description", value=default_jd, height=280)

if st.button("Run agent", type="primary"):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        jd_path = temp / "jd.md"
        jd_path.write_text(jd_text, encoding="utf-8")
        result = ResumeTailoringAgent().run(profile_path, jd_path, temp / "output")

        left, right = st.columns([1, 1])
        with left:
            st.subheader("JD evidence map")
            for item in result["analysis"]["requirements"]:
                st.markdown(f"**{item['match_level']}** — {item['text']}")
                st.caption("Sources: " + (", ".join(item["source_claim_ids"]) or "None"))
        with right:
            st.subheader("Tailored output")
            st.markdown(result["resume_markdown"])
            st.subheader("Audit")
            st.json(result["audit"])
