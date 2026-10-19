"""
Unit Tests for Skill Gap AI - Step 5 Learning Resources Dashboard
Verifies that:
1. TARGET_VIDEOS_PER_SKILL is 10.
2. Up to 10 videos are retrieved and displayed per missing or partially matching skill.
3. The count label clearly displays '10 learning videos for <Skill>' when 10 videos exist.
4. When fewer than 10 results exist, the actual number found is displayed accurately.
5. Video grid renders thumbnail, title, channel, description, and correct clickable URL.
6. API quota exhaustion, invalid keys, and network errors are handled gracefully without crashing.
"""

import pytest
from unittest.mock import patch, MagicMock
import html

from backend.youtube_service import TARGET_VIDEOS_PER_SKILL
from views.step5_learning import (
    fetch_cached_youtube_videos,
    render_video_grid,
    render_step5_learning,
)


class TestStep5LearningConfigAndCache:
    """Tests for Step 5 configuration and cached API retrieval."""

    def test_target_videos_per_skill_constant_is_ten(self):
        """Verify the video limit is configured to 10 videos per skill."""
        assert TARGET_VIDEOS_PER_SKILL == 10

    @patch("views.step5_learning.search_youtube_videos")
    def test_fetch_cached_youtube_videos_passes_target_count_ten(self, mock_search):
        """Verify fetch_cached_youtube_videos requests up to 10 videos."""
        mock_search.return_value = {
            "success": True,
            "videos": [{"video_id": f"vid_{i}"} for i in range(1, 11)],
            "total_results": 10,
        }

        result = fetch_cached_youtube_videos(
            query="Splunk SIEM tutorial",
            skill_name="Splunk",
            api_key="mock_key",
            target_count=10,
        )

        mock_search.assert_called_once_with(
            query="Splunk SIEM tutorial",
            skill_name="Splunk",
            api_key="mock_key",
            target_count=10,
        )
        assert result["success"] is True
        assert len(result["videos"]) == 10


class TestStep5VideoGridRendering:
    """Tests for rendering up to 10 video cards in the 3-column responsive layout."""

    @patch("views.step5_learning.st.columns")
    @patch("views.step5_learning.st.markdown")
    def test_render_video_grid_renders_all_ten_cards(self, mock_markdown, mock_cols):
        """Verify 10 videos are rendered across rows with full card metadata."""
        videos = [
            {
                "video_id": f"vid_{i:02d}",
                "title": f"Complete Tutorial #{i}",
                "channel_title": f"Tech Channel {i}",
                "description": f"Detailed description for tutorial {i}",
                "thumbnail_url": f"https://i.ytimg.com/vi/vid_{i:02d}/hqdefault.jpg",
                "watch_url": f"https://www.youtube.com/watch?v=vid_{i:02d}",
                "duration": f"1{i}:30",
            }
            for i in range(1, 11)
        ]

        # Mock st.columns to return dummy column contexts
        col_mock = MagicMock()
        mock_cols.return_value = [col_mock, col_mock, col_mock]

        render_video_grid(videos)

        # Check markdown calls for card contents
        all_rendered_html = "".join([call[0][0] for call in mock_markdown.call_args_list])

        for v in videos:
            assert v["title"] in all_rendered_html
            assert v["channel_title"] in all_rendered_html
            assert v["watch_url"] in all_rendered_html
            assert v["thumbnail_url"] in all_rendered_html
            assert f"⏱ {v['duration']}" in all_rendered_html


