"""
Step 3: Resume Analysis View for Skill Gap AI
Runs the deterministic Resume Analysis Engine comparing extracted resume text
against target job description requirements. Stores results in session state
and enables progression to Step 4 (Skill Gap Report).
"""

import html
import textwrap
import streamlit as st

from components.stepper import render_stepper
from backend.workflow_state import can_access_analysis_step
from backend.resume_analyzer import analyze_resume_against_job
from backend.recommendation_service import generate_recommendations_for_analysis


def render_step3_analysis():
    """Renders Step 3: Analysis Execution and Input Verification."""
    # Pre-requisite checks
    has_valid_inputs = can_access_analysis_step(
        st.session_state.get("resume_uploaded", False),
        st.session_state.get("resume_text", ""),
        st.session_state.get("job_title", ""),
        st.session_state.get("job_description", ""),
    )

    if not has_valid_inputs:
        if not st.session_state.get("resume_uploaded", False) or not st.session_state.get("resume_text"):
            st.warning("⚠️ Access Restricted: Please upload a readable resume in Step 1 first.")
            if st.button("⬅️ Go to Step 1: Upload Resume"):
                st.session_state["workflow_step"] = 1
                st.rerun()
            return
        else:
            st.warning("⚠️ Access Restricted: Please provide a valid job description in Step 2 first.")
            if st.button("⬅️ Go to Step 2: Job Description"):
                st.session_state["workflow_step"] = 2
                st.rerun()
            return

    # Render Step 3 Progress Stepper
    render_stepper(3)

    # Automatic Analysis Execution when transitioned from Step 2 with pending flag
    if st.session_state.get("run_analysis_pending", False):
        st.session_state["run_analysis_pending"] = False
        with st.spinner("Extracting job requirements, evaluating resume evidence, and computing match score..."):
            try:
                analysis_result = analyze_resume_against_job(
                    resume_text=st.session_state["resume_text"],
                    job_description=st.session_state["job_description"],
                    job_title=st.session_state.get("job_title", ""),
                )
                if analysis_result.get("success", False):
                    st.session_state["analysis_result"] = analysis_result
                    st.session_state["analysis_completed"] = True
                    st.session_state.pop("analysis_error", None)

                    # Also pre-compute Stage 4 personalized recommendations
                    try:
                        rec_output = generate_recommendations_for_analysis(
                            analysis_result=analysis_result,
                            job_description=st.session_state["job_description"],
                            resume_text=st.session_state["resume_text"],
                            job_title=st.session_state.get("job_title", ""),
                        )
                        st.session_state["recommendations_data"] = rec_output
                    except Exception:
                        pass

                    st.session_state["workflow_step"] = 4
                    st.session_state["current_page"] = "Resume Analysis"
                    st.session_state["pending_page"] = "Resume Analysis"
                    st.toast("Resume analysis completed successfully!", icon="✅")
                    st.rerun()
                else:
                    st.session_state["analysis_error"] = analysis_result.get(
                        "error", "Unable to complete resume analysis."
                    )
                    st.session_state["analysis_completed"] = False
            except Exception as e:
                st.session_state["analysis_error"] = f"An unexpected error occurred during analysis: {str(e)}"
                st.session_state["analysis_completed"] = False

    st.markdown(
        textwrap.dedent(
            """
            <div style="margin-bottom: 1.5rem;">
                <h2 style="font-size: 1.75rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.35rem;">
                    Step 3: AI Resume Analysis Engine
                </h2>
                <p style="color: #94A3B8; font-size: 0.95rem;">
                    Execute the deterministic skill comparison engine to extract requirements, evaluate resume evidence, and compute alignment.
                </p>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )

    # If an error occurred, show helpful error banner with preserved inputs notice
    if st.session_state.get("analysis_error"):
        error_msg = html.escape(str(st.session_state["analysis_error"]))
        st.markdown(
            textwrap.dedent(
                f"""
                <div style="background: rgba(244, 63, 94, 0.15); border: 1px solid rgba(244, 63, 94, 0.45); border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;">
                    <div style="color: #FDA4AF; font-weight: 700; font-size: 0.95rem; margin-bottom: 4px;">
                        ⚠️ Analysis Execution Issue
                    </div>
                    <div style="color: #F8FAFC; font-size: 0.88rem; line-height: 1.5;">
                        {error_msg}
                    </div>
                    <div style="color: #CBD5E1; font-size: 0.8rem; margin-top: 8px;">
                        Your resume and job description inputs have been fully preserved below. You can retry the analysis or adjust your inputs.
                    </div>
                </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )
    else:
        # Input Verification Status Banner
        st.markdown(
            textwrap.dedent(
                """
                <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.5rem;">✅</span>
                    <div>
                        <div style="font-weight: 700; color: #34D399; font-size: 0.95rem;">Inputs Loaded & Verified</div>
                        <div style="color: #CBD5E1; font-size: 0.85rem; margin-top: 2px;">
                            Resume text and job description are loaded in-memory and ready for analysis.
                        </div>
                    </div>
                </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )

    # Side-by-side Summary Cards: Resume vs Job Description
    resume_name = st.session_state.get("resume_name", "Resume")
    resume_type = st.session_state.get("resume_type", "PDF")
    resume_size_kb = st.session_state.get("resume_size_kb", 0.0)
    resume_words = st.session_state.get("resume_word_count", 0)
    resume_chars = st.session_state.get("resume_char_count", 0)
    resume_text = st.session_state.get("resume_text", "")

    job_title = st.session_state.get("job_title", "Target Role")
    company_name = st.session_state.get("company_name", "Not specified")
    job_desc_text = st.session_state.get("job_description", "")
    job_words = len(job_desc_text.split()) if job_desc_text.strip() else 0
    job_chars = len(job_desc_text)

    clean_res_name = html.escape(resume_name)
    clean_res_type = html.escape(resume_type)
    clean_job_title = html.escape(job_title)
    clean_company = html.escape(company_name or "Not specified")

    col_res, col_job = st.columns(2)

    with col_res:
        st.markdown(
            textwrap.dedent(
                f"""
                <div class="glass-card" style="height: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                        <span style="font-size: 0.8rem; color: #A5B4FC; font-weight: 700; text-transform: uppercase;">1. Candidate Resume</span>
                        <span style="background: rgba(99, 102, 241, 0.2); color: #C7D2FE; font-size: 0.75rem; padding: 2px 8px; border-radius: 9999px; font-weight: 600;">{clean_res_type}</span>
                    </div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.5rem; word-break: break-all;">
                        📄 {clean_res_name}
                    </div>
                    <div style="font-size: 0.85rem; color: #94A3B8; line-height: 1.6;">
                        • <strong>File Size:</strong> {resume_size_kb} KB<br/>
                        • <strong>Extracted Length:</strong> <span style="color: #34D399; font-weight: 600;">{resume_words} words</span> ({resume_chars:,} characters)<br/>
                        • <strong>Status:</strong> Ready for Evaluation
                    </div>
                </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )

        with st.expander("👁️ View Extracted Resume Snippet", expanded=False):
            st.text_area(
                "Resume Text Preview",
                value=resume_text,
                height=150,
                disabled=True,
                label_visibility="collapsed",
            )

    with col_job:
        st.markdown(
            textwrap.dedent(
                f"""
                <div class="glass-card" style="height: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                        <span style="font-size: 0.8rem; color: #D8B4FE; font-weight: 700; text-transform: uppercase;">2. Target Job Requirements</span>
                        <span style="background: rgba(168, 85, 247, 0.2); color: #E9D5FF; font-size: 0.75rem; padding: 2px 8px; border-radius: 9999px; font-weight: 600;">Benchmark</span>
                    </div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.5rem;">
                        🎯 {clean_job_title}
                    </div>
                    <div style="font-size: 0.85rem; color: #94A3B8; line-height: 1.6;">
                        • <strong>Company / Org:</strong> {clean_company}<br/>
                        • <strong>Description Length:</strong> <span style="color: #38BDF8; font-weight: 600;">{job_words} words</span> ({job_chars:,} characters)<br/>
                        • <strong>Status:</strong> Validated Requirements
                    </div>
                </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )

        with st.expander("👁️ View Job Description Snippet", expanded=False):
            st.text_area(
                "Job Description Preview",
                value=job_desc_text,
                height=150,
                disabled=True,
                label_visibility="collapsed",
            )

    st.write("")

    # Analysis Execution Section
    has_analysis = (
        st.session_state.get("analysis_completed", False)
        and st.session_state.get("analysis_result") is not None
    )

    st.markdown(
        textwrap.dedent(
            """
            <div class="glass-card" style="border-color: rgba(168, 85, 247, 0.35);">
                <h3 style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.5rem;">
                    🚀 Execute Resume-to-Job Matching Engine
                </h3>
                <p style="font-size: 0.88rem; color: #94A3B8; margin-bottom: 1.25rem; line-height: 1.5;">
                    The analysis engine extracts technical competencies from the job requirements, scans your resume for 
                    verbatim context sentences, classifies each skill (Matching, Partial, Missing, or Needs Verification), 
                    and computes a transparent alignment score.
                </p>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )

    # Action Buttons: Run Analysis vs View Existing
    col_run1, col_run2 = st.columns([1, 1])

    with col_run1:
        btn_label = "⚡ Re-run Analysis" if has_analysis else "⚡ Run Resume Analysis"
        if st.button(btn_label, use_container_width=True, type="primary"):
            st.session_state["run_analysis_pending"] = True
            st.session_state.pop("analysis_error", None)
            st.rerun()

    with col_run2:
        if has_analysis:
            if st.button("View Skill Gap Report ➔", use_container_width=True, type="secondary"):
                st.session_state["workflow_step"] = 4
                st.session_state["current_page"] = "Resume Analysis"
                st.session_state["pending_page"] = "Resume Analysis"
                st.rerun()

    st.write("")
    st.write("")

    # Back Navigation
    if st.button("⬅️ Back to Job Description", use_container_width=False, type="secondary"):
        st.session_state["workflow_step"] = 2
        st.rerun()

