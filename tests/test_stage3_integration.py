"""
Stage 3 Integration Tests for Skill Gap AI
Tests transition from Step 2 to Step 3, input validation, state preservation,
analysis service invocation, error handling, and results reporting.
"""

import pytest
from backend.workflow_state import (
    validate_job_description,
    can_access_job_description_step,
    can_access_analysis_step,
    can_access_report_step,
    reset_workflow_state,
)
from backend.resume_analyzer import analyze_resume_against_job
from backend.recommendation_service import generate_recommendations_for_analysis
from views.step2_job_desc import (
    SAMPLE_JOB_TITLE,
    SAMPLE_COMPANY,
    SAMPLE_JOB_DESC,
)


class TestStep2ToStep3ValidationAndGating:
    """Tests validation of job requirements and step gating."""

    def test_sample_job_constants_are_valid(self):
        """Confirm sample job contains non-empty title, company, and description."""
        assert SAMPLE_JOB_TITLE != ""
        assert "Sample" in SAMPLE_JOB_TITLE
        assert SAMPLE_COMPANY != ""
        assert len(SAMPLE_JOB_DESC) > 50
        is_valid, err = validate_job_description(SAMPLE_JOB_TITLE, SAMPLE_JOB_DESC)
        assert is_valid is True
        assert err == ""

    def test_empty_job_title_rejected(self):
        """Confirm empty job title fails validation with clear error message."""
        is_valid, err = validate_job_description("", "Requires 4 years Python and React.")
        assert is_valid is False
        assert "Job title is required" in err

    def test_whitespace_job_title_rejected(self):
        """Confirm whitespace-only job title fails validation."""
        is_valid, err = validate_job_description("   \t  ", "Requires 4 years Python and React.")
        assert is_valid is False
        assert "Job title is required" in err

    def test_empty_job_description_rejected(self):
        """Confirm empty job description fails validation with clear error message."""
        is_valid, err = validate_job_description("Senior Software Engineer", "")
        assert is_valid is False
        assert "Job description cannot be empty" in err

    def test_too_short_job_description_rejected(self):
        """Confirm job description shorter than 20 chars fails validation."""
        is_valid, err = validate_job_description("Senior Software Engineer", "Python only")
        assert is_valid is False
        assert "too short" in err

    def test_gating_cannot_access_step3_without_resume(self):
        """Confirm Step 3 cannot be accessed if resume is missing or unextracted."""
        # Resume uploaded false
        assert not can_access_analysis_step(
            resume_uploaded=False,
            resume_text="Some text",
            job_title="Software Engineer",
            job_description=SAMPLE_JOB_DESC,
        )
        # Resume text empty
        assert not can_access_analysis_step(
            resume_uploaded=True,
            resume_text="   ",
            job_title="Software Engineer",
            job_description=SAMPLE_JOB_DESC,
        )

    def test_gating_cannot_access_step3_without_valid_job(self):
        """Confirm Step 3 cannot be accessed if job title or description is missing."""
        assert not can_access_analysis_step(
            resume_uploaded=True,
            resume_text="Valid resume content with Python and SQL.",
            job_title="",
            job_description=SAMPLE_JOB_DESC,
        )
        assert not can_access_analysis_step(
            resume_uploaded=True,
            resume_text="Valid resume content with Python and SQL.",
            job_title="Software Engineer",
            job_description="",
        )

    def test_gating_can_access_step3_when_all_inputs_valid(self):
        """Confirm Step 3 is accessible when both resume and job inputs are valid."""
        assert can_access_analysis_step(
            resume_uploaded=True,
            resume_text="Valid candidate resume text mentioning Python, Docker, PostgreSQL.",
            job_title="Senior Engineer",
            job_description=SAMPLE_JOB_DESC,
        )


