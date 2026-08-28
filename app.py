from __future__ import annotations

from pathlib import Path
import tempfile

import streamlit as st

from evidence_grounded_resume_agent.agent import ResumeTailoringAgent
from evidence_grounded_resume_agent.retrieval import DEFAULT_EMBEDDING_MODEL


st.set_page_config(page_title="Evidence-Grounded Resume Agent", layout="wide")
st.title("Evidence-Grounded Resume Tailoring Agent")
st.caption("v0.2 — privacy-safe showcase with pluggable semantic retrieval and deterministic safety gates.")

root = Path(__file__).parent
profile_path = root / "examples" / "fictional_profile.yaml"
default_jd = (root / "examples" / "fictional_jd.md").read_text(encoding="utf-8")

left_controls, right_controls = st.columns([1, 2])
with left_controls:
    retriever = st.selectbox("Retriever", ["lexical", "hybrid", "embedding"], index=0)
with right_controls:
    embedding_model = st.text_input("Embedding model", value=DEFAULT_EMBEDDING_MODEL)

if retriever != "lexical":
    st.info('Embedding/hybrid mode requires: pip install -e ".[embedding,ui]"')

jd_text = st.text_area("Job description", value=default_jd, height=280)

if st.button("Run agent", type="primary"):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        jd_path = temp / "jd.md"
        jd_path.write_text(jd_text, encoding="utf-8")
        try:
            result = ResumeTailoringAgent(
                retriever_mode=retriever,
                embedding_model=embedding_model,
            ).run(profile_path, jd_path, temp / "output")
        except RuntimeError as exc:
            st.error(str(exc))
        else:
            left, right = st.columns([1, 1])
            with left:
                st.subheader("JD evidence map")
                for item in result["analysis"]["requirements"]:
                    st.markdown(
                        f"**{item['match_level']}** — {item['text']}  \n"
                        f"Retriever: `{item['retrieval_mode']}` · score: `{item['top_score']:.3f}`"
                    )
                    st.caption("Sources: " + (", ".join(item["source_claim_ids"]) or "None"))
                    if item["candidate_scores"]:
                        with st.expander("Retrieval scores"):
                            st.json(item["candidate_scores"])
            with right:
                st.subheader("Tailored output")
                st.markdown(result["resume_markdown"])
                st.subheader("Audit")
                st.json(result["audit"])
