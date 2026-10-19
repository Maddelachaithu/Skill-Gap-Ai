"""
About Project View for Skill Gap AI
Details the project objective, architecture overview, upcoming stages, and technology stack.
"""

import streamlit as st


def render_about_page():
    """Renders the About Project overview and technical roadmap."""
    st.markdown(
        """
        <div style="margin-bottom: 2rem;">
            <div class="hero-badge">
                <span>About Skill Gap AI</span>
            </div>
            <h2 style="font-size: 2.2rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.5rem;">
                Bridging the Gap Between Ambition and Opportunity
            </h2>
            <p style="color: #94A3B8; font-size: 1.05rem; max-width: 780px;">
                Skill Gap AI is an intelligent career assistant designed to demystify job requirements, 
                identify candidate weaknesses objectively, and provide actionable learning pathways.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="glass-card" style="height: 100%;">
                <h3 style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.75rem;">
                    🎯 Project Mission
                </h3>
                <p style="font-size: 0.92rem; color: #94A3B8; line-height: 1.6;">
                    Job descriptions frequently list dozens of competencies, making it overwhelming for candidates 
                    to understand where they truly stand. 
                    <strong style="color: #C7D2FE;">Skill Gap AI</strong> automates semantic comparison between a 
                    candidate's real experience and specific employer criteria, pinpointing exact deficits and recommending 
                    targeted, free video education.
                </p>
                <div style="margin-top: 1.25rem; padding: 12px; background: rgba(99, 102, 241, 0.12); border-radius: 10px; border-left: 3px solid #818CF8;">
                    <div style="font-weight: 700; color: #E0E7FF; font-size: 0.88rem;">Core Value Proposition</div>
                    <div style="font-size: 0.82rem; color: #A5B4FC; margin-top: 4px;">
                        "Analyze. Improve. Get Hired."
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="glass-card" style="height: 100%;">
                <h3 style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.75rem;">
                    💻 Architecture & Tech Stack
                </h3>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.88rem; padding-bottom: 6px; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                        <span style="color: #94A3B8;">Frontend & Dashboard:</span>
                        <span style="color: #F8FAFC; font-weight: 600;">Streamlit & Custom CSS Glassmorphism</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.88rem; padding-bottom: 6px; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                        <span style="color: #94A3B8;">Language Runtime:</span>
                        <span style="color: #F8FAFC; font-weight: 600;">Python 3.10+ (Windows / Linux / macOS)</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.88rem; padding-bottom: 6px; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                        <span style="color: #94A3B8;">Upcoming Parsing:</span>
                        <span style="color: #818CF8; font-weight: 600;">PyPDF & python-docx</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.88rem; padding-bottom: 6px; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                        <span style="color: #94A3B8;">Upcoming AI Engine:</span>
                        <span style="color: #A855F7; font-weight: 600;">LLM Semantic Matching & Skill Extraction</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.88rem;">
                        <span style="color: #94A3B8;">Video Learning Engine:</span>
                        <span style="color: #10B981; font-weight: 600;">YouTube Data API v3 (Live Recommendations)</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Development Roadmap
    st.markdown(
        """
        <div class="glass-card" style="margin-top: 1rem;">
            <h3 style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC; margin-bottom: 1rem;">
                🚀 Multi-Stage Implementation Roadmap
            </h3>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 14px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="font-weight: 700; color: #34D399; font-size: 0.9rem;">Stage 1: Frontend UI</span>
                        <span style="font-size: 0.72rem; background: #059669; color: white; padding: 2px 6px; border-radius: 4px;">DONE</span>
                    </div>
                    <div style="font-size: 0.82rem; color: #CBD5E1; line-height: 1.45;">
                        Complete modern AI dashboard, glassmorphism design system, session workflow, and placeholder reporting.
                    </div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 14px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="font-weight: 700; color: #34D399; font-size: 0.9rem;">Stage 2: Parsing</span>
                        <span style="font-size: 0.72rem; background: #059669; color: white; padding: 2px 6px; border-radius: 4px;">DONE</span>
                    </div>
                    <div style="font-size: 0.82rem; color: #CBD5E1; line-height: 1.45;">
                        In-memory text extraction for PDF (PyMuPDF) and DOCX (python-docx), empty document detection, input validation, and step gating.
                    </div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 14px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="font-weight: 700; color: #34D399; font-size: 0.9rem;">Stage 3: Analysis</span>
                        <span style="font-size: 0.72rem; background: #059669; color: white; padding: 2px 6px; border-radius: 4px;">DONE</span>
                    </div>
                    <div style="font-size: 0.82rem; color: #CBD5E1; line-height: 1.45;">
                        Taxonomy skill extraction, verbatim resume evidence matching, deterministic weighted scoring, and verified gap classifications.
                    </div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 14px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="font-weight: 700; color: #34D399; font-size: 0.9rem;">Stage 4: Recommendations</span>
                        <span style="font-size: 0.72rem; background: #059669; color: white; padding: 2px 6px; border-radius: 4px;">DONE</span>
                    </div>
                    <div style="font-size: 0.82rem; color: #CBD5E1; line-height: 1.45;">
                        Transparent priority calculation, personalized learning roadmap, hands-on exercises, portfolio project blueprints, and YouTube query generation.
                    </div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 14px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="font-weight: 700; color: #34D399; font-size: 0.9rem;">Stage 5: YouTube API</span>
                        <span style="font-size: 0.72rem; background: #059669; color: white; padding: 2px 6px; border-radius: 4px;">COMPLETED</span>
                    </div>
                    <div style="font-size: 0.82rem; color: #CBD5E1; line-height: 1.45;">
                        Official YouTube Data API v3 integration with real video search, thumbnail rendering, duration parsing, caching, and quota protection.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    if st.button("🚀 Try the Resume Analysis Workflow Now", type="primary", use_container_width=True):
        st.session_state["current_page"] = "Resume Analysis"
        st.session_state["pending_page"] = "Resume Analysis"
        st.session_state["workflow_step"] = 1
        st.rerun()
