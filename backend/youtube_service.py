"""
YouTube Learning Service for Skill Gap AI
Integrates with the official YouTube Data API v3 to search for educational videos,
fetch real video metadata (thumbnails, titles, channels, direct URLs, durations),
and provide graceful error handling for quota, network, and missing key scenarios.
"""

import os
import re
import html
from typing import Dict, List, Any, Optional

import requests
from dotenv import load_dotenv

# Base YouTube Data API v3 endpoints
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

# Target number of videos to display per skill when available
TARGET_VIDEOS_PER_SKILL = 10
MAX_SEARCH_RESULTS = 25


def get_youtube_api_key() -> Optional[str]:
    """
    Retrieves the YouTube Data API key from environment variables,
    .env file, or Streamlit secrets configuration.
    Never returns hardcoded keys.
    """
    # 1. Try dotenv loading
    load_dotenv()

    # 2. Check standard environment variable
    api_key = os.getenv("YOUTUBE_API_KEY")
    if api_key and api_key.strip():
        return api_key.strip()

    # 3. Check Streamlit secrets or session_state if running inside Streamlit
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "YOUTUBE_API_KEY" in st.secrets:
            key_from_secrets = st.secrets["YOUTUBE_API_KEY"]
            if key_from_secrets and key_from_secrets.strip():
                return key_from_secrets.strip()
        if hasattr(st, "session_state") and st.session_state.get("custom_youtube_api_key"):
            key_from_session = st.session_state["custom_youtube_api_key"]
            if key_from_session and key_from_session.strip():
                return key_from_session.strip()
    except Exception:
        pass

    return None


def parse_iso8601_duration(duration_str: str) -> Optional[str]:
    """
    Converts ISO 8601 duration format (e.g., 'PT1H25M30S', 'PT45M12S', 'PT3M')
    into a human-readable duration string ('1:25:30' or '45:12').
    Returns None if format is missing or invalid without fabricating values.
    """
    if not duration_str or not duration_str.startswith("PT"):
        return None

    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
    if not match:
        return None

    hours, minutes, seconds = match.groups()
    h = int(hours) if hours else 0
    m = int(minutes) if minutes else 0
    s = int(seconds) if seconds else 0

    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def fetch_video_durations(video_ids: List[str], api_key: str) -> Dict[str, str]:
    """
    Fetches exact video durations for a batch of video IDs using YouTube's videos endpoint.
    Returns a dictionary mapping video_id to formatted duration string.
    Fails gracefully returning empty dict without raising exceptions.
    """
    if not video_ids or not api_key:
        return {}

    try:
        params = {
            "part": "contentDetails",
            "id": ",".join(video_ids[:50]),
            "key": api_key,
        }
        response = requests.get(YOUTUBE_VIDEOS_URL, params=params, timeout=8)
        if response.status_code == 200:
            data = response.json()
            durations = {}
            for item in data.get("items", []):
                vid = item.get("id")
                raw_dur = item.get("contentDetails", {}).get("duration")
                formatted = parse_iso8601_duration(raw_dur)
                if vid and formatted:
                    durations[vid] = formatted
            return durations
    except Exception:
        # Ignore duration lookup failures; duration remains optional
        pass
    return {}


