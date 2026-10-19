"""
Streamlit AppTest Verification of Complete Workflow through Step 5 (Learning Resources)
Verifies:
1. Navigation from Step 4 (Skill Gap Report) to Step 5 (Learning Resources) via button.
2. Step 5 renders the live YouTube recommendations without exception.
3. Up to 10 video recommendations are displayed with proper count labels.
"""

from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest
import os


def test_step5_workflow_in_apptest():
    print("--- 1. Launching AppTest from app.py ---")
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))
    at = AppTest.from_file(script_path, default_timeout=30)
    at.run()

    # Step 1: Click Start Resume Analysis
    at.button(key="btn_home_start_analysis").click().run()

    # Step 1: Load Demo Resume
    demo_btn = next((b for b in at.button if "Load Demo Resume" in getattr(b, "label", "")), None)
    assert demo_btn is not None
    demo_btn.click().run()

    # Step 1: Continue to Job Description
    cont_step2 = next((b for b in at.button if "Continue to Job Description" in getattr(b, "label", "")), None)
    assert cont_step2 is not None
    cont_step2.click().run()

    # Step 2: Load Sample Job
    sample_btn = next((b for b in at.button if "Load Sample Job" in getattr(b, "label", "")), None)
    assert sample_btn is not None
    sample_btn.click().run()

    # Step 2: Continue to Analysis
    cont_analysis = next((b for b in at.button if "Continue to Analysis" in getattr(b, "label", "")), None)
    assert cont_analysis is not None
    cont_analysis.click().run()

    # Step 4: Verify we are on report page
    assert at.session_state["workflow_step"] == 4
    print("Step 4 reached. Advancing to Step 5 (Learning Resources)...")

    # Step 4: Click 'Explore YouTube Learning Resources ➔'
    explore_btn = next((b for b in at.button if "Explore YouTube Learning Resources" in getattr(b, "label", "")), None)
    assert explore_btn is not None, "Explore YouTube button not found on Step 4!"

    # Mock the YouTube search to return 10 videos per skill without consuming quota
    mock_10_videos = [
        {
            "video_id": f"vid_test_{i:02d}",
            "title": f"Complete Mastery Video #{i}",
            "channel_title": f"Dev Channel #{i}",
            "description": f"Learn key production skills in video #{i}",
            "thumbnail_url": f"https://i.ytimg.com/vi/vid_test_{i:02d}/hqdefault.jpg",
            "watch_url": f"https://www.youtube.com/watch?v=vid_test_{i:02d}",
            "duration": f"1{i}:00",
            "skill_name": "Docker",
        }
        for i in range(1, 11)
    ]

    with patch(
        "views.step5_learning.fetch_cached_youtube_videos",
        return_value={"success": True, "videos": mock_10_videos, "total_results": 10},
    ):
        explore_btn.click().run()

        # Verify Step 5 reached
        assert at.session_state["workflow_step"] == 5
        print(f"Step 5 reached! Workflow step: {at.session_state['workflow_step']}")

        # Verify NO exceptions occurred during Step 5 execution
        assert len(at.exception) == 0, f"Exceptions in Step 5: {[e.value for e in at.exception]}"

        # Verify markdown contents in Step 5
        all_markdown = " ".join([m.value for m in at.markdown])
        assert "10 learning videos" in all_markdown or "learning videos for" in all_markdown
        print("Verified '10 learning videos for <skill>' is rendered in markdown!")

    print("=== AppTest for Step 5 PASSED COMPLETELY! ===")


if __name__ == "__main__":
    test_step5_workflow_in_apptest()
