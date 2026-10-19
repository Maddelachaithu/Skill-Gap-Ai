"""
Step 1: Resume Upload View for Skill Gap AI
Provides functional drag-and-drop resume uploading, format & size validation,
in-memory text extraction using PyMuPDF (PDF) and python-docx (DOCX),
empty/unreadable file detection, and state preservation.
"""

import html
import textwrap
import streamlit as st

from components.stepper import render_stepper
from backend.resume_parser import parse_resume, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB

# Pre-extracted sample resume profile for rapid UI/UX demo testing
DEMO_RESUME_FILENAME = "Alex_Morgan_Senior_Software_Engineer_Resume.pdf"
DEMO_RESUME_TEXT = """Alex Morgan
Senior Software Engineer | Cloud & Full-Stack Architect
Email: alex.morgan@example.com | GitHub: github.com/alexmorgan | LinkedIn: linkedin.com/in/alexmorgan

PROFESSIONAL SUMMARY
Experienced Senior Full-Stack Engineer with 4.5+ years of designing, building, and deploying highly scalable cloud applications. Proven track record in asynchronous microservices with Python (FastAPI, Django), reactive single-page applications with React and Next.js, and relational database architecture with PostgreSQL.

CORE TECHNICAL SKILLS
- Programming Languages: Python 3.11+, JavaScript (ES6+), TypeScript, SQL, Bash
- Backend & Frameworks: FastAPI, Django, Flask, Node.js, RESTful API Design
- Frontend & UI: React.js, Next.js, Redux Toolkit, Tailwind CSS, HTML5/CSS3
- Databases & Storage: PostgreSQL, SQLite, Redis caching, SQLAlchemy ORM
- DevOps & Tools: Git, GitHub Actions, Docker, Linux Systems, AWS (EC2, S3)
- Testing & Quality: Pytest, Unit Testing, Integration Testing, Code Reviews

PROFESSIONAL EXPERIENCE
Senior Software Engineer | Apex Cloud Systems (2022 - Present)
- Architected and delivered 12+ production REST API endpoints using FastAPI and PostgreSQL, serving 150k+ daily requests with <80ms response times.
- Led frontend migration from legacy monolithic views to a modern React / Next.js architecture, improving client-side page load speed by 38%.
- Optimized database indexing and query execution plans in PostgreSQL, reducing query execution latency by 45%.
- Implemented automated CI/CD pipeline checks using GitHub Actions and Pytest, boosting code coverage from 62% to 91%.

Full-Stack Developer | InnovateTech Labs (2020 - 2022)
- Built customer-facing analytical dashboards using React, TypeScript, and Chart.js.
- Developed backend service integrations with external payment gateways and webhook ingestion pipelines in Python/Django.
- Managed cloud hosting, domain certificates, and automated backups on AWS EC2 and S3.

EDUCATION & CERTIFICATIONS
- B.S. in Computer Science | State University of Technology (2016 - 2020)
- AWS Certified Cloud Practitioner (2023)
"""


