from __future__ import annotations

from pathlib import Path
import tempfile

import streamlit as st

from evidence_grounded_resume_agent.agent import ResumeTailoringAgent
from evidence_grounded_resume_agent.retrieval import DEFAULT_EMBEDDING_MODEL


st.set_page_config(page_title="Evidence-Grounded Resume Agent", layout="wide")
st.title("Evidence-Grounded Resume Tailoring Agent")
st.caption(
    "v0.3 — structured JD analysis, multilingual retrieval, evidence-constrained rewriting, "
    "deterministic safety gates, and baseline-aware change review."
)

root = Path(__file__).parent
profile_path = root / "examples" / "fictional_profile.yaml"
baseline_path = root / "examples" / "fictional_baseline_resume.yaml"
default_jd = (root / "examples" / "fictional_jd.md").read_text(encoding="utf-8")

controls = st.columns([1, 2, 1])
with controls[0]:
    retriever = st.selectbox("Retriever", ["lexical", "hybrid", "embedding"], index=0)
with controls[1]:
    embedding_model = st.text_input("Embedding model", value=DEFAULT_EMBEDDING_MODEL)
with controls[2]:
    use_baseline = st.checkbox("Compare with baseline", value=True)

if retriever != "lexical":
    st.info('Embedding/hybrid mode requires: pip install -e ".[embedding,ui]"')

jd_text = st.text_area("Job description", value=default_jd, height=320)

if st.button("Run agent", type="primary"):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        jd_path = temp / "jd.md"
        jd_path.write_text(jd_text, encoding="utf-8")
        try:
            result = ResumeTailoringAgent(
                retriever_mode=retriever,
                embedding_model=embedding_model,
            ).run(
                profile_path,
                jd_path,
                temp / "output",
                baseline_path=baseline_path if use_baseline else None,
            )
        except (RuntimeError, ValueError) as exc:
            st.error(str(exc))
        else:
            status = result["audit"]["status"]
            if status == "passed":
                st.success(
                    f"Safety audit passed · {result['audit']['gap_count']} explicit gap(s) · "
                    f"{result['audit']['revision_count']} revision cycle(s)"
                )
            else:
                st.error("Safety audit failed. Inspect unresolved violations below.")

            left, right = st.columns([1, 1])
            with left:
                st.subheader("JD evidence map")
                for item in result["analysis"]["requirements"]:
                    label = (
                        f"{item['match_level']} · {item['kind']} · {item['priority']} — "
                        f"{item['text']}"
                    )
                    st.markdown(f"**{label}**")
                    if item.get("authorization_note"):
                        st.caption(item["authorization_note"])
                    else:
                        st.caption(
                            f"Retriever: `{item['retrieval_mode']}` · score: `{item['top_score']:.3f}` · "
                            f"Sources: {', '.join(item['source_claim_ids']) or 'None'}"
                        )
                    if item["candidate_scores"]:
                        with st.expander("Retrieval scores"):
                            st.json(item["candidate_scores"])

            with right:
                st.subheader("Tailored output")
                st.markdown(result["resume_markdown"])

                if use_baseline:
                    st.subheader("Before / after review")
                    for change in result["change_log"]:
                        if change["status"] == "not_selected":
                            continue
                        with st.expander(
                            f"{change['status'].upper()} · {change['claim_id']}",
                            expanded=change["status"] == "rephrased",
                        ):
                            st.markdown("**Before**")
                            st.write(change["before"] or "—")
                            st.markdown("**After**")
                            st.write(change["after"] or "—")
                            st.caption(change["reason"] or "")
                            if change["revision_notes"]:
                                st.caption("Revision: " + " | ".join(change["revision_notes"]))

                st.subheader("Safety audit")
                st.json(
                    {
                        "status": result["audit"]["status"],
                        "violations": result["audit"]["violations"],
                        "change_summary": result["audit"]["change_summary"],
                    }
                )

            with st.expander("Full run trace"):
                st.json(result["trace"])
