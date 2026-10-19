"""
Skill Gap AI - AI-Powered Resume Analyzer and Personalized Learning Platform
Main Entry Point (app.py)

This module handles:
1. Streamlit configuration and futuristic dark navy theme injection.
2. Session state lifecycle management (resumes, extracted text, job postings, step navigation).
3. Sidebar rendering and view routing across the 5-step workflow with step gating.
"""

import streamlit as st

# Import visual styles & components
from components.styles import inject_custom_css
from components.sidebar import render_sidebar

# Import individual view handlers
from views.home import render_home_page
from views.step1_upload import render_step1_upload
from views.step2_job_desc import render_step2_job_desc
from views.step3_analysis import render_step3_analysis
from views.step4_report import render_step4_report
from views.step5_learning import render_step5_learning
from views.about import render_about_page

# Import workflow validation guards
from backend.workflow_state import (
    can_access_job_description_step,
    can_access_analysis_step,
    can_access_report_step,
)


def initialize_session_state():
    """Initializes default session state variables if they do not already exist."""
    defaults = {
        "current_page": "Home",
        "workflow_step": 1,
        # Resume state
        "resume_uploaded": False,
        "resume_name": None,
        "resume_size_kb": None,
        "resume_type": None,
        "resume_text": "",
        "resume_word_count": 0,
        "resume_char_count": 0,
        "resume_page_count": 0,
        # Job description state
        "job_title": "",
        "company_name": "",
        "job_description": "",
        # Analysis state
        "analysis_completed": False,
        "analysis_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main():
    """Main application lifecycle controller."""
    # 1. Configure the page properties
    st.set_page_config(
        page_title="Skill Gap AI — AI Resume Analyzer",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 2. Inject dark navy glassmorphic CSS design system
    inject_custom_css()

    # 3. Initialize state tracking
    initialize_session_state()

    # 4. Render branded sidebar
    render_sidebar()

    # 5. Route to appropriate view based on active page selection
    current_page = st.session_state.get("current_page", "Home")

    if current_page == "Home":
        render_home_page()

    elif current_page == "Resume Analysis":
        # Route through the 5-step analysis pipeline with step gating
        current_step = st.session_state.get("workflow_step", 1)

        # Step 2 gating: must have uploaded resume with extracted text
        if current_step == 2 and not can_access_job_description_step(
            st.session_state.get("resume_uploaded", False),
            st.session_state.get("resume_text", ""),
        ):
            st.session_state["workflow_step"] = 1
            current_step = 1

        # Step 3 gating: must have both resume and job description
        if current_step == 3 and not can_access_analysis_step(
            st.session_state.get("resume_uploaded", False),
            st.session_state.get("resume_text", ""),
            st.session_state.get("job_title", ""),
            st.session_state.get("job_description", ""),
        ):
            st.session_state["workflow_step"] = 2
            current_step = 2

        # Step 4 gating: must have run an analysis
        if current_step == 4 and not can_access_report_step(st.session_state):
            st.session_state["workflow_step"] = 3
            current_step = 3

        if current_step == 1:
            render_step1_upload()
        elif current_step == 2:
            render_step2_job_desc()
        elif current_step == 3:
            render_step3_analysis()
        elif current_step == 4:
            render_step4_report()
        elif current_step == 5:
            render_step5_learning()
        else:
            # Fallback to Step 1
            st.session_state["workflow_step"] = 1
            render_step1_upload()

    elif current_page == "Skill Gap Report":
        # Direct view of the Skill Gap Report (demonstration mode)
        render_step4_report()

    elif current_page == "Learning Resources":
        # Direct view of the YouTube Learning Resources dashboard
        render_step5_learning()

    elif current_page == "About Project":
        render_about_page()

    else:
        render_home_page()


if __name__ == "__main__":
    main()
