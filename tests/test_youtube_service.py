"""
Unit Tests for Skill Gap AI - YouTube Learning Service
Tests YouTube Data API v3 integration, query execution, metadata parsing,
error scenarios, quota handling, deduplication, and URL generation.
All external network requests are strictly mocked with unittest.mock.
"""

import pytest
from unittest.mock import patch, MagicMock
import requests

from backend.youtube_service import (
    search_youtube_videos,
    search_learning_resources_for_skills,
    get_youtube_api_key,
    parse_iso8601_duration,
    fetch_video_durations,
)


class TestDurationParsing:
    """Tests for ISO 8601 duration conversion to readable format."""

    def test_parse_minutes_and_seconds(self):
        assert parse_iso8601_duration("PT45M12S") == "45:12"
        assert parse_iso8601_duration("PT5M30S") == "5:30"
        assert parse_iso8601_duration("PT0M45S") == "0:45"

    def test_parse_hours_minutes_and_seconds(self):
        assert parse_iso8601_duration("PT1H25M30S") == "1:25:30"
        assert parse_iso8601_duration("PT2H0M0S") == "2:00:00"

    def test_parse_only_hours_or_minutes(self):
        assert parse_iso8601_duration("PT1H") == "1:00:00"
        assert parse_iso8601_duration("PT12M") == "12:00"

    def test_invalid_or_empty_duration_returns_none(self):
        assert parse_iso8601_duration("") is None
        assert parse_iso8601_duration(None) is None
        assert parse_iso8601_duration("invalid") is None


class TestApiKeyHandling:
    """Tests for YouTube API key retrieval and missing key handling."""

    @patch("backend.youtube_service.os.getenv", return_value=None)
    def test_missing_api_key_returns_helpful_error(self, mock_env):
        result = search_youtube_videos("Docker tutorial", "Docker", api_key=None)
        assert result["success"] is False
        assert result["error_type"] == "MISSING_KEY"
        assert "YOUTUBE_API_KEY" in result["message"]
        assert result["videos"] == []

    @patch("backend.youtube_service.os.getenv", return_value="test_mock_api_key_123")
    def test_reads_api_key_from_environment(self, mock_env):
        key = get_youtube_api_key()
        assert key == "test_mock_api_key_123"


