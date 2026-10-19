"""
Step 4: Skill Gap Report View for Skill Gap AI
Renders the real, evidence-backed compatibility report derived from the Resume Analysis Engine
and the Personalized Recommendation Service (Stage 4).
Displays score, categorized skills with verbatim resume quotes, priority labels,
individual skill-gap recommendation cards, and a prioritized learning roadmap.
"""

import html
import textwrap
import streamlit as st

from components.stepper import render_stepper
from backend.resume_analyzer import analyze_resume_against_job
from backend.recommendation_service import generate_recommendations_for_analysis

# Demonstration fallback dataset if user directly previews report without analyzing
DEMO_RESUME_SNIPPET = """Taylor Swift - Senior Full Stack Developer.
Skills: Python, FastAPI, React, PostgreSQL, Docker, Git.
5+ years experience building web applications and REST APIs."""

DEMO_JOB_SNIPPET = """Role: Senior Full-Stack Engineer
Required: 4+ years of Python, React, PostgreSQL, and Kubernetes.
Nice to have: GraphQL, Redis, and automated testing."""


def render_step4_report():
    """Renders Step 4: Real Skill Gap Report with Personalized Stage 4 Recommendations."""
    render_stepper(4)

    analysis_data = st.session_state.get("analysis_result")
    is_real_analysis = analysis_data is not None and analysis_data.get("success", False)

    st.markdown(
        textwrap.dedent(
            """
            <div style="margin-bottom: 1.5rem;">
                <h2 style="font-size: 1.75rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.35rem;">
                    Step 4: Skill Gap Report & Personalized Recommendations
                </h2>
                <p style="color: #94A3B8; font-size: 0.95rem;">
                    Evidence-grounded compatibility metrics, prioritized skill gaps, and custom action plans tailored to your target position.
                </p>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )

    # If no analysis has been executed yet, provide friendly prompt or demo loader
    if not is_real_analysis:
        st.markdown(
            textwrap.dedent(
                """
                <div class="glass-card" style="padding: 2rem; text-align: center;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
                    <h3 style="color: #F8FAFC; font-size: 1.3rem; margin-bottom: 0.5rem;">
                        No Resume Analysis Data Available Yet
                    </h3>
                    <p style="color: #94A3B8; font-size: 0.92rem; max-width: 600px; margin: 0 auto 1.5rem auto;">
                        To generate a personalized, evidence-based skill gap report and learning roadmap, 
                        please upload your resume and enter your target job description.
                    </p>
                </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )

        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("🚀 Start Resume Analysis Workflow", use_container_width=True, type="primary"):
                st.session_state["workflow_step"] = 1
                st.session_state["current_page"] = "Resume Analysis"
                st.rerun()

        with col_act2:
            if st.button("📋 Load Sample Demo Analysis", use_container_width=True, type="secondary"):
                # Run deterministic analysis on demo profile
                demo_analysis = analyze_resume_against_job(
                    DEMO_RESUME_SNIPPET,
                    DEMO_JOB_SNIPPET,
                    job_title="Senior Full-Stack Engineer",
                )
                st.session_state["analysis_result"] = demo_analysis
                st.session_state["analysis_completed"] = True
                st.session_state["job_title"] = "Senior Full-Stack Engineer"
                st.session_state["company_name"] = "CloudScale Tech (Sample)"
                st.session_state["resume_name"] = "Sample_Candidate_Profile.pdf"
                st.toast("Loaded sample analysis report!", icon="📊")
                st.rerun()
        return

    # Extract real analysis data
    scoring = analysis_data["scoring"]
    score_display = scoring.get("display_score", 0)
    score_percentage = scoring.get("score_percentage", 0.0)
    formula_explanation = scoring.get("formula_explanation", "")
    disclaimer = scoring.get("disclaimer", "")

    matching_skills = analysis_data.get("matching_skills", [])
    partial_skills = analysis_data.get("partial_skills", [])
    missing_skills = analysis_data.get("missing_skills", [])
    needs_verification_skills = analysis_data.get("needs_verification_skills", [])
    exp_insights = analysis_data.get("experience_insights", [])

    job_title = st.session_state.get("job_title", "Target Role")
    company_name = st.session_state.get("company_name", "")
    resume_name = st.session_state.get("resume_name", "Uploaded Resume")
    job_display = f"{job_title} ({company_name})" if company_name else job_title

    # Generate or reuse Stage 4 Personalized Recommendations
    rec_service_output = st.session_state.get("recommendations_data")
    if not rec_service_output or not rec_service_output.get("success", False):
        resume_text = st.session_state.get("resume_text", "")
        job_desc_text = st.session_state.get("job_description", "")
        rec_service_output = generate_recommendations_for_analysis(
            analysis_result=analysis_data,
            job_description=job_desc_text,
            resume_text=resume_text,
            job_title=job_title,
        )
        st.session_state["recommendations_data"] = rec_service_output

    detailed_recommendations = rec_service_output.get("recommendations", [])
    learning_plan = rec_service_output.get("learning_plan", {})
    top_skills_to_improve = learning_plan.get("top_skills_to_improve", [])

    clean_resume_name = html.escape(resume_name)
    clean_job_display = html.escape(job_display)

    # Context Header
    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.markdown(
            textwrap.dedent(
                f"""
                <div class="glass-card" style="padding: 1rem 1.25rem;">
                    <div style="font-size: 0.78rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Candidate Resume</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC;">📄 {clean_resume_name}</div>
                </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )
    with col_meta2:
        st.markdown(
            textwrap.dedent(
                f"""
                <div class="glass-card" style="padding: 1rem 1.25rem;">
                    <div style="font-size: 0.78rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Benchmark Target Position</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #818CF8;">🎯 {clean_job_display}</div>
                </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )

    # Score Card and Summary Metrics Row
    col_score, col_stats = st.columns([1.2, 2.8])

    with col_score:
        score_status = (
            "● Exceptional Match" if score_display >= 80
            else ("● Strong Alignment" if score_display >= 60
            else ("● Moderate Match" if score_display >= 40
            else "● Significant Gaps Identified"))
        )
        score_color = (
            "#34D399" if score_display >= 80
            else ("#818CF8" if score_display >= 60
            else ("#FBBF24" if score_display >= 40
            else "#FB7185"))
        )

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="score-card">
                    <div class="score-label">WEIGHTED MATCH SCORE</div>
                    <div class="score-number">{score_display}<span style="font-size: 1.8rem; font-weight: 500; color: #94A3B8;">%</span></div>
                    <div style="font-size: 0.82rem; color: {score_color}; font-weight: 600; margin-top: 4px;">
                        {score_status}
                    </div>
                </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )

    with col_stats:
        total_reqs = scoring.get("total_requirements", len(matching_skills) + len(partial_skills) + len(missing_skills) + len(needs_verification_skills))
        st.markdown(
            textwrap.dedent(
                f"""
                <div class="glass-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                        <span style="font-size: 0.85rem; font-weight: 700; color: #CBD5E1;">AUDIT BREAKDOWN</span>
                        <span style="font-size: 0.75rem; color: #94A3B8;">{total_reqs} Requirements Evaluated</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem;">
                        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 10px; text-align: center;">
                            <div style="font-size: 1.6rem; font-weight: 800; color: #34D399;">{len(matching_skills)}</div>
                            <div style="font-size: 0.72rem; color: #A7F3D0; font-weight: 600;">Matching (100%)</div>
                        </div>
                        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 10px; padding: 10px; text-align: center;">
                            <div style="font-size: 1.6rem; font-weight: 800; color: #FBBF24;">{len(partial_skills)}</div>
                            <div style="font-size: 0.72rem; color: #FDE68A; font-weight: 600;">Partial (50%)</div>
                        </div>
                        <div style="background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 10px; padding: 10px; text-align: center;">
                            <div style="font-size: 1.6rem; font-weight: 800; color: #FB7185;">{len(missing_skills)}</div>
                            <div style="font-size: 0.72rem; color: #FECDD3; font-weight: 600;">Missing (0%)</div>
                        </div>
                        <div style="background: rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.3); border-radius: 10px; padding: 10px; text-align: center;">
                            <div style="font-size: 1.6rem; font-weight: 800; color: #38BDF8;">{len(needs_verification_skills)}</div>
                            <div style="font-size: 0.72rem; color: #BAE6FD; font-weight: 600;">Review (30%)</div>
                        </div>
                    </div>
                    <div style="margin-top: 0.75rem; font-size: 0.76rem; color: #94A3B8; line-height: 1.4;">
                        ℹ️ <em>{html.escape(formula_explanation)}</em>
                    </div>
                </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )

    st.write("")

    # =========================================================================
    # STAGE 4: PERSONALIZED LEARNING ROADMAP & TOP SKILLS HIGHLIGHT
    # =========================================================================
    if top_skills_to_improve:
        st.markdown(
            textwrap.dedent(
                """
                <div style="margin: 1.5rem 0 0.75rem 0;">
                    <div class="hero-badge" style="margin-bottom: 0.5rem;">
                        <span>🎯 Stage 4: Personalized Learning Roadmap</span>
                    </div>
                    <h3 style="font-size: 1.35rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.35rem;">
                        Targeted Upskilling Priorities
                    </h3>
                    <p style="color: #94A3B8; font-size: 0.88rem;">
                        Prioritized based on job description emphasis, prerequisite hierarchy, and highest ROI to improve match score.
                    </p>
                </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )

        # Highlight Top 3 Skills to Improve First
        top_recs = learning_plan.get("top_recommendations", [])
        top_cols = st.columns(len(top_recs))

        for idx, (col, r) in enumerate(zip(top_cols, top_recs), start=1):
            with col:
                p_color = "#FB7185" if r["priority"] == "High" else ("#FBBF24" if r["priority"] == "Medium" else "#38BDF8")
                p_bg = "rgba(244, 63, 94, 0.15)" if r["priority"] == "High" else ("rgba(245, 158, 11, 0.15)" if r["priority"] == "Medium" else "rgba(14, 165, 233, 0.15)")
                s_icon = "~" if r["status"] == "Partial" else ("✕" if r["status"] == "Missing" else "🔍")

                clean_skill_name = html.escape(r["skill_name"])
                clean_status = html.escape(r["status"])
                clean_category = html.escape(r.get("category", "Technical"))
                clean_why = html.escape(r["why_it_matters"][:130])
                clean_next = html.escape(r["next_action"])

                st.markdown(
                    textwrap.dedent(
                        f"""
                        <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(99, 102, 241, 0.35); border-radius: 14px; padding: 1.2rem; height: 100%;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span style="font-size: 0.75rem; font-weight: 700; color: #A5B4FC; background: rgba(99, 102, 241, 0.2); padding: 2px 8px; border-radius: 9999px;">
                                    Priority #{idx}
                                </span>
                                <span style="font-size: 0.75rem; font-weight: 700; color: {p_color}; background: {p_bg}; padding: 2px 8px; border-radius: 9999px;">
                                    {r['priority']} Priority
                                </span>
                            </div>
                            <div style="font-size: 1.15rem; font-weight: 800; color: #F8FAFC; margin-bottom: 4px;">
                                {s_icon} {clean_skill_name}
                            </div>
                            <div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 8px;">
                                Status: <span style="color: #CBD5E1; font-weight: 600;">{clean_status}</span> • {clean_category}
                            </div>
                            <div style="font-size: 0.82rem; color: #CBD5E1; line-height: 1.45; margin-bottom: 10px;">
                                {clean_why}...
                            </div>
                            <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 8px 10px; font-size: 0.76rem; color: #E0E7FF; line-height: 1.4;">
                                🚀 <strong>Next Action:</strong> {clean_next}
                            </div>
                        </div>
                        """
                    ).strip(),
                    unsafe_allow_html=True,
                )

        st.write("")

        # Completion Goals Box
        st.markdown(
            textwrap.dedent(
                """
                <div class="glass-card" style="padding: 1rem 1.25rem; margin-top: 0.5rem; margin-bottom: 1.5rem;">
                    <div style="font-size: 0.85rem; font-weight: 700; color: #CBD5E1; margin-bottom: 6px;">
                        🏁 Structured Completion Milestones
                    </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )
        for goal in learning_plan.get("completion_goals", []):
            st.markdown(
                textwrap.dedent(
                    f"""
                    <div style="font-size: 0.82rem; color: #94A3B8; margin-bottom: 4px; padding-left: 8px; border-left: 2px solid #818CF8;">
                        {html.escape(goal)}
                    </div>
                    """
                ).strip(),
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # DETAILED RECOMMENDATION ACCORDIONS
    # =========================================================================
    if detailed_recommendations:
        st.markdown("### Actionable Skill-Gap Breakdown & Exercise Blueprints")
        st.caption("Expand each card below to view custom practical exercises, portfolio projects, and YouTube search targets:")

        for rec in detailed_recommendations:
            p_badge = (
                "🔴 High Priority" if rec["priority"] == "High"
                else ("🟡 Medium Priority" if rec["priority"] == "Medium" else "🟢 Low Priority")
            )
            s_symbol = "~" if rec["status"] == "Partial" else ("✕" if rec["status"] == "Missing" else "🔍")

            expander_title = f"{s_symbol} {rec['skill_name']}  —  {rec['status']}  |  {p_badge}"

            with st.expander(expander_title, expanded=(rec["priority"] == "High")):
                col_r1, col_r2 = st.columns([1.1, 0.9])

                clean_why = html.escape(rec["why_it_matters"])
                clean_demo = html.escape(rec["current_demonstration"])
                clean_reason = html.escape(rec["priority_reason"])
                clean_learn = html.escape(rec["what_to_learn"])
                clean_proj = html.escape(rec["suggested_project"])

                with col_r1:
                    st.markdown(
                        textwrap.dedent(
                            f"""
                            <div style="font-size: 0.84rem; color: #CBD5E1; line-height: 1.55; margin-bottom: 12px;">
                                <strong>Why This Matters for the Target Role:</strong><br/>
                                {clean_why}
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 10px 12px; margin-bottom: 12px; font-size: 0.82rem;">
                                <span style="color: #94A3B8; font-weight: 600;">Current Resume Status:</span><br/>
                                <span style="color: #F8FAFC;">{clean_demo}</span><br/>
                                <span style="color: #818CF8; font-size: 0.78rem;"><em>Priority Reason: {clean_reason}</em></span>
                            </div>
                            <div style="font-size: 0.84rem; color: #CBD5E1; line-height: 1.55;">
                                <strong>Core Concepts to Master:</strong><br/>
                                {clean_learn}
                            </div>
                            """
                        ).strip(),
                        unsafe_allow_html=True,
                    )

                with col_r2:
                    st.markdown(
                        textwrap.dedent(
                            """
                            <div style="font-size: 0.84rem; font-weight: 700; color: #F8FAFC; margin-bottom: 6px;">
                                🛠️ Practical Hands-on Exercises:
                            </div>
                            """
                        ).strip(),
                        unsafe_allow_html=True,
                    )
                    for ex in rec["practical_exercises"]:
                        st.markdown(
                            textwrap.dedent(
                                f"""
                                <div style="font-size: 0.8rem; color: #CBD5E1; margin-bottom: 6px; padding-left: 8px; border-left: 2px solid #34D399; line-height: 1.4;">
                                    • {html.escape(ex)}
                                </div>
                                """
                            ).strip(),
                            unsafe_allow_html=True,
                        )

                    st.markdown(
                        textwrap.dedent(
                            f"""
                            <div style="margin-top: 10px; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 8px; padding: 10px; font-size: 0.8rem; color: #E0E7FF; line-height: 1.45;">
                                📁 <strong>Suggested Portfolio Project:</strong><br/>
                                {clean_proj}
                            </div>
                            """
                        ).strip(),
                        unsafe_allow_html=True,
                    )

                # YouTube Search Query Action Line
                yt_query = rec["youtube_search_query"]
                yt_url = f"https://www.youtube.com/results?search_query={yt_query.replace(' ', '+')}"

                st.markdown(
                    textwrap.dedent(
                        f"""
                        <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.06); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                            <span style="font-size: 0.8rem; color: #94A3B8;">
                                🎯 <strong>Focused Video Query:</strong> <code style="color: #FCA5A5; background: rgba(239,68,68,0.1); padding: 2px 6px; border-radius: 4px;">{html.escape(yt_query)}</code>
                            </span>
                            <a href="{yt_url}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; background: rgba(239, 68, 68, 0.18); border: 1px solid rgba(239, 68, 68, 0.4); color: #FCA5A5; padding: 4px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; text-decoration: none;">
                                <span>Watch Tutorials on YouTube</span> ↗
                            </a>
                        </div>
                        """
                    ).strip(),
                    unsafe_allow_html=True,
                )

    st.write("")

    # =========================================================================
    # CATEGORIZED SKILLS TAXONOMY TABS (EVIDENCE & QUOTES)
    # =========================================================================
    st.markdown("### Verified Skills Taxonomy & Evidence Quotes")
    tab_match, tab_missing, tab_partial, tab_review = st.tabs([
        f"✅ Matching ({len(matching_skills)})",
        f"❌ Missing ({len(missing_skills)})",
        f"⚠️ Partial ({len(partial_skills)})",
        f"🔍 Needs Verification ({len(needs_verification_skills)})",
    ])

    with tab_match:
        if not matching_skills:
            st.info("No directly matching skills were detected between the resume and job requirements.")
        else:
            for s in matching_skills:
                importance_badge = (
                    "🔴 High Priority" if s["importance"] == "High"
                    else ("🟡 Medium Priority" if s["importance"] == "Medium" else "🟢 Preferred")
                )
                evidence_text = s.get("evidence", "")
                clean_name = html.escape(s["name"])
                clean_cat = html.escape(s.get("category", "Technical"))
                clean_exp = html.escape(s["explanation"])
                clean_ev = html.escape(evidence_text)

                st.markdown(
                    textwrap.dedent(
                        f"""
                        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 12px; padding: 14px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span class="pill pill-match">✓ {clean_name}</span>
                                    <span style="font-size: 0.76rem; background: rgba(255,255,255,0.06); color: #CBD5E1; padding: 2px 8px; border-radius: 4px;">{clean_cat}</span>
                                </div>
                                <span style="font-size: 0.75rem; color: #34D399; font-weight: 600;">{importance_badge}</span>
                            </div>
                            <div style="font-size: 0.85rem; color: #CBD5E1; margin-bottom: 6px;">
                                {clean_exp}
                            </div>
                            <div style="background: rgba(0,0,0,0.3); border-left: 3px solid #34D399; padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; color: #E2E8F0; font-family: monospace; line-height: 1.4;">
                                "{clean_ev}"
                            </div>
                        </div>
                        """
                    ).strip(),
                    unsafe_allow_html=True,
                )

    with tab_missing:
        if not missing_skills:
            st.success("🎉 Outstanding! No critical missing skill gaps were found for this position.")
        else:
            for s in missing_skills:
                importance_badge = (
                    "🔴 High Priority Gap" if s["importance"] == "High"
                    else ("🟡 Medium Gap" if s["importance"] == "Medium" else "🟢 Optional Gap")
                )
                clean_name = html.escape(s["name"])
                clean_cat = html.escape(s.get("category", "Technical"))
                clean_exp = html.escape(s["explanation"])
                clean_sug = html.escape(s["suggestion"])

                st.markdown(
                    textwrap.dedent(
                        f"""
                        <div style="background: rgba(244, 63, 94, 0.08); border: 1px solid rgba(244, 63, 94, 0.25); border-radius: 12px; padding: 14px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span class="pill pill-missing">✕ {clean_name}</span>
                                    <span style="font-size: 0.76rem; background: rgba(255,255,255,0.06); color: #CBD5E1; padding: 2px 8px; border-radius: 4px;">{clean_cat}</span>
                                </div>
                                <span style="font-size: 0.75rem; color: #FB7185; font-weight: 600;">{importance_badge}</span>
                            </div>
                            <div style="font-size: 0.85rem; color: #CBD5E1; margin-bottom: 6px;">
                                {clean_exp}
                            </div>
                            <div style="background: rgba(244, 63, 94, 0.12); padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; color: #FECDD3; line-height: 1.4;">
                                💡 <strong>Suggested Improvement:</strong> {clean_sug}
                            </div>
                        </div>
                        """
                    ).strip(),
                    unsafe_allow_html=True,
                )

    with tab_partial:
        if not partial_skills:
            st.info("No partially matching skills identified.")
        else:
            for s in partial_skills:
                evidence_text = s.get("evidence", "")
                clean_name = html.escape(s["name"])
                clean_cat = html.escape(s.get("category", "Technical"))
                clean_exp = html.escape(s["explanation"])
                clean_ev = html.escape(evidence_text)
                clean_sug = html.escape(s["suggestion"])

                st.markdown(
                    textwrap.dedent(
                        f"""
                        <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 12px; padding: 14px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span class="pill pill-partial">~ {clean_name}</span>
                                    <span style="font-size: 0.76rem; background: rgba(255,255,255,0.06); color: #CBD5E1; padding: 2px 8px; border-radius: 4px;">{clean_cat}</span>
                                </div>
                                <span style="font-size: 0.75rem; color: #FBBF24; font-weight: 600;">Partial Alignment</span>
                            </div>
                            <div style="font-size: 0.85rem; color: #CBD5E1; margin-bottom: 6px;">
                                {clean_exp}
                            </div>
                            <div style="background: rgba(0,0,0,0.3); border-left: 3px solid #FBBF24; padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; color: #E2E8F0; font-family: monospace; line-height: 1.4; margin-bottom: 6px;">
                                "{clean_ev}"
                            </div>
                            <div style="background: rgba(245, 158, 11, 0.12); padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; color: #FDE68A; line-height: 1.4;">
                                💡 <strong>Action:</strong> {clean_sug}
                            </div>
                        </div>
                        """
                    ).strip(),
                    unsafe_allow_html=True,
                )

    with tab_review:
        if not needs_verification_skills:
            st.info("No ambiguous skills requiring manual verification.")
        else:
            for s in needs_verification_skills:
                evidence_text = s.get("evidence", "")
                clean_name = html.escape(s["name"])
                clean_exp = html.escape(s["explanation"])
                clean_ev = html.escape(evidence_text)
                clean_sug = html.escape(s["suggestion"])

                ev_block = (
                    f'<div style="background: rgba(0,0,0,0.3); border-left: 3px solid #38BDF8; padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; color: #E2E8F0; font-family: monospace; line-height: 1.4; margin-bottom: 6px;">"{clean_ev}"</div>'
                    if evidence_text else ""
                )

                st.markdown(
                    textwrap.dedent(
                        f"""
                        <div style="background: rgba(14, 165, 233, 0.08); border: 1px solid rgba(14, 165, 233, 0.25); border-radius: 12px; padding: 14px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <span class="pill pill-tech">🔍 {clean_name}</span>
                                <span style="font-size: 0.75rem; color: #38BDF8; font-weight: 600;">Needs User Confirmation</span>
                            </div>
                            <div style="font-size: 0.85rem; color: #CBD5E1; margin-bottom: 6px;">
                                {clean_exp}
                            </div>
                            {ev_block}
                            <div style="background: rgba(14, 165, 233, 0.12); padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; color: #BAE6FD; line-height: 1.4;">
                                💡 {clean_sug}
                            </div>
                        </div>
                        """
                    ).strip(),
                    unsafe_allow_html=True,
                )

    st.write("")

    # =========================================================================
    # EXPERIENCE & SENIORITY SECTION
    # =========================================================================
    st.markdown(
        textwrap.dedent(
            """
            <div class="glass-card">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.2rem;">⏱️</span>
                    <h4 style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC; margin: 0;">
                        Experience & Seniority Evaluation
                    </h4>
                </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )
    for insight in exp_insights:
        st.markdown(
            textwrap.dedent(
                f"""
                <div style="margin-bottom: 10px; padding-left: 12px; border-left: 2px solid #818CF8; font-size: 0.85rem; color: #E2E8F0; line-height: 1.45;">
                    {html.escape(insight)}
                </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Disclaimer note
    if disclaimer:
        st.markdown(
            textwrap.dedent(
                f"""
                <div style="margin-top: 1rem; font-size: 0.75rem; color: #64748B; text-align: center; line-height: 1.5;">
                    {html.escape(disclaimer)}
                </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    # Navigation buttons
    col_nav1, col_nav2 = st.columns([1, 1])

    with col_nav1:
        if st.button("⬅️ Back to Analysis Pipeline", use_container_width=True, type="secondary"):
            st.session_state["workflow_step"] = 3
            st.session_state["current_page"] = "Resume Analysis"
            st.session_state["pending_page"] = "Resume Analysis"
            st.rerun()

    with col_nav2:
        if st.button("Explore YouTube Learning Resources ➔", use_container_width=True, type="primary"):
            st.session_state["workflow_step"] = 5
            st.session_state["current_page"] = "Resume Analysis"
            st.session_state["pending_page"] = "Resume Analysis"
            st.rerun()
