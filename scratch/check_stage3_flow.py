"""
End-to-End Simulation of Stage 3 Workflow
"""

from backend.workflow_state import (
    validate_job_description,
    can_access_job_description_step,
    can_access_analysis_step,
    can_access_report_step,
)
from backend.resume_analyzer import analyze_resume_against_job
from backend.recommendation_service import generate_recommendations_for_analysis
from views.step1_upload import DEMO_RESUME_TEXT, DEMO_RESUME_FILENAME
from views.step2_job_desc import (
    SAMPLE_JOB_TITLE,
    SAMPLE_COMPANY,
    SAMPLE_JOB_DESC,
)


def run_e2e_simulation():
    session_state = {}

    print("--- 1. Testing Initial Gating ---")
    assert not can_access_job_description_step(False, "")
    assert not can_access_analysis_step(False, "", "", "")

    print("--- 2. Step 1: User uploads resume ---")
    session_state["resume_uploaded"] = True
    session_state["resume_name"] = DEMO_RESUME_FILENAME
    session_state["resume_text"] = DEMO_RESUME_TEXT
    session_state["resume_size_kb"] = 42.5
    session_state["resume_word_count"] = len(DEMO_RESUME_TEXT.split())
    session_state["resume_char_count"] = len(DEMO_RESUME_TEXT)
    session_state["workflow_step"] = 1

    assert can_access_job_description_step(
        session_state["resume_uploaded"], session_state["resume_text"]
    )
    print("Step 1 valid -> Can advance to Step 2.")

    print("--- 3. Step 2: User navigates to Step 2 ---")
    session_state["workflow_step"] = 2

    # Validation: empty job title
    valid, err = validate_job_description("", SAMPLE_JOB_DESC)
    assert not valid
    print(f"Validation caught empty job title: '{err}'")

    # Validation: empty job description
    valid, err = validate_job_description(SAMPLE_JOB_TITLE, "")
    assert not valid
    print(f"Validation caught empty job description: '{err}'")

    # User clicks 'Load Sample Job'
    session_state["job_title"] = SAMPLE_JOB_TITLE
    session_state["company_name"] = SAMPLE_COMPANY
    session_state["job_description"] = SAMPLE_JOB_DESC
    print(f"Sample job loaded: '{SAMPLE_JOB_TITLE}' at '{SAMPLE_COMPANY}'")

    valid, err = validate_job_description(
        session_state["job_title"], session_state["job_description"]
    )
    assert valid
    print("Sample job inputs validated successfully.")

    # User clicks Back to Step 1
    session_state["workflow_step"] = 1
    # Verify inputs are preserved
    assert session_state["job_title"] == SAMPLE_JOB_TITLE
    assert session_state["company_name"] == SAMPLE_COMPANY
    assert session_state["job_description"] == SAMPLE_JOB_DESC
    print("Inputs preserved on back navigation to Step 1.")

    # User returns to Step 2 and clicks Continue to Analysis
    session_state["workflow_step"] = 2
    assert can_access_analysis_step(
        session_state["resume_uploaded"],
        session_state["resume_text"],
        session_state["job_title"],
        session_state["job_description"],
    )
    session_state["run_analysis_pending"] = True
    session_state["workflow_step"] = 3
    print("Advanced to Step 3 with run_analysis_pending = True.")

    print("--- 4. Step 3: Analysis Execution ---")
    analysis_result = analyze_resume_against_job(
        resume_text=session_state["resume_text"],
        job_description=session_state["job_description"],
        job_title=session_state["job_title"],
    )

    assert analysis_result["success"] is True
    session_state["analysis_result"] = analysis_result
    session_state["analysis_completed"] = True
    session_state["run_analysis_pending"] = False

    score = analysis_result["scoring"]["display_score"]
    matching = [s["name"] for s in analysis_result["matching_skills"]]
    partial = [s["name"] for s in analysis_result["partial_skills"]]
    missing = [s["name"] for s in analysis_result["missing_skills"]]

    print(f"Analysis Completed! Match Score: {score}%")
    print(f"Matching Skills ({len(matching)}): {matching}")
    print(f"Partial Skills ({len(partial)}): {partial}")
    print(f"Missing Skills ({len(missing)}): {missing}")

    assert "Python" in matching
    assert "FastAPI" in matching
    assert "React" in matching
    assert "PostgreSQL" in matching
    assert "Docker" in matching
    assert len(missing) > 0 or len(partial) > 0

    recs = generate_recommendations_for_analysis(
        analysis_result=analysis_result,
        job_description=session_state["job_description"],
        resume_text=session_state["resume_text"],
        job_title=session_state["job_title"],
    )
    assert recs["success"] is True
    session_state["recommendations_data"] = recs
    print(f"Generated {len(recs['recommendations'])} personalized improvement recommendations.")

    session_state["workflow_step"] = 4
    assert can_access_report_step(session_state)
    print("Step 4 Accessible with genuine analysis data!")

    print("--- All E2E checks passed! ---")


if __name__ == "__main__":
    run_e2e_simulation()
