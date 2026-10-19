"""
Unit Tests for Skill Gap AI - Navigation & Workflow Routing
Verifies that:
1. Clicking Start Resume Analysis from Home updates session state to Resume Analysis.
2. Clicking sidebar radio items updates current_page.
3. Programmatic page changes synchronize the sidebar radio widget state.
4. Resetting workflow sets both current_page and sidebar_nav_radio to Resume Analysis.
"""

import pytest
from unittest.mock import MagicMock, patch

from views.home import on_start_resume_analysis
from components.sidebar import on_sidebar_nav_change
from backend.workflow_state import reset_workflow_state


class TestNavigationCallbacks:
    """Tests for in-page button callbacks and sidebar radio sync."""

    def test_home_start_analysis_callback_sets_correct_state(self):
        fake_session = {
            "current_page": "Home",
            "sidebar_nav_radio": "🏠 Home",
            "workflow_step": 1,
        }
        with patch("views.home.st.session_state", fake_session):
            on_start_resume_analysis()
            assert fake_session["current_page"] == "Resume Analysis"
            assert fake_session["sidebar_nav_radio"] == "🚀 Resume Analysis"
            assert fake_session["workflow_step"] == 1

    def test_sidebar_nav_change_callback_syncs_current_page(self):
        fake_session = {
            "current_page": "Home",
            "sidebar_nav_radio": "🚀 Resume Analysis",
        }
        with patch("components.sidebar.st.session_state", fake_session):
            on_sidebar_nav_change()
            assert fake_session["current_page"] == "Resume Analysis"

    def test_sidebar_nav_change_to_report(self):
        fake_session = {
            "current_page": "Home",
            "sidebar_nav_radio": "📊 Skill Gap Report",
        }
        with patch("components.sidebar.st.session_state", fake_session):
            on_sidebar_nav_change()
            assert fake_session["current_page"] == "Skill Gap Report"

    def test_sidebar_nav_change_to_learning(self):
        fake_session = {
            "current_page": "Home",
            "sidebar_nav_radio": "🎥 Learning Resources",
        }
        with patch("components.sidebar.st.session_state", fake_session):
            on_sidebar_nav_change()
            assert fake_session["current_page"] == "Learning Resources"

    def test_reset_workflow_state_syncs_navigation(self):
        fake_session = {
            "current_page": "Skill Gap Report",
            "sidebar_nav_radio": "📊 Skill Gap Report",
            "workflow_step": 4,
            "resume_uploaded": True,
            "resume_text": "Sample resume text",
            "job_title": "Engineer",
            "job_description": "Sample job",
            "analysis_completed": True,
        }
        reset_workflow_state(fake_session)
        assert fake_session["current_page"] == "Resume Analysis"
        assert fake_session["sidebar_nav_radio"] == "🚀 Resume Analysis"
        assert fake_session["workflow_step"] == 1
        assert fake_session["resume_uploaded"] is False
        assert fake_session["resume_text"] == ""

    def test_pending_page_syncs_sidebar_radio_in_sidebar_render(self):
        """Verify render_sidebar applies pending_page before creating radio widget."""
        from components.sidebar import render_sidebar
        fake_session = {
            "current_page": "Home",
            "pending_page": "Resume Analysis",
            "sidebar_nav_radio": "🏠 Home",
            "resume_uploaded": False,
            "resume_text": "",
            "job_description": "",
            "job_title": "",
            "workflow_step": 1,
        }
        with patch("components.sidebar.st.session_state", fake_session), \
             patch("components.sidebar.st.sidebar"), \
             patch("components.sidebar.st.markdown"), \
             patch("components.sidebar.st.caption"), \
             patch("components.sidebar.st.radio") as mock_radio, \
             patch("components.sidebar.st.button", return_value=False):
            render_sidebar()
            # pending_page should have been popped and applied
            assert "pending_page" not in fake_session
            assert fake_session["current_page"] == "Resume Analysis"
            assert fake_session["sidebar_nav_radio"] == "🚀 Resume Analysis"
            mock_radio.assert_called_once()
            # index is None because sidebar_nav_radio in session state controls selection without warning
            assert mock_radio.call_args[1]["index"] is None
            assert mock_radio.call_args[1]["key"] == "sidebar_nav_radio"

    def test_reset_workflow_state_with_locked_widget_state(self):
        """Simulate Streamlit's behavior where sidebar_nav_radio raises an exception if modified."""
        class LockedSession(dict):
            def __setitem__(self, key, value):
                if key == "sidebar_nav_radio":
                    raise RuntimeError("st.session_state['sidebar_nav_radio'] cannot be modified after widget is instantiated.")
                super().__setitem__(key, value)

        locked_state = LockedSession({
            "current_page": "Skill Gap Report",
            "sidebar_nav_radio": "📊 Skill Gap Report",
            "workflow_step": 4,
            "resume_uploaded": True,
            "resume_text": "Sample",
            "job_title": "Role",
            "job_description": "Job",
            "analysis_completed": True,
        })
        # Should not raise exception
        reset_workflow_state(locked_state)
        assert locked_state["current_page"] == "Resume Analysis"
        assert locked_state["pending_page"] == "Resume Analysis"
        assert locked_state["workflow_step"] == 1