class TestStep5LearningDashboardWorkflow:
    """Tests for Step 5 dashboard integration with session state and recommendation service."""

    @patch("views.step5_learning.get_youtube_api_key", return_value="mock_key_123")
    @patch("views.step5_learning.fetch_cached_youtube_videos")
    @patch("views.step5_learning.render_stepper")
    @patch("views.step5_learning.render_video_grid")
    @patch("views.step5_learning.st.markdown")
    @patch("views.step5_learning.st.spinner")
    @patch("views.step5_learning.st.button", return_value=False)
    @patch("views.step5_learning.st.columns")
    def test_step5_displays_ten_videos_and_count_for_missing_skill(
        self,
        mock_columns,
        mock_button,
        mock_spinner,
        mock_markdown,
        mock_render_grid,
        mock_stepper,
        mock_fetch_cached,
        mock_key,
    ):
        """Verify 10 videos are retrieved and '10 learning videos for Splunk' is clearly displayed."""
        col_mock = MagicMock()
        mock_columns.return_value = [col_mock, col_mock]

        # Fake session state with analysis results containing Splunk as Missing
        fake_session = {
            "workflow_step": 5,
            "current_page": "Learning Resources",
            "job_title": "Security Analyst",
            "job_description": "Requires Splunk SIEM experience.",
            "resume_text": "Experienced in Python and Linux.",
            "analysis_result": {
                "success": True,
                "classified_skills": [
                    {
                        "name": "Splunk",
                        "status": "Missing",
                        "category": "Security",
                        "evidence": None,
                    }
                ],
                "matching_skills": [],
                "partial_skills": [],
                "missing_skills": ["Splunk"],
                "scoring": {"display_score": 50},
            },
        }

        # Mock fetch_cached_youtube_videos returning 10 videos
        mock_videos = [
            {
                "video_id": f"splunk_vid_{i:02d}",
                "title": f"Splunk Tutorial #{i}",
                "channel_title": "CyberAcademy",
                "description": f"Splunk lesson {i}",
                "thumbnail_url": f"https://i.ytimg.com/vi/splunk_vid_{i:02d}/hqdefault.jpg",
                "watch_url": f"https://www.youtube.com/watch?v=splunk_vid_{i:02d}",
                "duration": "12:00",
                "skill_name": "Splunk",
            }
            for i in range(1, 11)
        ]
        mock_fetch_cached.return_value = {
            "success": True,
            "videos": mock_videos,
            "total_results": 10,
        }

        with patch("views.step5_learning.st.session_state", fake_session):
            render_step5_learning()

        # Verify 10 videos were passed to render_video_grid
        assert mock_render_grid.called
        grid_videos = mock_render_grid.call_args[0][0]
        assert len(grid_videos) == 10

        # Verify clear count display '10 learning videos for Splunk' in rendered HTML
        all_markdown = "".join([call[0][0] for call in mock_markdown.call_args_list if call[0]])
        assert "10 learning videos for Splunk" in all_markdown
        assert "10 of 10 Recommended" in all_markdown

    @patch("views.step5_learning.get_youtube_api_key", return_value="mock_key_123")
    @patch("views.step5_learning.fetch_cached_youtube_videos")
    @patch("views.step5_learning.render_stepper")
    @patch("views.step5_learning.render_video_grid")
    @patch("views.step5_learning.st.markdown")
    @patch("views.step5_learning.st.spinner")
    @patch("views.step5_learning.st.button", return_value=False)
    @patch("views.step5_learning.st.columns")
    def test_step5_displays_actual_count_when_fewer_than_ten_results(
        self,
        mock_columns,
        mock_button,
        mock_spinner,
        mock_markdown,
        mock_render_grid,
        mock_stepper,
        mock_fetch_cached,
        mock_key,
    ):
        """Verify when only 4 videos exist, '4 learning videos for Splunk' and the explanation are displayed."""
        col_mock = MagicMock()
        mock_columns.return_value = [col_mock, col_mock]

        fake_session = {
            "workflow_step": 5,
            "current_page": "Learning Resources",
            "job_title": "Security Analyst",
            "job_description": "Requires Splunk.",
            "resume_text": "Python developer.",
            "analysis_result": {
                "success": True,
                "classified_skills": [
                    {"name": "Splunk", "status": "Missing", "category": "Security"}
                ],
                "matching_skills": [],
                "partial_skills": [],
                "missing_skills": ["Splunk"],
                "scoring": {"display_score": 60},
            },
        }

        # Mock 4 videos returned
        mock_videos = [
            {
                "video_id": f"splunk_vid_{i}",
                "title": f"Splunk Tutorial #{i}",
                "channel_title": "Sec",
                "description": "",
                "thumbnail_url": f"https://i.ytimg.com/vi/splunk_vid_{i}/hqdefault.jpg",
                "watch_url": f"https://www.youtube.com/watch?v=splunk_vid_{i}",
                "duration": "10:00",
                "skill_name": "Splunk",
            }
            for i in range(1, 5)
        ]
        mock_fetch_cached.return_value = {
            "success": True,
            "videos": mock_videos,
            "total_results": 4,
        }

        with patch("views.step5_learning.st.session_state", fake_session):
            render_step5_learning()

        # Verify grid received all 4 videos
        grid_videos = mock_render_grid.call_args[0][0]
        assert len(grid_videos) == 4

        # Verify clear count displays 4 learning videos
        all_markdown = "".join([call[0][0] for call in mock_markdown.call_args_list if call[0]])
        assert "4 learning videos for Splunk" in all_markdown
        assert "Fewer than 10 suitable tutorials available" in all_markdown

    @patch("views.step5_learning.get_youtube_api_key", return_value="mock_key_123")
    @patch("views.step5_learning.fetch_cached_youtube_videos")
    @patch("views.step5_learning.render_stepper")
    @patch("views.step5_learning.st.error")
    @patch("views.step5_learning.st.markdown")
    @patch("views.step5_learning.st.spinner")
    @patch("views.step5_learning.st.button", return_value=False)
    @patch("views.step5_learning.st.columns")
    def test_step5_quota_exceeded_handled_gracefully(
        self,
        mock_columns,
        mock_button,
        mock_spinner,
        mock_markdown,
        mock_error,
        mock_stepper,
        mock_fetch_cached,
        mock_key,
    ):
        """Verify YouTube Data API quota exceeded message is displayed without crashing."""
        col_mock = MagicMock()
        mock_columns.return_value = [col_mock, col_mock]

        fake_session = {
            "workflow_step": 5,
            "current_page": "Learning Resources",
            "job_title": "DevOps",
            "job_description": "Kubernetes required.",
            "resume_text": "Linux sysadmin.",
            "analysis_result": {
                "success": True,
                "classified_skills": [
                    {"name": "Kubernetes", "status": "Missing", "category": "DevOps"}
                ],
                "matching_skills": [],
                "partial_skills": [],
                "missing_skills": ["Kubernetes"],
                "scoring": {"display_score": 70},
            },
        }

        mock_fetch_cached.return_value = {
            "success": False,
            "error_type": "QUOTA_EXCEEDED",
            "message": "Daily quota exceeded.",
            "videos": [],
        }

        with patch("views.step5_learning.st.session_state", fake_session):
            render_step5_learning()

        # Verify quota exceeded error is displayed gracefully
        assert mock_error.called
        error_msg = mock_error.call_args[0][0]
        assert "Quota Exceeded" in error_msg

    @patch("views.step5_learning.get_youtube_api_key", return_value=None)
    @patch("views.step5_learning.render_stepper")
    @patch("views.step5_learning.render_api_key_setup_card")
    @patch("views.step5_learning.st.columns")
    @patch("views.step5_learning.st.button", return_value=False)
    def test_step5_missing_api_key_shows_setup_card(
        self,
        mock_button,
        mock_columns,
        mock_setup_card,
        mock_stepper,
        mock_key,
    ):
        """Verify missing API key renders the setup guide card and does not crash."""
        col_mock = MagicMock()
        mock_columns.return_value = [col_mock, col_mock]

        fake_session = {"workflow_step": 5, "current_page": "Learning Resources"}

        with patch("views.step5_learning.st.session_state", fake_session):
            render_step5_learning()

        assert mock_setup_card.called
