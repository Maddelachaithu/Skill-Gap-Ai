"""
Streamlit AppTest Verification of Resume Analysis Workflow
Simulates full in-browser interaction and ensures NO session state widget key exception is raised.
"""

from streamlit.testing.v1 import AppTest


def test_full_analysis_workflow_in_apptest():
    print("--- 1. Launching AppTest from app.py ---")
    import os
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))
    at = AppTest.from_file(script_path, default_timeout=30)
    at.run()
    assert at.session_state["current_page"] == "Home"
    print("Initial page: Home")

    # 2. Click Start Resume Analysis button on Home page
    print("--- 2. Clicking 'Start Resume Analysis' button ---")
    at.button(key="btn_home_start_analysis").click().run()
    assert at.session_state["current_page"] == "Resume Analysis"
    assert at.session_state["workflow_step"] == 1
    print("Navigated to Resume Analysis - Step 1")

    # 3. On Step 1, click 'Load Demo Resume'
    print("--- 3. Clicking 'Load Demo Resume' ---")
    # Find the demo load button on Step 1
    demo_btn = None
    for btn in at.button:
        if "Load Demo Resume" in getattr(btn, "label", ""):
            demo_btn = btn
            break
    assert demo_btn is not None, "Load Demo Resume button not found!"
    demo_btn.click().run()
    assert at.session_state["resume_uploaded"] is True
    assert len(at.session_state["resume_text"]) > 100
    print("Demo Resume loaded successfully!")

    # 4. Click 'Continue to Job Description'
    print("--- 4. Clicking 'Continue to Job Description' ---")
    cont_step2_btn = None
    for btn in at.button:
        if "Continue to Job Description" in getattr(btn, "label", ""):
            cont_step2_btn = btn
            break
    assert cont_step2_btn is not None, "Continue to Job Description button not found!"
    cont_step2_btn.click().run()
    assert at.session_state["workflow_step"] == 2
    print("Advanced to Step 2: Add Job Description")

    # 5. On Step 2, click 'Load Sample Job'
    print("--- 5. Clicking 'Load Sample Job' ---")
    sample_job_btn = None
    for btn in at.button:
        if "Load Sample Job" in getattr(btn, "label", ""):
            sample_job_btn = btn
            break
    assert sample_job_btn is not None, "Load Sample Job button not found!"
    sample_job_btn.click().run()
    assert at.session_state["job_title"] != ""
    assert at.session_state["job_description"] != ""
    print(f"Sample Job loaded: '{at.session_state['job_title']}'")

    # 6. Click 'Continue to Analysis'
    print("--- 6. Clicking 'Continue to Analysis' ---")
    cont_analysis_btn = None
    for btn in at.button:
        if "Continue to Analysis" in getattr(btn, "label", ""):
            cont_analysis_btn = btn
            break
    assert cont_analysis_btn is not None, "Continue to Analysis button not found!"

    # This is where the bug occurred: modifying sidebar_nav_radio after instantiation!
    # With our fix, this must run cleanly without any exception!
    cont_analysis_btn.click().run()
    print("Step 2 Continue clicked. Workflow step:", at.session_state.get("workflow_step"))

    # Step 3 executed analysis and advanced to Step 4
    # Check if there are any exceptions
    assert len(at.exception) == 0, f"Exceptions occurred: {[e.value for e in at.exception]}"
    print("No exceptions encountered during analysis execution!")

    # Verify results stored in session state
    assert at.session_state.get("analysis_completed") is True
    assert at.session_state.get("analysis_result") is not None
    assert at.session_state["analysis_result"]["success"] is True

    score = at.session_state["analysis_result"]["scoring"]["display_score"]
    matching = len(at.session_state["analysis_result"]["matching_skills"])
    partial = len(at.session_state["analysis_result"]["partial_skills"])
    missing = len(at.session_state["analysis_result"]["missing_skills"])
    print(f"Analysis Results Verified! Score: {score}%, Matching: {matching}, Partial: {partial}, Missing: {missing}")

    assert at.session_state["workflow_step"] == 4
    print("Navigated to Step 4 (Skill Gap Report) successfully!")

    print("=== AppTest PASSED COMPLETELY! ===")


if __name__ == "__main__":
    test_full_analysis_workflow_in_apptest()