class TestYouTubeSearchSuccess:
    """Tests for successful YouTube API search response parsing."""

    @patch("backend.youtube_service.fetch_video_durations")
    @patch("backend.youtube_service.requests.get")
    def test_successful_search_returns_video_metadata(self, mock_get, mock_durations):
        # Mock Search response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": {"videoId": "vid_docker_01"},
                    "snippet": {
                        "title": "Docker Tutorial for Beginners &amp; Pro",
                        "channelTitle": "TechWorld with Nana",
                        "description": "Learn Docker containerization in this comprehensive tutorial.",
                        "thumbnails": {
                            "high": {"url": "https://i.ytimg.com/vi/vid_docker_01/hqdefault.jpg"},
                        },
                    },
                },
                {
                    "id": {"videoId": "vid_docker_02"},
                    "snippet": {
                        "title": "Docker in 100 Seconds",
                        "channelTitle": "Fireship",
                        "description": "Quick overview of Docker.",
                        "thumbnails": {
                            "default": {"url": "https://i.ytimg.com/vi/vid_docker_02/default.jpg"},
                        },
                    },
                },
            ]
        }
        mock_get.return_value = mock_response
        mock_durations.return_value = {
            "vid_docker_01": "2:45:10",
            "vid_docker_02": "2:18",
        }

        result = search_youtube_videos(
            query="Docker tutorial",
            skill_name="Docker",
            api_key="mock_key_valid",
        )

        assert result["success"] is True
        assert result["error_type"] is None
        assert len(result["videos"]) == 2

        v1 = result["videos"][0]
        assert v1["video_id"] == "vid_docker_01"
        assert v1["title"] == "Docker Tutorial for Beginners & Pro"  # Unescaped &amp;
        assert v1["channel_title"] == "TechWorld with Nana"
        assert v1["watch_url"] == "https://www.youtube.com/watch?v=vid_docker_01"
        assert v1["thumbnail_url"] == "https://i.ytimg.com/vi/vid_docker_01/hqdefault.jpg"
        assert v1["duration"] == "2:45:10"
        assert v1["skill_name"] == "Docker"

        v2 = result["videos"][1]
        assert v2["video_id"] == "vid_docker_02"
        assert v2["duration"] == "2:18"

    @patch("backend.youtube_service.requests.get")
    def test_deduplicates_duplicate_video_ids(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"id": {"videoId": "same_id_123"}, "snippet": {"title": "Title 1"}},
                {"id": {"videoId": "same_id_123"}, "snippet": {"title": "Duplicate Title"}},
                {"id": {"videoId": "unique_id_456"}, "snippet": {"title": "Title 2"}},
            ]
        }
        mock_get.return_value = mock_response

        result = search_youtube_videos(
            query="Kubernetes",
            skill_name="Kubernetes",
            api_key="mock_key",
        )

        assert result["success"] is True
        assert len(result["videos"]) == 2
        ids = [v["video_id"] for v in result["videos"]]
        assert ids == ["same_id_123", "unique_id_456"]

    @patch("backend.youtube_service.requests.get")
    def test_empty_search_results_returns_empty_list(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        result = search_youtube_videos(
            query="obscure_nonexistent_skill_xyz",
            skill_name="Obscure",
            api_key="mock_key",
        )

        assert result["success"] is True
        assert result["videos"] == []
        assert result["total_results"] == 0


class TestYouTubeSearchErrorHandling:
    """Tests for API errors, quota exhaustion, network failures, and invalid keys."""

    @patch("backend.youtube_service.requests.get")
    def test_quota_exceeded_handled_gracefully(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "error": {
                "code": 403,
                "message": "The request cannot be completed because you have exceeded your quota.",
                "errors": [{"reason": "quotaExceeded", "domain": "youtube.quota"}],
            }
        }
        mock_get.return_value = mock_response

        result = search_youtube_videos("Docker", "Docker", api_key="mock_key")
        assert result["success"] is False
        assert result["error_type"] == "QUOTA_EXCEEDED"
        assert "quota exceeded" in result["message"].lower()

    @patch("backend.youtube_service.requests.get")
    def test_invalid_api_key_handled_gracefully(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "code": 400,
                "message": "API key not valid. Please pass a valid API key.",
                "errors": [{"reason": "keyInvalid"}],
            }
        }
        mock_get.return_value = mock_response

        result = search_youtube_videos("Python", "Python", api_key="invalid_key")
        assert result["success"] is False
        assert result["error_type"] == "INVALID_KEY"
        assert "invalid" in result["message"].lower()

    @patch("backend.youtube_service.requests.get", side_effect=requests.exceptions.ConnectionError("Connection timed out"))
    def test_network_failure_handled_gracefully(self, mock_get):
        result = search_youtube_videos("Python", "Python", api_key="mock_key")
        assert result["success"] is False
        assert result["error_type"] == "NETWORK_ERROR"
        assert "network error" in result["message"].lower()

    @patch("backend.youtube_service.requests.get")
    def test_invalid_api_response_http_500_handled_gracefully(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = Exception("Not a JSON response")
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        result = search_youtube_videos("GraphQL", "GraphQL", api_key="mock_key")
        assert result["success"] is False
        assert result["error_type"] == "API_ERROR"
        assert "500" in result["message"]

    @patch("backend.youtube_service.requests.get")
    def test_missing_thumbnails_or_optional_metadata_handled_safely(self, mock_get):
        # Snippet without thumbnails, without description
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": {"videoId": "vid_no_thumb"},
                    "snippet": {
                        "title": "Minimal Metadata Video",
                        "channelTitle": "Code Academy",
                        # Missing 'thumbnails'
                        # Missing 'description'
                    },
                }
            ]
        }
        mock_get.return_value = mock_response

        result = search_youtube_videos("PostgreSQL", "PostgreSQL", api_key="mock_key")
        assert result["success"] is True
        assert len(result["videos"]) == 1
        video = result["videos"][0]
        assert video["video_id"] == "vid_no_thumb"
        assert video["title"] == "Minimal Metadata Video"
        assert video["description"] == ""
        # Defaults to YouTube official CDN image
        assert video["thumbnail_url"] == "https://i.ytimg.com/vi/vid_no_thumb/hqdefault.jpg"
        assert video["watch_url"] == "https://www.youtube.com/watch?v=vid_no_thumb"
        assert video["duration"] is None  # Optional duration gracefully None

    @patch("backend.youtube_service.requests.get")
    def test_correct_youtube_urls_format(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"id": {"videoId": "abc123xyz"}, "snippet": {"title": "Test URL Video"}},
            ]
        }
        mock_get.return_value = mock_response

        result = search_youtube_videos("FastAPI", "FastAPI", api_key="mock_key")
        assert result["success"] is True
        video = result["videos"][0]
        assert video["watch_url"] == "https://www.youtube.com/watch?v=abc123xyz"
        assert video["watch_url"].startswith("https://www.youtube.com/watch?v=")

    @patch("backend.youtube_service.fetch_video_durations")
    @patch("backend.youtube_service.requests.get")
    def test_six_or_more_results_retrieved(self, mock_get, mock_durations):
        # Mock 8 video results returned by YouTube Data API v3
        items = [
            {
                "id": {"videoId": f"vid_splunk_{i:02d}"},
                "snippet": {
                    "title": f"Splunk Tutorial #{i}",
                    "channelTitle": "CyberSec Channel",
                    "description": f"Splunk security analysis guide part {i}",
                    "thumbnails": {"high": {"url": f"https://i.ytimg.com/vi/vid_splunk_{i:02d}/hqdefault.jpg"}},
                },
            }
            for i in range(1, 9)
        ]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": items}
        mock_get.return_value = mock_response
        mock_durations.return_value = {f"vid_splunk_{i:02d}": f"{i * 10}:00" for i in range(1, 9)}

        result = search_youtube_videos("Splunk SIEM tutorial", "Splunk", api_key="mock_key")
        assert result["success"] is True
        assert len(result["videos"]) == 8
        assert result["total_results"] == 8
        for idx, v in enumerate(result["videos"], start=1):
            assert v["video_id"] == f"vid_splunk_{idx:02d}"
            assert v["watch_url"] == f"https://www.youtube.com/watch?v=vid_splunk_{idx:02d}"
            assert v["thumbnail_url"] == f"https://i.ytimg.com/vi/vid_splunk_{idx:02d}/hqdefault.jpg"

    @patch("backend.youtube_service.requests.get", side_effect=requests.exceptions.Timeout("Request timed out after 12s"))
    def test_network_timeout_handled_gracefully(self, mock_get):
        result = search_youtube_videos("Wireshark", "Wireshark", api_key="mock_key")
        assert result["success"] is False
        assert result["error_type"] == "TIMEOUT"
        assert "timed out" in result["message"].lower()

    @patch("backend.youtube_service.requests.get")
    def test_malformed_json_response_handled_gracefully(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON in response payload")
        mock_get.return_value = mock_response

        result = search_youtube_videos("Docker", "Docker", api_key="mock_key")
        assert result["success"] is False
        assert result["error_type"] == "MALFORMED_RESPONSE"
        assert "malformed" in result["message"].lower()

    @patch("backend.youtube_service.requests.get")
    def test_valid_thumbnail_and_watch_urls(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": {"videoId": "LbR5cqqaFVk"},
                    "snippet": {
                        "title": "Splunk SIEM Crash Course",
                        "channelTitle": "Free Security Training",
                        "thumbnails": {"high": {"url": "https://i.ytimg.com/vi/LbR5cqqaFVk/hqdefault.jpg"}},
                    },
                }
            ]
        }
        mock_get.return_value = mock_response

        result = search_youtube_videos("Splunk", "Splunk", api_key="mock_key")
        assert result["success"] is True
        video = result["videos"][0]
        assert video["watch_url"] == "https://www.youtube.com/watch?v=LbR5cqqaFVk"
        assert video["thumbnail_url"] == "https://i.ytimg.com/vi/LbR5cqqaFVk/hqdefault.jpg"
        assert video["watch_url"].startswith("https://www.youtube.com/watch?v=")
        assert video["thumbnail_url"].startswith("https://")

    @patch("backend.youtube_service.search_youtube_videos")
    def test_batch_skill_search_deduplicates_globally(self, mock_search):
        # First skill returns vid_1, vid_2
        mock_search.side_effect = [
            {"success": True, "videos": [{"video_id": "vid_1"}, {"video_id": "vid_2"}]},
            {"success": True, "videos": [{"video_id": "vid_3"}]},
        ]

        skills_to_query = [
            {"skill_name": "Docker", "query": "Docker tutorial"},
            {"skill_name": "Kubernetes", "query": "Kubernetes tutorial"},
        ]

        batch_result = search_learning_resources_for_skills(skills_to_query, api_key="mock_key")
        assert batch_result["success"] is True
        assert len(batch_result["results_by_skill"]) == 2


