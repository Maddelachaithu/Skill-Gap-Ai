"""
Home Page View for Skill Gap AI
Displays the hero header, call-to-action, 3 core feature cards, and 5-step workflow overview.
"""

import streamlit as st


def on_start_resume_analysis():
    """Callback for Home page call-to-action button."""
    st.session_state["current_page"] = "Resume Analysis"
    st.session_state["pending_page"] = "Resume Analysis"
    st.session_state["workflow_step"] = 1
    try:
        st.session_state["sidebar_nav_radio"] = "🚀 Resume Analysis"
    except Exception:
        pass


def render_home_page():
    """Renders the landing Home page with modern AI dashboard aesthetics."""

    # Hero Badge and Title
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 1rem 1rem 1rem;">
            <div class="hero-badge">
                <span>✨ Next-Gen Career Intelligence</span>
            </div>
            <h1 class="hero-title">Build Your Career with AI</h1>
            <p class="hero-subtitle" style="margin: 0 auto 2rem auto;">
                Discover your skill gaps, improve your resume, and prepare for your dream job 
                with precision AI comparison and curated YouTube learning roadmaps.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Prominent Call-to-Action button centered
    col_l, col_btn, col_r = st.columns([1.5, 2, 1.5])
    with col_btn:
        if st.button(
            "🚀 Start Resume Analysis",
            use_container_width=True,
            type="primary",
            on_click=on_start_resume_analysis,
            key="btn_home_start_analysis",
        ):
            st.session_state["current_page"] = "Resume Analysis"
            st.session_state["pending_page"] = "Resume Analysis"
            st.session_state["workflow_step"] = 1
            st.rerun()

    st.write("")
    st.write("")

    # Feature Cards Section
    st.markdown(
        """
        <div style="margin: 2rem 0 1rem 0;">
            <h3 style="font-size: 1.35rem; font-weight: 700; color: #F1F5F9; letter-spacing: -0.01em;">
                Core Capabilities
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    feat_col1, feat_col2, feat_col3 = st.columns(3)

    with feat_col1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon-wrapper">📄</div>
                <div class="feature-title">AI Resume Analysis</div>
                <div class="feature-desc">
                    Parse and match your resume against target job postings with advanced semantic extraction to evaluate role alignment.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feat_col2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon-wrapper">🎯</div>
                <div class="feature-title">Smart Skill Gap Detection</div>
                <div class="feature-desc">
                    Spot exactly which critical technologies, tools, and project experiences you are missing or only partially satisfying.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feat_col3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon-wrapper">🎥</div>
                <div class="feature-title">Personalized YouTube Learning</div>
                <div class="feature-desc">
                    Automatically receive high-quality, targeted YouTube tutorials and courses tailored to bridge each identified skill gap.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    # 5-Step Workflow Overview Section
    st.markdown(
        """
        <div class="glass-card" style="margin-top: 1.5rem;">
            <h3 style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.5rem;">
                Five-Step Path to Career Readiness
            </h3>
            <p style="color: #94A3B8; font-size: 0.92rem; margin-bottom: 1.5rem;">
                A structured, transparent workflow designed to take you from resume upload to interview-ready.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    step_cols = st.columns(5)
    steps_data = [
        ("1", "Upload Resume", "Upload your resume in PDF or DOCX format for instant validation.", "📄"),
        ("2", "Add Job Desc", "Paste the job description or role requirements you wish to target.", "📝"),
        ("3", "Analyze Resume", "Intelligent semantic comparison matches skills and identifies gaps.", "⚡"),
        ("4", "View Skill Gaps", "Explore an interactive match score with detailed skill breakdowns.", "📊"),
        ("5", "Learn & Improve", "Bridge weaknesses with curated YouTube learning playlists.", "🎓"),
    ]

    for col, (num, title, desc, icon) in zip(step_cols, steps_data):
        with col:
            st.markdown(
                f"""
                <div style="background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 1.1rem; height: 100%;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                        <span style="font-size: 1.3rem;">{icon}</span>
                        <span style="font-size: 0.75rem; font-weight: 700; background: rgba(99, 102, 241, 0.2); color: #A5B4FC; padding: 2px 8px; border-radius: 9999px;">Step {num}</span>
                    </div>
                    <div style="font-weight: 700; font-size: 0.95rem; color: #F1F5F9; margin-bottom: 0.35rem;">{title}</div>
                    <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.45;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
