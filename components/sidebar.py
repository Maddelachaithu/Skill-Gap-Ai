"""
Sidebar Navigation Component for Skill Gap AI
Displays project branding, navigation options, current workflow status, and session controls.
"""

import streamlit as st
from backend.workflow_state import reset_workflow_state


def on_sidebar_nav_change():
    """Callback triggered when the user interacts with the sidebar navigation radio."""
    selected_nav = st.session_state.get("sidebar_nav_radio")
    if selected_nav:
        clean_page_name = selected_nav.split(" ", 1)[1]
        st.session_state["current_page"] = clean_page_name


def render_sidebar():
    """Renders the stylized sidebar with branding, navigation, and state status."""
    with st.sidebar:
        # Branding Header
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="brand-logo-icon">⚡</div>
                <div>
                    <div class="brand-title">Skill Gap AI</div>
                    <div class="brand-tagline">Analyze • Improve • Get Hired</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("NAVIGATION")

        nav_options = [
            "🏠 Home",
            "🚀 Resume Analysis",
            "📊 Skill Gap Report",
            "🎥 Learning Resources",
            "ℹ️ About Project",
        ]

        page_to_nav_option = {
            "Home": "🏠 Home",
            "Resume Analysis": "🚀 Resume Analysis",
            "Skill Gap Report": "📊 Skill Gap Report",
            "Learning Resources": "🎥 Learning Resources",
            "About Project": "ℹ️ About Project",
        }

        # Apply any pending programmatic navigation request before creating the radio widget
        if "pending_page" in st.session_state:
            st.session_state["current_page"] = st.session_state.pop("pending_page")

        # Keep sidebar radio state in sync with current_page before creating the widget
        current_page = st.session_state.get("current_page", "Home")
        expected_nav = page_to_nav_option.get(current_page, "🏠 Home")
        if st.session_state.get("sidebar_nav_radio") != expected_nav:
            st.session_state["sidebar_nav_radio"] = expected_nav

        page_to_index = {
            "Home": 0,
            "Resume Analysis": 1,
            "Skill Gap Report": 2,
            "Learning Resources": 3,
            "About Project": 4,
        }
        selected_index = page_to_index.get(current_page, 0)
        # Avoid Streamlit warning by passing index=None when session state already controls the key
        radio_index = None if "sidebar_nav_radio" in st.session_state else selected_index

        st.radio(
            label="Go to",
            options=nav_options,
            index=radio_index,
            label_visibility="collapsed",
            key="sidebar_nav_radio",
            on_change=on_sidebar_nav_change,
        )

        st.markdown("---")

        # Session Status Snapshot
        st.caption("ANALYSIS WORKFLOW STATUS")
        has_resume = bool(
            st.session_state.get("resume_uploaded", False)
            and st.session_state.get("resume_text", "").strip()
        )
        has_job = bool(
            st.session_state.get("job_description", "").strip()
            and st.session_state.get("job_title", "").strip()
        )
        current_step = st.session_state.get("workflow_step", 1)

        # Resume Status display
        dot_class_resume = "status-dot" if has_resume else "status-dot idle"
        if has_resume:
            name = st.session_state.get("resume_name", "Resume")
            words = st.session_state.get("resume_word_count", 0)
            resume_label = f"Resume: {name[:11]}... ({words}w)"
        else:
            resume_label = "Resume: Not Uploaded"

        # Job Status display
        dot_class_job = "status-dot" if has_job else "status-dot idle"
        if has_job:
            title = st.session_state.get("job_title", "Role")
            job_words = len(st.session_state.get("job_description", "").split())
            job_label = f"Target: {title[:11]}... ({job_words}w)"
        else:
            job_label = "Job Desc: Pending"

        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.5); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.05);">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; font-size: 0.82rem; color: #CBD5E1;">
                    <div class="{dot_class_resume}"></div>
                    <span>{resume_label}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; font-size: 0.82rem; color: #CBD5E1;">
                    <div class="{dot_class_job}"></div>
                    <span>{job_label}</span>
                </div>
                <div style="font-size: 0.78rem; color: #818CF8; font-weight: 600; margin-top: 8px;">
                    Active Step: {current_step} of 5
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        if st.button("🔄 Reset / Start New", use_container_width=True, type="secondary"):
            # Completely clear all session data including extracted text
            reset_workflow_state(st.session_state)
            st.success("Session reset. All analysis inputs cleared!")
            st.rerun()

        st.markdown(
            """
            <div style="margin-top: 2.5rem; text-align: center; font-size: 0.75rem; color: #64748B;">
                Skill Gap AI v0.2.0<br/>
                Stage 2: Functional Resume & Job
            </div>
            """,
            unsafe_allow_html=True,
        )