class TestYouTubeTenVideoRecommendations:
    """Comprehensive tests for the 10-video recommendation limit, pagination, and deduplication."""

    @patch("backend.youtube_service.fetch_video_durations")
    @patch("backend.youtube_service.requests.get")
    def test_ten_videos_returned_when_ten_or_more_suitable_results_exist(self, mock_get, mock_durations):
        """Verify up to 10 videos are selected when the API returns 15 suitable results."""
        items = [
            {
                "id": {"videoId": f"vid_test_{i:02d}"},
                "snippet": {
                    "title": f"Tutorial Video #{i}",
                    "channelTitle": f"Channel {i}",
                    "description": f"Description for video {i}",
                    "thumbnails": {"high": {"url": f"https://i.ytimg.com/vi/vid_test_{i:02d}/hqdefault.jpg"}},
                },
            }
            for i in range(1, 16)
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"items": items}
        mock_get.return_value = mock_resp
        mock_durations.return_value = {f"vid_test_{i:02d}": "15:00" for i in range(1, 16)}

        result = search_youtube_videos("Python tutorial", "Python", api_key="valid_key")

        assert result["success"] is True
        assert len(result["videos"]) == 10
        assert result["total_results"] == 10
        for idx, video in enumerate(result["videos"], start=1):
            assert video["video_id"] == f"vid_test_{idx:02d}"
            assert video["watch_url"] == f"https://www.youtube.com/watch?v=vid_test_{idx:02d}"
            assert video["skill_name"] == "Python"
            assert video["duration"] == "15:00"

    @patch("backend.youtube_service.fetch_video_durations")
    @patch("backend.youtube_service.requests.get")
    def test_fewer_than_ten_results_handled_correctly(self, mock_get, mock_durations):
        """Verify when fewer than 10 results exist (e.g. 4), exactly 4 are returned without dummy links."""
        items = [
            {
                "id": {"videoId": f"vid_splunk_{i}"},
                "snippet": {
                    "title": f"Splunk Tutorial {i}",
                    "channelTitle": "Splunk Academy",
                    "description": f"Learn Splunk basics {i}",
                    "thumbnails": {"high": {"url": f"https://i.ytimg.com/vi/vid_splunk_{i}/hqdefault.jpg"}},
                },
            }
            for i in range(1, 5)
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"items": items}  # No nextPageToken
        mock_get.return_value = mock_resp
        mock_durations.return_value = {f"vid_splunk_{i}": "10:00" for i in range(1, 5)}

        result = search_youtube_videos("Splunk SIEM", "Splunk", api_key="valid_key")

        assert result["success"] is True
        assert len(result["videos"]) == 4
        assert result["total_results"] == 4
        assert result["videos"][0]["video_id"] == "vid_splunk_1"
        assert result["videos"][3]["video_id"] == "vid_splunk_4"

    @patch("backend.youtube_service.fetch_video_durations")
    @patch("backend.youtube_service.requests.get")
    def test_pagination_fetches_up_to_ten_when_initial_page_has_fewer_than_ten(self, mock_get, mock_durations):
        """Verify pagination is used to retrieve up to 10 videos if the first page returned only 6."""
        page1_items = [
            {
                "id": {"videoId": f"p1_vid_{i}"},
                "snippet": {"title": f"Page 1 Video {i}", "channelTitle": "DevOps"},
            }
            for i in range(1, 7)
        ]
        page2_items = [
            {
                "id": {"videoId": f"p2_vid_{i}"},
                "snippet": {"title": f"Page 2 Video {i}", "channelTitle": "DevOps"},
            }
            for i in range(1, 8)
        ]

        resp1 = MagicMock()
        resp1.status_code = 200
        resp1.json.return_value = {"items": page1_items, "nextPageToken": "page_2_token_abc"}

        resp2 = MagicMock()
        resp2.status_code = 200
        resp2.json.return_value = {"items": page2_items}

        mock_get.side_effect = [resp1, resp2]
        mock_durations.return_value = {}

        result = search_youtube_videos("Docker tutorial", "Docker", api_key="valid_key")

        assert result["success"] is True
        assert len(result["videos"]) == 10
        assert mock_get.call_count == 2
        # Check that page 2 request used pageToken
        second_call_kwargs = mock_get.call_args_list[1]
        assert second_call_kwargs.kwargs["params"]["pageToken"] == "page_2_token_abc"

    @patch("backend.youtube_service.fetch_video_durations")
    @patch("backend.youtube_service.requests.get")
    def test_pagination_not_triggered_when_ten_results_available_on_first_page(self, mock_get, mock_durations):
        """Verify pagination is skipped when the first page already has 10 suitable results, conserving quota."""
        page1_items = [
            {
                "id": {"videoId": f"p1_vid_{i}"},
                "snippet": {"title": f"Page 1 Video {i}", "channelTitle": "Cloud"},
            }
            for i in range(1, 13)
        ]
        resp1 = MagicMock()
        resp1.status_code = 200
        resp1.json.return_value = {"items": page1_items, "nextPageToken": "should_not_be_used"}
        mock_get.return_value = resp1
        mock_durations.return_value = {}

        result = search_youtube_videos("AWS tutorial", "AWS", api_key="valid_key")

        assert result["success"] is True
        assert len(result["videos"]) == 10
        assert mock_get.call_count == 1  # Only 1 request made

    @patch("backend.youtube_service.requests.get")
    def test_deduplication_removes_duplicate_video_ids(self, mock_get):
        """Verify identical video IDs within response are deduplicated."""
        items = [
            {"id": {"videoId": "dup_vid_1"}, "snippet": {"title": "Tutorial A"}},
            {"id": {"videoId": "dup_vid_1"}, "snippet": {"title": "Tutorial A Duplicate"}},
            {"id": {"videoId": "dup_vid_2"}, "snippet": {"title": "Tutorial B"}},
            {"id": {"videoId": "dup_vid_2"}, "snippet": {"title": "Tutorial B Duplicate"}},
            {"id": {"videoId": "unique_vid_3"}, "snippet": {"title": "Tutorial C"}},
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"items": items}
        mock_get.return_value = mock_resp

        result = search_youtube_videos("GraphQL", "GraphQL", api_key="valid_key")

        assert result["success"] is True
        assert len(result["videos"]) == 3
        assert [v["video_id"] for v in result["videos"]] == ["dup_vid_1", "dup_vid_2", "unique_vid_3"]

    @patch("backend.youtube_service.requests.get")
    def test_existing_video_ids_excluded(self, mock_get):
        """Verify videos already seen in prior skills are excluded."""
        items = [
            {"id": {"videoId": "already_seen_1"}, "snippet": {"title": "Seen 1"}},
            {"id": {"videoId": "fresh_vid_2"}, "snippet": {"title": "Fresh 2"}},
            {"id": {"videoId": "fresh_vid_3"}, "snippet": {"title": "Fresh 3"}},
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"items": items}
        mock_get.return_value = mock_resp

        result = search_youtube_videos(
            "Terraform",
            "Terraform",
            api_key="valid_key",
            existing_video_ids={"already_seen_1"},
        )

        assert result["success"] is True
        assert len(result["videos"]) == 2
        assert [v["video_id"] for v in result["videos"]] == ["fresh_vid_2", "fresh_vid_3"]

    @patch("backend.youtube_service.fetch_video_durations")
    @patch("backend.youtube_service.requests.get")
    def test_pagination_network_failure_preserves_page_one_results(self, mock_get, mock_durations):
        """Verify network timeout during pagination degrades gracefully, preserving page 1 results."""
        page1_items = [
            {
                "id": {"videoId": f"p1_vid_{i}"},
                "snippet": {"title": f"Page 1 Video {i}", "channelTitle": "Channel"},
            }
            for i in range(1, 6)
        ]
        resp1 = MagicMock()
        resp1.status_code = 200
        resp1.json.return_value = {"items": page1_items, "nextPageToken": "tok_err"}

        # Page 2 fails with network timeout
        mock_get.side_effect = [resp1, requests.exceptions.Timeout("Timeout on page 2")]
        mock_durations.return_value = {}

        result = search_youtube_videos("Kubernetes", "Kubernetes", api_key="valid_key")

        assert result["success"] is True
        assert len(result["videos"]) == 5
        assert result["total_results"] == 5

    @patch("backend.youtube_service.search_youtube_videos")
    def test_separate_skills_receive_own_results(self, mock_search):
        """Verify separate skills each receive their own unique video recommendations."""
        mock_search.side_effect = [
            {
                "success": True,
                "videos": [{"video_id": f"docker_{i}", "skill_name": "Docker"} for i in range(1, 11)],
            },
            {
                "success": True,
                "videos": [{"video_id": f"k8s_{i}", "skill_name": "Kubernetes"} for i in range(1, 11)],
            },
        ]

        skills = [
            {"skill_name": "Docker", "query": "Docker tutorial for beginners"},
            {"skill_name": "Kubernetes", "query": "Kubernetes tutorial for beginners"},
        ]

        batch_result = search_learning_resources_for_skills(skills, api_key="mock_key")

        assert batch_result["success"] is True
        assert "Docker" in batch_result["results_by_skill"]
        assert "Kubernetes" in batch_result["results_by_skill"]
        assert len(batch_result["results_by_skill"]["Docker"]["videos"]) == 10
        assert len(batch_result["results_by_skill"]["Kubernetes"]["videos"]) == 10



