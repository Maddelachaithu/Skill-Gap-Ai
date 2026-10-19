"""
Unit Tests for Skill Gap AI - Workflow State & Job Description Validation
Covers job description validation, step gating, and reset state transitions.
"""

import pytest
from backend.workflow_state import (
    validate_job_description,
    can_access_job_description_step,
    can_access_analysis_step,
    reset_workflow_state,
)


class TestJobDescriptionValidation:
    """Tests for job title and job description validation."""

    def test_valid_job_description(self):
        valid, err = validate_job_description(
            job_title="Software Engineer",
            job_description="Seeking a Python developer with experience in FastAPI and PostgreSQL.",
        )
        assert valid is True
        assert err == ""

    def test_empty_job_title(self):
        valid, err = validate_job_description(
            job_title="",
            job_description="Seeking a Python developer with experience in FastAPI.",
        )
        assert valid is False
        assert "Job title is required" in err

    def test_whitespace_job_title(self):
        valid, err = validate_job_description(
            job_title="   ",
            job_description="Seeking a Python developer with experience in FastAPI.",
        )
        assert valid is False
        assert "Job title is required" in err

    def test_empty_job_description(self):
        valid, err = validate_job_description(
            job_title="Software Engineer",
            job_description="",
        )
        assert valid is False
        assert "Job description cannot be empty" in err

    def test_too_short_job_description(self):
        valid, err = validate_job_description(
            job_title="Software Engineer",
            job_description="Too short",
        )
        assert valid is False
        assert "too short" in err


class TestWorkflowGating:
    """Tests for preventing skipping required steps."""

    def test_cannot_access_step2_without_resume(self):
        assert can_access_job_description_step(resume_uploaded=False, resume_text="") is False

    def test_cannot_access_step2_with_uploaded_but_empty_text(self):
        assert can_access_job_description_step(resume_uploaded=True, resume_text="") is False

    def test_can_access_step2_with_valid_resume_and_text(self):
        assert can_access_job_description_step(
            resume_uploaded=True,
            resume_text="John Doe Senior Engineer Experience in Cloud",
        ) is True

    def test_cannot_access_step3_without_resume(self):
        assert can_access_analysis_step(
            resume_uploaded=False,
            resume_text="",
            job_title="DevOps",
            job_description="Valid job description with enough characters for testing.",
        ) is False

    def test_cannot_access_step3_without_job_description(self):
        assert can_access_analysis_step(
            resume_uploaded=True,
            resume_text="Valid resume content here with sufficient details.",
            job_title="",
            job_description="",
        ) is False

    def test_can_access_step3_with_both_inputs_valid(self):
        assert can_access_analysis_step(
            resume_uploaded=True,
            resume_text="Jane Developer Python React AWS Docker Kubernetes",
            job_title="Senior Developer",
            job_description="Looking for an experienced Senior Developer proficient in Python and React.",
        ) is True


class TestResetWorkflowState:
    """Tests for Reset / Start New analysis state clearing."""

    def test_reset_clears_all_data(self):
        fake_session = {
            "resume_uploaded": True,
            "resume_name": "candidate.pdf",
            "resume_size_kb": 120.5,
            "resume_type": "PDF",
            "resume_text": "Extracted text content here",
            "resume_word_count": 250,
            "resume_char_count": 1500,
            "job_title": "Full Stack Dev",
            "company_name": "Acme Corp",
            "job_description": "We need a full stack developer...",
            "workflow_step": 4,
            "analysis_completed": True,
            "current_page": "Skill Gap Report",
        }

        reset_workflow_state(fake_session)

        assert fake_session["resume_uploaded"] is False
        assert fake_session["resume_name"] is None
        assert fake_session["resume_text"] == ""
        assert fake_session["resume_word_count"] == 0
        assert fake_session["job_title"] == ""
        assert fake_session["company_name"] == ""
        assert fake_session["job_description"] == ""
        assert fake_session["workflow_step"] == 1
        assert fake_session["analysis_completed"] is False
        assert fake_session["current_page"] == "Resume Analysis"
        assert fake_session["sidebar_nav_radio"] == "🚀 Resume Analysis"