def render_step1_upload():
    """Renders Step 1: Resume Upload with live text extraction and validation."""
    render_stepper(1)

    st.markdown(
        textwrap.dedent(
            """
            <div style="margin-bottom: 1.5rem;">
                <h2 style="font-size: 1.75rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.35rem;">
                    Step 1: Upload Your Resume
                </h2>
                <p style="color: #94A3B8; font-size: 0.95rem;">
                    Upload your latest resume. Text is extracted securely in-memory using PyMuPDF and python-docx.
                </p>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )

    # Information & privacy banner
    st.markdown(
        textwrap.dedent(
            """
            <div class="glass-card" style="padding: 1rem 1.25rem; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.4rem;">🔒</span>
                    <span style="font-size: 0.88rem; color: #CBD5E1;">
                        <strong>Supported Formats:</strong> PDF (.pdf) or Word (.docx) &nbsp;|&nbsp; 
                        <strong>Max Size:</strong> 10 MB &nbsp;|&nbsp;
                        <strong>Privacy Guarantee:</strong> Processed locally in-memory; never stored on disk or shared.
                    </span>
                </div>
                <span style="font-size: 0.78rem; background: rgba(16, 185, 129, 0.2); color: #34D399; padding: 4px 10px; border-radius: 9999px; font-weight: 600;">
                    Stage 2 Functional Parser
                </span>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )

    # File Uploader
    uploaded_file = st.file_uploader(
        label="Drag and drop your resume file here (PDF or DOCX)",
        type=list(ALLOWED_EXTENSIONS),
        help=f"Supported formats: PDF (.pdf) and Word (.docx). Maximum file size: {MAX_FILE_SIZE_MB} MB",
        key="resume_file_uploader",
    )

    # Quick Demo Load Option (Great for quick UI evaluations)
    col_demo1, col_demo2 = st.columns([3, 1.2])
    with col_demo2:
        if st.button(
            "📄 Load Demo Resume",
            use_container_width=True,
            type="secondary",
            help="Populate with a pre-validated software engineer resume for rapid evaluation",
        ):
            words = len(DEMO_RESUME_TEXT.split())
            chars = len(DEMO_RESUME_TEXT)
            st.session_state["resume_uploaded"] = True
            st.session_state["resume_name"] = DEMO_RESUME_FILENAME
            st.session_state["resume_size_kb"] = 245.8
            st.session_state["resume_type"] = "PDF"
            st.session_state["resume_text"] = DEMO_RESUME_TEXT
            st.session_state["resume_word_count"] = words
            st.session_state["resume_char_count"] = chars
            st.session_state["resume_page_count"] = 1
            st.toast("Pre-validated sample resume profile loaded!", icon="📄")
            st.rerun()

    # Process Uploaded File when user provides a new file
    if uploaded_file is not None:
        current_name = st.session_state.get("resume_name")
        file_bytes = uploaded_file.read()

        # Only re-parse if not already parsed with this exact filename and size
        if current_name != uploaded_file.name or not st.session_state.get("resume_text"):
            with st.spinner("Extracting and validating resume text in-memory..."):
                parse_result = parse_resume(file_bytes, uploaded_file.name)

            if parse_result["success"]:
                st.session_state["resume_uploaded"] = True
                st.session_state["resume_name"] = uploaded_file.name
                st.session_state["resume_size_kb"] = round(len(file_bytes) / 1024, 1)
                st.session_state["resume_type"] = parse_result["file_type"]
                st.session_state["resume_text"] = parse_result["text"]
                st.session_state["resume_word_count"] = parse_result["word_count"]
                st.session_state["resume_char_count"] = parse_result["char_count"]
                st.session_state["resume_page_count"] = parse_result["page_count"]
                st.success(
                    f"✅ Resume successfully parsed! Extracted {parse_result['word_count']} words ready for job comparison."
                )
            else:
                # Parsing failed (empty, corrupted, unreadable scanned image, etc.)
                st.session_state["resume_uploaded"] = False
                st.session_state["resume_name"] = None
                st.session_state["resume_text"] = ""
                st.session_state["resume_word_count"] = 0
                st.session_state["resume_char_count"] = 0
                st.error(f"❌ {parse_result['error']}", icon="⚠️")

    # Display Uploaded Resume Card if validated in session state
    has_valid_resume = (
        st.session_state.get("resume_uploaded", False)
        and bool(st.session_state.get("resume_text", "").strip())
    )

    if has_valid_resume:
        name = st.session_state.get("resume_name", "Resume.pdf")
        size_kb = st.session_state.get("resume_size_kb", 0.0)
        file_type = st.session_state.get("resume_type", "PDF")
        word_count = st.session_state.get("resume_word_count", 0)
        char_count = st.session_state.get("resume_char_count", 0)
        icon_symbol = "📕" if file_type == "PDF" else "📘"

        clean_name = html.escape(name)
        clean_file_type = html.escape(file_type)

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="file-card">
                    <div class="file-info">
                        <div class="file-icon">{icon_symbol}</div>
                        <div>
                            <div style="font-weight: 700; font-size: 1.02rem; color: #F8FAFC;">
                                {clean_name}
                            </div>
                            <div style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">
                                Format: <span style="color: #A5B4FC; font-weight: 600;">{clean_file_type}</span> • 
                                Size: <span style="color: #CBD5E1;">{size_kb} KB</span> • 
                                Extracted: <span style="color: #34D399; font-weight: 600;">{word_count} words ({char_count:,} characters)</span>
                            </div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="background: rgba(16, 185, 129, 0.18); border: 1px solid rgba(16, 185, 129, 0.4); color: #34D399; padding: 4px 12px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600;">
                            ✓ Text Extracted
                        </span>
                    </div>
                </div>
                """
            ).strip(),
            unsafe_allow_html=True,
        )

        # Extracted text inspector (Collapsible, beginner-friendly verification)
        with st.expander("👁️ Preview Extracted Resume Text (Verification)", expanded=False):
            st.caption("Verifying that all sections, skills, and experience items were cleanly captured:")
            st.text_area(
                label="Extracted Text",
                value=st.session_state.get("resume_text", ""),
                height=220,
                disabled=True,
                label_visibility="collapsed",
            )

    # Action / Progression Buttons
    st.write("")
    col_nav1, col_nav2 = st.columns([1, 1])

    with col_nav2:
        if st.button(
            "Continue to Job Description ➔",
            use_container_width=True,
            type="primary",
            disabled=not has_valid_resume,
            help="Upload a valid resume first to unlock the next step" if not has_valid_resume else "Proceed to Step 2",
        ):
            st.session_state["workflow_step"] = 2
            st.rerun()

    if not has_valid_resume:
        st.info("ℹ️ Please upload a readable PDF or DOCX resume (or click 'Load Demo Resume') to proceed to Step 2.")
