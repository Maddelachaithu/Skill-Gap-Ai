"""
Step 5: YouTube Learning Resources Dashboard for Skill Gap AI
Integrates official YouTube Data API v3 to search real educational tutorials
for identified skill gaps, display accurate metadata (thumbnails, channels, durations),
and provide caching, quota management, and graceful error handling.
"""

from typing import List, Dict, Any, Optional
import html
import streamlit as st

from components.stepper import render_stepper
from backend.youtube_service import (
    get_youtube_api_key,
    search_youtube_videos,
    TARGET_VIDEOS_PER_SKILL,
)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_cached_youtube_videos(
    query: str,
    skill_name: str,
    api_key: str,
    target_count: int = TARGET_VIDEOS_PER_SKILL,
) -> Dict[str, Any]:
    """
    Cached wrapper around search_youtube_videos.
    Caches search results for 1 hour to prevent redundant API calls on page reruns
    and conserve YouTube Data API v3 quota.
    """
    return search_youtube_videos(
        query=query,
        skill_name=skill_name,
        api_key=api_key,
        target_count=target_count,
    )


def render_api_key_setup_card():
    """
    Renders an informative, glassmorphic setup guide when YOUTUBE_API_KEY is not configured.
    Prevents showing fake/dummy links and provides an interactive key entry option.
    """
    st.markdown(
        """
        <div class="glass-card" style="border-color: rgba(239, 68, 68, 0.45); background: rgba(30, 27, 75, 0.55); margin-bottom: 2rem;">
            <div style="display: flex; align-items: flex-start; gap: 14px;">
                <div style="font-size: 2.2rem; line-height: 1;">🔑</div>
                <div style="flex: 1;">
                    <div style="font-size: 1.25rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.35rem;">
                        YouTube Data API Key Required
                    </div>
                    <p style="color: #CBD5E1; font-size: 0.92rem; line-height: 1.55; margin-bottom: 1rem;">
                        To provide <strong>real, live video recommendations</strong> for your missing skills, Skill Gap AI integrates directly with the 
                        official <strong>YouTube Data API v3</strong>. No API key is currently detected in your environment.
                    </p>
                    <div style="background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">
                        <div style="font-weight: 700; color: #E0E7FF; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            📋 Quick Setup Steps (Free Google Cloud Tier):
                        </div>
                        <ol style="color: #94A3B8; font-size: 0.86rem; line-height: 1.6; margin: 0; padding-left: 1.25rem;">
                            <li>Visit the <a href="https://console.cloud.google.com/" target="_blank" style="color: #818CF8; font-weight: 600;">Google Cloud Console</a> and create or select a project.</li>
                            <li>Navigate to <strong>APIs & Services &gt; Library</strong>, search for <strong>YouTube Data API v3</strong>, and click <strong>Enable</strong>.</li>
                            <li>Go to <strong>APIs & Services &gt; Credentials</strong> and click <strong>Create Credentials &gt; API Key</strong>.</li>
                            <li>Create a <code>.env</code> file in the project root containing: <code style="color: #F43F5E;">YOUTUBE_API_KEY=your_api_key_here</code>.</li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Interactive Session Key Input for testing/demo without editing local files
    with st.expander("⚡ Or Enter an API Key for This Session (Instant Activation)", expanded=True):
        st.markdown(
            "<p style='color: #94A3B8; font-size: 0.85rem; margin-bottom: 0.5rem;'>"
            "Paste your YouTube Data API v3 key below to query live videos immediately. "
            "Your key is held strictly in temporary session memory and is never logged or committed."
            "</p>",
            unsafe_allow_html=True,
        )
        col_inp, col_btn = st.columns([3, 1])
        with col_inp:
            entered_key = st.text_input(
                "YouTube Data API Key",
                type="password",
                placeholder="AIzaSy...",
                label_visibility="collapsed",
                key="session_api_key_input",
            )
        with col_btn:
            if st.button("Activate Key 🚀", type="primary", use_container_width=True):
                if entered_key and entered_key.strip():
                    st.session_state["custom_youtube_api_key"] = entered_key.strip()
                    st.cache_data.clear()
                    st.toast("✅ YouTube API key activated for this session!", icon="🔑")
                    st.rerun()
                else:
                    st.warning("Please enter a valid non-empty API key.")


def render_video_grid(videos: List[Dict[str, Any]]):
    """Renders a responsive 3-column grid of YouTube video cards."""
    num_cols = 3
    for row_start in range(0, len(videos), num_cols):
        row_items = videos[row_start : row_start + num_cols]
        cols = st.columns(num_cols)

        for col_idx, video in enumerate(row_items):
            with cols[col_idx]:
                vid_title = video.get("title", "Untitled Tutorial")
                vid_channel = video.get("channel_title", "YouTube Channel")
                vid_desc = video.get("description", "")
                vid_thumb = video.get("thumbnail_url", "")
                vid_url = video.get("watch_url", f"https://www.youtube.com/watch?v={video.get('video_id')}")
                vid_dur = video.get("duration")

                # Duration badge markup (only if duration was retrieved)
                duration_badge_html = (
                    f'<span class="yt-duration-badge">⏱ {vid_dur}</span>'
                    if vid_dur
                    else ""
                )

                # Description markup (optional snippet)
                desc_html = (
                    f'<div class="yt-desc">{html.escape(vid_desc)}</div>'
                    if vid_desc
                    else ""
                )

                st.markdown(
                    f"""
                    <div class="yt-video-card">
                        <div class="yt-thumb-container">
                            <img src="{vid_thumb}" alt="{html.escape(vid_title)}" class="yt-thumb-img" loading="lazy" />
                            <div class="yt-thumb-overlay">
                                <div class="yt-play-icon">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
                                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                                    </svg>
                                </div>
                            </div>
                            {duration_badge_html}
                        </div>
                        <div class="yt-body">
                            <div>
                                <div class="yt-title" title="{html.escape(vid_title)}">
                                    {html.escape(vid_title)}
                                </div>
                                <div class="yt-channel">
                                    <span>📺 {html.escape(vid_channel)}</span>
                                </div>
                                {desc_html}
                            </div>
                            <a href="{vid_url}" target="_blank" rel="noopener noreferrer" class="yt-btn">
                                <span>Watch on YouTube</span>
                                <span>↗</span>
                            </a>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_step5_learning():
    """Renders Step 5: Your Personalized Learning Hub with live YouTube recommendations."""
    render_stepper(5)

    # Official Page Heading
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div class="hero-badge">
                <span>Stage 5: Live YouTube Integration</span>
            </div>
            <h2 style="font-size: 2rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.4rem;">
                Your Personalized Learning Hub
            </h2>
            <p style="color: #94A3B8; font-size: 0.98rem; max-width: 820px;">
                High-impact, educational video tutorials dynamically retrieved via the official YouTube Data API v3 
                to target your exact skill gaps and learning priorities.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Check for active API key
    active_api_key = get_youtube_api_key()

    # If API key is missing, show setup instructions and session key input
    if not active_api_key:
        render_api_key_setup_card()
        # Per requirements: "Do not create fake video results or placeholder links when the API is unavailable."
        st.write("")
        col_back, col_home = st.columns([1, 1])
        with col_back:
            if st.button("⬅️ Back to Improvement Recommendations", use_container_width=True):
                st.session_state["workflow_step"] = 4
                st.session_state["current_page"] = "Skill Gap Report"
                st.rerun()
        with col_home:
            if st.button("🔄 Start New Analysis", use_container_width=True, type="primary"):
                from backend.workflow_state import reset_workflow_state
                reset_workflow_state(st.session_state)
                st.rerun()
        return

    # Extract missing/partial skills and learning queries from actual session state
    analysis_data = st.session_state.get("analysis_result")
    skills_to_query: List[Dict[str, Any]] = []

    if analysis_data and analysis_data.get("success", False):
        from backend.recommendation_service import generate_recommendations_for_analysis
        rec_output = generate_recommendations_for_analysis(
            analysis_result=analysis_data,
            job_description=st.session_state.get("job_description", ""),
            resume_text=st.session_state.get("resume_text", ""),
            job_title=st.session_state.get("job_title", ""),
        )
        learning_order = rec_output.get("learning_plan", {}).get("learning_order", [])

        for item in learning_order:
            skills_to_query.append({
                "skill_name": item["skill_name"],
                "query": item["youtube_query"],
                "priority": item.get("priority", "Medium"),
                "status": item.get("status", "Missing"),
                "focus": item.get("focus", ""),
                "project": item.get("project_suggestion", ""),
            })

    # Case A: Real analysis exists with skill gaps
    if analysis_data and analysis_data.get("success", False) and skills_to_query:
        total_gaps = len(skills_to_query)
        high_pri_count = sum(1 for s in skills_to_query if s.get("priority") == "High")
        missing_count = sum(1 for s in skills_to_query if s.get("status") == "Missing")
        partial_count = sum(1 for s in skills_to_query if s.get("status") == "Partial")

        st.markdown(
            f"""
            <div class="glass-card" style="margin-bottom: 1.5rem; border-color: rgba(99, 102, 241, 0.4);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 0.75rem;">
                    <div>
                        <span style="font-weight: 800; color: #F8FAFC; font-size: 1.15rem;">
                            🎯 Addressing {total_gaps} Identified Skill Gaps from Your Resume
                        </span>
                        <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 2px;">
                            Prioritized sequence based on job description weighting and prerequisite hierarchy
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <span class="pill pill-missing">🚨 {missing_count} Missing</span>
                        <span class="pill pill-partial">⚡ {partial_count} Partial</span>
                        <span class="pill pill-tech">🔥 {high_pri_count} High Priority</span>
                    </div>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 0.5rem; padding-top: 0.75rem; border-top: 1px solid rgba(255, 255, 255, 0.06);">
                    {" ".join([f'<span style="background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.35); color: #C7D2FE; font-size: 0.8rem; padding: 3px 10px; border-radius: 6px; font-weight: 600;">#{idx+1} {s["skill_name"]} ({s["priority"]} Pri)</span>' for idx, s in enumerate(skills_to_query)])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Case B: Analysis exists but 0 skill gaps (100% match)
    elif analysis_data and analysis_data.get("success", False) and not skills_to_query:
        st.markdown(
            """
            <div class="glass-card" style="margin-bottom: 1.5rem; border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.08);">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <span style="font-size: 2rem;">🎉</span>
                    <div>
                        <div style="font-weight: 800; color: #6EE7B7; font-size: 1.15rem;">
                            Outstanding Alignment — No Skill Gaps Identified!
                        </div>
                        <div style="color: #94A3B8; font-size: 0.9rem; margin-top: 2px;">
                            Your resume demonstrates alignment with all technical requirements extracted from this job description.
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_rpt, col_rst = st.columns([1, 1])
        with col_rpt:
            if st.button("⬅️ View Detailed Analysis Report", use_container_width=True):
                st.session_state["workflow_step"] = 4
                st.session_state["current_page"] = "Skill Gap Report"
                st.rerun()
        with col_rst:
            if st.button("🔄 Analyze Another Job Description", use_container_width=True, type="primary"):
                from backend.workflow_state import reset_workflow_state
                reset_workflow_state(st.session_state)
                st.rerun()
        return

    # Case C: No analysis in session state
    else:
        st.markdown(
            """
            <div class="glass-card" style="margin-bottom: 1.5rem; border-color: rgba(14, 165, 233, 0.35);">
                <div style="display: flex; align-items: flex-start; gap: 14px;">
                    <span style="font-size: 2rem;">💡</span>
                    <div style="flex: 1;">
                        <div style="font-weight: 800; color: #F8FAFC; font-size: 1.15rem;">
                            No Active Resume Analysis in Current Session
                        </div>
                        <div style="color: #94A3B8; font-size: 0.9rem; line-height: 1.5; margin-top: 4px; margin-bottom: 1rem;">
                            To view personalized video recommendations mapped to your real skill deficits, 
                            please upload your resume and paste a job description. Real reports never use hardcoded example skills.
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_start, col_dummy = st.columns([1, 1])
        with col_start:
            if st.button("🚀 Start Resume Analysis (Step 1)", type="primary", use_container_width=True):
                st.session_state["current_page"] = "Resume Analysis"
                st.session_state["pending_page"] = "Resume Analysis"
                st.session_state["workflow_step"] = 1
                st.rerun()

        # Interactive quick-query tool to test the live API immediately
        with st.expander("🧪 Test Live YouTube API with a Custom Skill Query", expanded=True):
            st.markdown(
                "<p style='color: #94A3B8; font-size: 0.85rem; margin-bottom: 0.6rem;'>"
                "Search live educational tutorials directly with your connected YouTube Data API key:"
                "</p>",
                unsafe_allow_html=True,
            )
            col_q, col_act = st.columns([3, 1])
            with col_q:
                custom_skill_input = st.text_input(
                    "Topic or Skill",
                    value="Splunk SIEM tutorial for beginners",
                    placeholder="e.g. Splunk SIEM tutorial for beginners",
                    label_visibility="collapsed",
                    key="live_test_query_input",
                )
            with col_act:
                do_search = st.button("Search YouTube 🔍", use_container_width=True, type="primary")

            if do_search or st.session_state.get("ran_test_search"):
                st.session_state["ran_test_search"] = True
                with st.spinner(f"🔍 Searching YouTube for '{custom_skill_input}'..."):
                    test_res = fetch_cached_youtube_videos(
                        query=custom_skill_input,
                        skill_name="Custom Query",
                        api_key=active_api_key,
                        target_count=TARGET_VIDEOS_PER_SKILL,
                    )
                if test_res.get("success", False) and test_res.get("videos"):
                    count = len(test_res["videos"])
                    st.markdown(
                        f"<div style='color: #10B981; font-size: 0.88rem; font-weight: 600; margin: 0.75rem 0;'>"
                        f"✅ Found {count} live tutorial{'s' if count != 1 else ''} via YouTube Data API v3:</div>",
                        unsafe_allow_html=True,
                    )
                    render_video_grid(test_res["videos"][:TARGET_VIDEOS_PER_SKILL])
                elif test_res.get("success", False):
                    st.info("No videos found matching this query.", icon="ℹ️")
                else:
                    st.error(f"Search failed: {test_res.get('message')}", icon="❌")

        return

    # API Controls: Refresh cache and session key status
    col_ctrl1, col_ctrl2 = st.columns([3, 1])
    with col_ctrl1:
        st.markdown(
            "<span style='color: #10B981; font-weight: 600; font-size: 0.88rem;'>● Live YouTube Data API Connected</span> "
            "<span style='color: #64748B; font-size: 0.82rem;'>(Cached locally to optimize API quota)</span>",
            unsafe_allow_html=True,
        )
    with col_ctrl2:
        if st.button("🔄 Refresh All Videos", help="Clear cached YouTube results and refetch", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Track seen video IDs globally across all skills to eliminate duplicates
    global_seen_video_ids = set()
    quota_exceeded_encountered = False

    # Iterate over each skill and render educational video tutorial cards
    for s_idx, skill_info in enumerate(skills_to_query):
        skill_name = skill_info["skill_name"]
        search_query = skill_info["query"]
        priority = skill_info.get("priority", "Medium")
        status = skill_info.get("status", "Missing")
        focus = skill_info.get("focus", "")

        pri_color = "#F43F5E" if priority == "High" else "#F59E0B" if priority == "Medium" else "#10B981"

        # Section Header for Skill
        st.markdown(
            f"""
            <div class="glass-card" style="margin-top: 1.75rem; margin-bottom: 1rem; border-left: 4px solid {pri_color};">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 1.35rem; font-weight: 800; color: #F8FAFC;">
                                {skill_name}
                            </span>
                            <span style="background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.4); color: #C7D2FE; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">
                                {priority} Priority
                            </span>
                            <span style="background: rgba(244, 63, 94, 0.15); border: 1px solid rgba(244, 63, 94, 0.35); color: #FDA4AF; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">
                                {status}
                            </span>
                        </div>
                        <div style="font-size: 0.84rem; color: #94A3B8; margin-top: 4px;">
                            {focus if focus else f'Educational video tutorials to master {skill_name}'}
                        </div>
                    </div>
                    <div style="font-size: 0.78rem; color: #64748B; font-family: 'JetBrains Mono', monospace;">
                        Search: "{html.escape(search_query)}"
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # If quota was exceeded in a prior skill, skip making further calls
        if quota_exceeded_encountered:
            st.warning(
                f"Skipping live search for {skill_name} due to YouTube Data API daily quota limit.",
                icon="⚠️",
            )
            continue

        # Execute cached API query with loading spinner
        with st.spinner(f"🔍 Searching YouTube Data API v3 for {skill_name} tutorials..."):
            result = fetch_cached_youtube_videos(
                query=search_query,
                skill_name=skill_name,
                api_key=active_api_key,
                target_count=TARGET_VIDEOS_PER_SKILL,
            )

        # Handle API Error Scenarios gracefully
        if not result.get("success", False):
            err_type = result.get("error_type", "API_ERROR")
            err_msg = result.get("message", "An error occurred fetching videos.")

            if err_type == "QUOTA_EXCEEDED":
                quota_exceeded_encountered = True
                st.error(
                    f"**YouTube Data API Quota Exceeded:** {err_msg}\n\n"
                    "Google provides 10,000 free quota units per day for YouTube Data API v3. "
                    "The quota will automatically reset at midnight Pacific Time.",
                    icon="🚫",
                )
                if st.button(f"Retry {skill_name}", key=f"retry_quota_{skill_name}"):
                    st.cache_data.clear()
                    st.rerun()
                break

            elif err_type == "INVALID_KEY":
                st.error(
                    f"**Invalid YouTube API Key:** {err_msg}\n\n"
                    "Please check that your API key is enabled for YouTube Data API v3 in Google Cloud Console.",
                    icon="❌",
                )
                if st.button("Re-enter API Key", key="re_enter_key"):
                    if "custom_youtube_api_key" in st.session_state:
                        del st.session_state["custom_youtube_api_key"]
                    st.rerun()
                break

            else:
                st.warning(f"**Search Issue:** {err_msg}", icon="⚠️")
                if st.button(f"🔄 Retry Search for {skill_name}", key=f"retry_{skill_name}"):
                    st.cache_data.clear()
                    st.rerun()
                continue

        # Filter out globally seen duplicate video IDs
        raw_videos = result.get("videos", [])
        unique_videos = []
        for v in raw_videos:
            vid = v["video_id"]
            if vid not in global_seen_video_ids:
                global_seen_video_ids.add(vid)
                unique_videos.append(v)

        # Handle empty search results
        if not unique_videos:
            st.info(
                f"No suitable educational video tutorials found for '{search_query}'. "
                "Try searching YouTube directly with broader terms.",
                icon="ℹ️",
            )
            continue

        # Aim to display up to 10 relevant videos per skill when available
        display_videos = unique_videos[:TARGET_VIDEOS_PER_SKILL]
        num_found = len(display_videos)

        # Clear count header line, for example "10 learning videos for Splunk"
        if num_found >= TARGET_VIDEOS_PER_SKILL:
            count_label = f"{num_found} learning videos for {skill_name}"
            badge_style = "background: rgba(99, 102, 241, 0.18); border: 1px solid rgba(99, 102, 241, 0.4); color: #C7D2FE;"
        else:
            count_label = f"{num_found} learning video{'s' if num_found != 1 else ''} for {skill_name}"
            badge_style = "background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.35); color: #FCD34D;"

        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem; padding: 0 4px;">
                <div style="font-size: 1rem; font-weight: 700; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.1rem;">🎥</span>
                    <span>{count_label}</span>
                </div>
                <span style="{badge_style} font-size: 0.78rem; font-weight: 600; padding: 3px 10px; border-radius: 6px;">
                    {num_found} of {TARGET_VIDEOS_PER_SKILL} Recommended
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Render 3-column video grid using helper function
        render_video_grid(display_videos)

        # Display result count note, explaining if fewer than 10 were available
        if num_found < TARGET_VIDEOS_PER_SKILL:
            st.markdown(
                f"<div style='font-size: 0.82rem; color: #F59E0B; margin-top: -0.25rem; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 6px; background: rgba(245, 158, 11, 0.08); padding: 8px 14px; border-radius: 8px; border: 1px solid rgba(245, 158, 11, 0.25);'>"
                f"<span>ℹ️</span> <span>Found {num_found} learning video{'s' if num_found != 1 else ''} for {skill_name}. (Fewer than {TARGET_VIDEOS_PER_SKILL} suitable tutorials available without including unrelated videos).</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='text-align: right; font-size: 0.78rem; color: #94A3B8; margin-top: -0.25rem; margin-bottom: 1.25rem;'>"
                f"Showing top {num_found} verified tutorials for {skill_name}"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown("---")

    # Workflow Navigation Footer
    col_back, col_reset = st.columns([1, 1])

    with col_back:
        if st.button("⬅️ Back to Improvement Recommendations", use_container_width=True, type="secondary"):
            st.session_state["workflow_step"] = 4
            st.session_state["current_page"] = "Skill Gap Report"
            st.rerun()

    with col_reset:
        if st.button("🔄 Start New Analysis", use_container_width=True, type="primary"):
            from backend.workflow_state import reset_workflow_state
            reset_workflow_state(st.session_state)
            st.rerun()
