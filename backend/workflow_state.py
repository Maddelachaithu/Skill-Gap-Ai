"""
Workflow State and Validation Helpers for Skill Gap AI
Centralizes validation logic and session state transitions across the 5-step workflow.
"""

from typing import Tuple, Dict, Any


def validate_job_description(job_title: str, job_description: str) -> Tuple[bool, str]:
    """
    Validates job title and job description inputs.
    Returns (is_valid, error_message).
    """
    if not job_title or not job_title.strip():
        return False, "Job title is required. Please specify the target position."

    if not job_description or not job_description.strip():
        return False, "Job description cannot be empty. Please paste the job requirements."

    if len(job_description.strip()) < 20:
        return False, "Job description is too short (minimum 20 characters required)."

    return True, ""


def can_access_job_description_step(resume_uploaded: bool, resume_text: str) -> bool:
    """
    Step 2 requires a valid uploaded resume with extracted readable text.
    """
    return bool(resume_uploaded and resume_text and resume_text.strip())


def can_access_analysis_step(
    resume_uploaded: bool,
    resume_text: str,
    job_title: str,
    job_description: str,
) -> bool:
    """
    Step 3 requires both valid resume text and valid job description inputs.
    """
    resume_ok = can_access_job_description_step(resume_uploaded, resume_text)
    is_job_valid, _ = validate_job_description(job_title, job_description)
    return resume_ok and is_job_valid


def can_access_report_step(state: Dict[str, Any]) -> bool:
    """
    Step 4 requires that an analysis has been successfully executed with results.
    """
    return bool(
        state.get("analysis_completed", False)
        and state.get("analysis_result")
        and state["analysis_result"].get("success", False)
    )


def reset_workflow_state(state: Dict[str, Any]) -> None:
    """
    Cleanses all analysis data and resets workflow to Step 1.
    Never stores files on disk.
    """
    state["resume_uploaded"] = False
    state["resume_name"] = None
    state["resume_size_kb"] = None
    state["resume_type"] = None
    state["resume_text"] = ""
    state["resume_word_count"] = 0
    state["resume_char_count"] = 0
    state["job_title"] = ""
    state["company_name"] = ""
    state["job_description"] = ""
    state["workflow_step"] = 1
    state["analysis_completed"] = False
    state["analysis_result"] = None
    state["current_page"] = "Resume Analysis"
    state["pending_page"] = "Resume Analysis"
    try:
        state["sidebar_nav_radio"] = "🚀 Resume Analysis"
    except Exception:
        pass