def search_youtube_videos(
    query: str,
    skill_name: str,
    max_results: int = MAX_SEARCH_RESULTS,
    api_key: Optional[str] = None,
    existing_video_ids: Optional[set] = None,
    target_count: int = TARGET_VIDEOS_PER_SKILL,
) -> Dict[str, Any]:
    """
    Searches YouTube Data API v3 for educational tutorials for a given skill query.
    Extracts real metadata: video_id, title, channel, description, thumbnail_url,
    direct watch URL, and exact duration.

    Selects up to target_count (default 10) most relevant suitable results.
    Requests up to 25 results initially, and uses pagination if fewer than target_count
    suitable results are available and a nextPageToken exists.
    
    Handles missing keys, quota limits, network errors, and empty responses gracefully.
    """
    key = api_key or get_youtube_api_key()

    if not key:
        return {
            "success": False,
            "error_type": "MISSING_KEY",
            "message": "YouTube API key not found. Please set YOUTUBE_API_KEY in your .env file or environment.",
            "videos": [],
            "skill_name": skill_name,
            "query": query,
        }

    if not query or not query.strip():
        return {
            "success": False,
            "error_type": "EMPTY_QUERY",
            "message": "Search query cannot be empty.",
            "videos": [],
            "skill_name": skill_name,
            "query": query,
        }

    params = {
        "part": "snippet",
        "type": "video",
        "q": query.strip(),
        "maxResults": min(max_results, 50),
        "order": "relevance",
        "relevanceLanguage": "en",
        "safeSearch": "strict",
        "key": key,
    }

    try:
        response = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=12)
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error_type": "TIMEOUT",
            "message": "YouTube API request timed out. Please verify your network connection and retry.",
            "videos": [],
            "skill_name": skill_name,
            "query": query,
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error_type": "NETWORK_ERROR",
            "message": f"Network error connecting to YouTube API: {str(e)}",
            "videos": [],
            "skill_name": skill_name,
            "query": query,
        }

    # Handle HTTP error responses
    if response.status_code != 200:
        try:
            err_data = response.json().get("error", {})
            err_code = err_data.get("code", response.status_code)
            errors_list = err_data.get("errors", [])
            reason = errors_list[0].get("reason", "") if errors_list else ""
            err_msg = err_data.get("message", "YouTube API error")
        except Exception:
            err_code = response.status_code
            reason = ""
            err_msg = response.text

        if response.status_code == 403 and "quota" in reason.lower():
            return {
                "success": False,
                "error_type": "QUOTA_EXCEEDED",
                "message": (
                    "YouTube Data API daily quota exceeded for this key. "
                    "Google provides 10,000 units/day free, which resets at midnight Pacific Time."
                ),
                "videos": [],
                "skill_name": skill_name,
                "query": query,
            }
        elif response.status_code in [400, 403] and ("keyInvalid" in reason or "invalid" in err_msg.lower()):
            return {
                "success": False,
                "error_type": "INVALID_KEY",
                "message": "The provided YouTube API key is invalid or restricted. Please verify your Google Cloud Console credentials.",
                "videos": [],
                "skill_name": skill_name,
                "query": query,
            }
        else:
            return {
                "success": False,
                "error_type": "API_ERROR",
                "message": f"YouTube API returned HTTP {response.status_code}: {err_msg}",
                "videos": [],
                "skill_name": skill_name,
                "query": query,
            }

    # Parse successful response safely
    try:
        data = response.json()
    except Exception as e:
        return {
            "success": False,
            "error_type": "MALFORMED_RESPONSE",
            "message": f"Malformed JSON response received from YouTube API: {str(e)}",
            "videos": [],
            "skill_name": skill_name,
            "query": query,
        }

    items = data.get("items", [])

    seen_ids = set(existing_video_ids) if existing_video_ids else set()
    raw_videos = []

    def _parse_item(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        id_obj = item.get("id", {})
        vid = id_obj.get("videoId")
        if not vid or not isinstance(vid, str) or vid in seen_ids:
            return None

        snippet = item.get("snippet", {})
        raw_title = snippet.get("title", "")
        if not raw_title or not raw_title.strip():
            return None

        seen_ids.add(vid)

        raw_channel = snippet.get("channelTitle", "YouTube Channel")
        raw_desc = snippet.get("description", "")

        # Unescape HTML entities (e.g. &amp;, &#39;, &quot;)
        clean_title = html.unescape(raw_title).strip()
        clean_channel = html.unescape(raw_channel).strip()
        clean_desc = html.unescape(raw_desc).strip()

        # Extract best available thumbnail URL
        thumbnails = snippet.get("thumbnails", {})
        thumb_url = (
            thumbnails.get("high", {}).get("url")
            or thumbnails.get("medium", {}).get("url")
            or thumbnails.get("default", {}).get("url")
            or f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
        )

        watch_url = f"https://www.youtube.com/watch?v={vid}"

        return {
            "video_id": vid,
            "title": clean_title,
            "channel_title": clean_channel,
            "description": clean_desc,
            "thumbnail_url": thumb_url,
            "watch_url": watch_url,
            "skill_name": skill_name,
            "duration": None,  # Will be populated below if available
        }

    for item in items:
        entry = _parse_item(item)
        if entry:
            raw_videos.append(entry)

    # If fewer than target_count suitable results are found and nextPageToken exists,
    # use pagination to fetch additional suitable results within API quota
    next_page_token = data.get("nextPageToken")
    if len(raw_videos) < target_count and next_page_token:
        page2_params = dict(params)
        page2_params["pageToken"] = next_page_token
        page2_params["maxResults"] = min(max_results, 25)
        try:
            p2_response = requests.get(YOUTUBE_SEARCH_URL, params=page2_params, timeout=10)
            if p2_response.status_code == 200:
                p2_data = p2_response.json()
                for item in p2_data.get("items", []):
                    entry = _parse_item(item)
                    if entry:
                        raw_videos.append(entry)
                        if len(raw_videos) >= target_count:
                            break
        except Exception:
            # Gracefully retain the results already collected from initial request
            pass

    # Select the top most relevant suitable results up to target_count
    selected_videos = raw_videos[:target_count]
    selected_ids = [v["video_id"] for v in selected_videos]

    # Fetch accurate durations using videos endpoint
    if selected_ids and key:
        durations_map = fetch_video_durations(selected_ids, key)
        for v in selected_videos:
            v["duration"] = durations_map.get(v["video_id"])

    return {
        "success": True,
        "error_type": None,
        "message": None,
        "skill_name": skill_name,
        "query": query,
        "total_results": len(selected_videos),
        "videos": selected_videos,
    }


def search_learning_resources_for_skills(
    skills_with_queries: List[Dict[str, str]],
    api_key: Optional[str] = None,
    target_count: int = TARGET_VIDEOS_PER_SKILL,
) -> Dict[str, Any]:
    """
    Searches YouTube for multiple skills, deduplicating video IDs across queries
    and aiming for up to 10 relevant videos per skill when available.
    
    skills_with_queries: List of dicts, each having:
      {"skill_name": "Docker", "query": "Docker tutorial for beginners"}
    """
    results_by_skill: Dict[str, Dict[str, Any]] = {}
    global_seen_video_ids = set()
    overall_success = True
    first_error = None

    for item in skills_with_queries:
        skill = item.get("skill_name", "Skill")
        query = item.get("query", f"{skill} tutorial for beginners")

        search_res = search_youtube_videos(
            query=query,
            skill_name=skill,
            max_results=MAX_SEARCH_RESULTS,
            api_key=api_key,
            existing_video_ids=global_seen_video_ids,
            target_count=target_count,
        )

        if not search_res["success"]:
            overall_success = False
            if not first_error:
                first_error = search_res

            results_by_skill[skill] = search_res
            # If quota is exhausted or key is invalid, break immediately to avoid wasting quota/requests
            if search_res.get("error_type") in ["QUOTA_EXCEEDED", "INVALID_KEY", "MISSING_KEY"]:
                break
        else:
            # Register seen video IDs
            for v in search_res["videos"]:
                global_seen_video_ids.add(v["video_id"])
            results_by_skill[skill] = search_res

    return {
        "success": overall_success,
        "results_by_skill": results_by_skill,
        "first_error": first_error,
        "total_skills_searched": len(results_by_skill),
    }
