"""
Step 2: Job Description View for Skill Gap AI
Collects job title, company name, and job requirements with validation.
Only accessible after Step 1 resume upload and text extraction is verified.
"""

import textwrap
import streamlit as st

from components.stepper import render_stepper
from backend.workflow_state import (
    validate_job_description,
    can_access_job_description_step,
)

SAMPLE_JOB_TITLE = "Senior Full-Stack Engineer (Sample)"
SAMPLE_COMPANY = "CloudScale Tech (Sample)"
SAMPLE_JOB_DESC = """Role: Senior Full-Stack Engineer
Location: Remote (US / Global)

About the Role:
We are looking for an experienced Senior Full-Stack Engineer to architect, build, and deploy high-performance cloud applications. You will work across modern frontend frameworks and scalable distributed backends.

Requirements & Tech Stack:
- 4+ years of production experience with Python and JavaScript/TypeScript
- Deep expertise in React, Next.js, and modern CSS
- Backend proficiency with Python (FastAPI, Django) and PostgreSQL
- Containerization and orchestration experience using Docker and Kubernetes
- Solid understanding of GraphQL APIs and REST architecture
- Familiarity with CI/CD pipelines, AWS/GCP cloud infrastructure
- Strong foundation in distributed systems, caching (Redis), and system design

Nice to Have:
- Experience with AI/LLM integration and prompt engineering
- Knowledge of automated testing (pytest, Playwright)
"""


def render_step2_job_desc():
    """Renders Step 2: Job Description Input form with validation and state preservation."""
    # Ensure pre-requisite (Resume uploaded with extracted text) is met
    has_valid_resume = can_access_job_description_step(
        st.session_state.get("resume_uploaded", False),
        st.session_state.get("resume_text", ""),
    )

    if not has_valid_resume:
        st.warning("⚠️ Access Restricted: Please complete Step 1 (Upload Resume & Extract Text) before providing a job description.")
        if st.button("⬅️ Go to Step 1: Upload Resume"):
            st.session_state["workflow_step"] = 1
            st.rerun()
        return

    render_stepper(2)

    st.markdown(
        textwrap.dedent(
            """
            <div style="margin-bottom: 1.5rem;">
                <h2 style="font-size: 1.75rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.35rem;">
                    Step 2: Add Job Description
                </h2>
                <p style="color: #94A3B8; font-size: 0.95rem;">
                    Specify the target position and paste the job posting requirements to evaluate against your resume.
                </p>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )

    # Quick demo fill button
    col_hdr, col_fill = st.columns([3, 1.2])
    with col_fill:
        if st.button(
            "📋 Load Sample Job",
            use_container_width=True,
            type="secondary",
            help="Autofill with sample Senior Full-Stack Engineer job posting for quick evaluation",
        ):
            st.session_state["job_title"] = SAMPLE_JOB_TITLE
            st.session_state["company_name"] = SAMPLE_COMPANY
            st.session_state["job_description"] = SAMPLE_JOB_DESC
            st.session_state["input_job_title"] = SAMPLE_JOB_TITLE
            st.session_state["input_company_name"] = SAMPLE_COMPANY
            st.session_state["input_job_description"] = SAMPLE_JOB_DESC
            st.toast("Loaded sample job description!", icon="📝")
            st.rerun()

    title_kwargs = {"key": "input_job_title"}
    if "input_job_title" not in st.session_state and "job_title" in st.session_state:
        title_kwargs["value"] = st.session_state["job_title"]

    company_kwargs = {"key": "input_company_name"}
    if "input_company_name" not in st.session_state and "company_name" in st.session_state:
        company_kwargs["value"] = st.session_state["company_name"]

    desc_kwargs = {"key": "input_job_description"}
    if "input_job_description" not in st.session_state and "job_description" in st.session_state:
        desc_kwargs["value"] = st.session_state["job_description"]

    # Form layout
    col_title, col_company = st.columns(2)

    with col_title:
        job_title = st.text_input(
            "Target Job Title *",
            placeholder="e.g. Senior Full-Stack Engineer, Data Scientist, DevOps Specialist",
            help="The specific position title from the job advertisement",
            **title_kwargs,
        )

    with col_company:
        company_name = st.text_input(
            "Company / Organization (Optional)",
            placeholder="e.g. CloudScale Tech, Stripe, InnovateLabs",
            help="Optional employer name for reporting context",
            **company_kwargs,
        )

    # Synchronize state immediately
    st.session_state["job_title"] = job_title
    st.session_state["company_name"] = company_name

    job_description = st.text_area(
        "Job Description & Requirements *",
        height=260,
        placeholder="Paste the complete job description, required qualifications, key technologies, and day-to-day responsibilities here...",
        help="Paste the full job requirements text here",
        **desc_kwargs,
    )

    st.session_state["job_description"] = job_description

    # Live word count metrics
    desc_words = len(job_description.split()) if job_description.strip() else 0
    desc_chars = len(job_description)

    st.markdown(
        textwrap.dedent(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.82rem; color: #94A3B8; margin-top: 0.25rem;">
                <span>* Both Job Title and Job Description fields are required.</span>
                <span>Length: <strong style="color: #A5B4FC;">{desc_words} words</strong> ({desc_chars:,} chars)</span>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )

    st.write("")
    st.write("")

    # Navigation buttons
    col_back, col_next = st.columns([1, 1])

    with col_back:
        if st.button("⬅️ Back to Resume Upload", use_container_width=True, type="secondary"):
            # Preserve form values in session state
            st.session_state["job_title"] = job_title.strip() if job_title else ""
            st.session_state["company_name"] = company_name.strip() if company_name else ""
            st.session_state["job_description"] = job_description.strip() if job_description else ""
            st.session_state["workflow_step"] = 1
            st.rerun()

    with col_next:
        if st.button("Continue to Analysis ➔", use_container_width=True, type="primary"):
            # 1. Confirm that a valid resume has already been uploaded & extracted
            has_resume = (
                st.session_state.get("resume_uploaded", False)
                and bool(st.session_state.get("resume_text", "").strip())
            )
            if not has_resume:
                st.error("⚠️ Resume Required: Please complete Step 1 by uploading a valid resume before continuing.", icon="⚠️")
            else:
                # 2. Validate job title and description
                is_valid, error_msg = validate_job_description(job_title, job_description)
                if not is_valid:
                    st.error(f"⚠️ {error_msg}", icon="⚠️")
                else:
                    # 3. Store the submitted information in session state
                    st.session_state["job_title"] = job_title.strip()
                    st.session_state["company_name"] = company_name.strip() if company_name else ""
                    st.session_state["job_description"] = job_description.strip()

                    # Set flag so Step 3 automatically runs analysis with spinner
                    st.session_state["run_analysis_pending"] = True
                    st.session_state.pop("analysis_error", None)

                    # 4. Navigate to Step 3
                    st.session_state["workflow_step"] = 3
                    st.rerun()