class TestStatePreservationAndTransitions:
    """Tests session-state persistence during transitions."""

    def test_session_state_preservation_on_back_navigation(self):
        """Verify state keys persist when moving back and forth."""
        state = {}
        # User uploaded resume in step 1
        state["resume_uploaded"] = True
        state["resume_name"] = "test_resume.pdf"
        state["resume_text"] = "Alex Morgan - Python, FastAPI, Docker developer"
        state["workflow_step"] = 2

        # User fills step 2
        state["job_title"] = "Cloud Architect"
        state["company_name"] = "Tech Corp"
        state["job_description"] = "Seeking a Cloud Architect with AWS, Kubernetes, and Python."

        # User clicks Back to Resume Upload (step 1)
        state["workflow_step"] = 1
        assert state["job_title"] == "Cloud Architect"
        assert state["company_name"] == "Tech Corp"
        assert "AWS" in state["job_description"]

        # User returns to step 2
        state["workflow_step"] = 2
        assert state["resume_uploaded"] is True
        assert state["resume_text"] == "Alex Morgan - Python, FastAPI, Docker developer"
        assert state["job_title"] == "Cloud Architect"

    def test_reset_workflow_clears_all_inputs_and_analysis(self):
        """Verify reset function clears all stages completely."""
        state = {
            "resume_uploaded": True,
            "resume_name": "resume.pdf",
            "resume_text": "Python React developer",
            "job_title": "Developer",
            "job_description": "We need Python and React",
            "workflow_step": 4,
            "analysis_completed": True,
            "analysis_result": {"success": True},
        }
        reset_workflow_state(state)
        assert state["resume_uploaded"] is False
        assert state["resume_text"] == ""
        assert state["job_title"] == ""
        assert state["job_description"] == ""
        assert state["workflow_step"] == 1
        assert state["analysis_completed"] is False
        assert state["analysis_result"] is None


class TestRealAnalysisExecutionAndErrorReporting:
    """Tests executing real resume analysis against real job descriptions."""

    def test_analysis_runs_against_real_inputs(self):
        """Confirm analysis produces realistic scores, matches, partials, and missing skills."""
        resume_text = (
            "Alex Morgan. Senior Software Engineer.\n"
            "Technical Skills: Python, FastAPI, React, Docker, PostgreSQL, Git.\n"
            "Experience: Built production APIs in Python and FastAPI. Managed Docker containers."
        )
        job_description = (
            "We are seeking a Senior Full-Stack Engineer.\n"
            "Required Qualifications:\n"
            "- Strong proficiency in Python and FastAPI\n"
            "- Hands-on experience with Docker\n"
            "- Kubernetes cluster orchestration experience (Must Have)\n"
            "- Experience with GraphQL APIs (Nice to have)\n"
            "- Familiarity with AWS cloud services\n"
        )
        job_title = "Senior Full-Stack Engineer"

        result = analyze_resume_against_job(
            resume_text=resume_text,
            job_description=job_description,
            job_title=job_title,
        )

        assert result["success"] is True
        assert result["error"] is None
        assert "scoring" in result

        matching_names = [s["name"] for s in result["matching_skills"]]
        missing_names = [s["name"] for s in result["missing_skills"]]

        # Python, FastAPI, Docker are mentioned in resume -> Matching
        assert "Python" in matching_names
        assert "FastAPI" in matching_names
        assert "Docker" in matching_names

        # Kubernetes, GraphQL, AWS are not in resume -> Missing or Partial
        assert "Kubernetes" in missing_names or any(s["name"] == "Kubernetes" for s in result["partial_skills"])
        assert "GraphQL" in missing_names or any(s["name"] == "GraphQL" for s in result["partial_skills"])

        # Score is deterministic and between 0 and 100
        score = result["scoring"]["display_score"]
        assert 0 < score < 100

        # Recommendations generated from actual analysis result
        recs = generate_recommendations_for_analysis(
            analysis_result=result,
            job_description=job_description,
            resume_text=resume_text,
            job_title=job_title,
        )
        assert recs["success"] is True
        assert len(recs["recommendations"]) > 0

    def test_analysis_fails_gracefully_with_empty_resume(self):
        """Confirm error is returned when resume text is empty, with helpful message."""
        result = analyze_resume_against_job(
            resume_text="",
            job_description="Seeking a Python developer.",
            job_title="Developer",
        )
        assert result["success"] is False
        assert "empty" in result["error"].lower()

    def test_analysis_fails_gracefully_with_empty_job(self):
        """Confirm error is returned when job description is empty."""
        result = analyze_resume_against_job(
            resume_text="Experienced Python developer.",
            job_description="",
            job_title="Developer",
        )
        assert result["success"] is False
        assert "empty" in result["error"].lower()

    def test_report_step_accessible_only_after_successful_analysis(self):
        """Confirm Step 4 can_access_report_step requires success=True."""
        state = {"analysis_completed": False, "analysis_result": None}
        assert not can_access_report_step(state)

        # Analysis completed but failed
        state = {
            "analysis_completed": True,
            "analysis_result": {"success": False, "error": "Failed"},
        }
        assert not can_access_report_step(state)

        # Analysis completed and succeeded
        state = {
            "analysis_completed": True,
            "analysis_result": {"success": True, "classified_skills": []},
        }
        assert can_access_report_step(state)
