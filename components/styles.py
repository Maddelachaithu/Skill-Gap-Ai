"""
CSS Styling and Design System for Skill Gap AI
Theme: Dark Navy, Glassmorphism, Indigo & Purple Neon Accents
"""

import streamlit as st


def inject_custom_css():
    """Injects custom CSS to achieve a futuristic dark navy AI dashboard theme."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global reset & typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main background - Dark Navy with subtle purple/indigo ambient glows */
    .stApp {
        background-color: #070B14;
        background-image: 
            radial-gradient(circle at 15% 10%, rgba(99, 102, 241, 0.12) 0%, transparent 40%),
            radial-gradient(circle at 85% 20%, rgba(168, 85, 247, 0.10) 0%, transparent 45%),
            radial-gradient(circle at 50% 90%, rgba(14, 165, 233, 0.08) 0%, transparent 50%),
            linear-gradient(180deg, #070B14 0%, #0B1120 100%);
        background-attachment: fixed;
        color: #E2E8F0;
    }

    /* Streamlit header transparency */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 15, 29, 0.85) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(99, 102, 241, 0.18);
    }

    section[data-testid="stSidebar"] div.stRadio > div {
        gap: 6px;
    }

    /* Sidebar radio button items styled as modern nav pills */
    section[data-testid="stSidebar"] label[data-baseweb="radio"] {
        background: rgba(15, 23, 42, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.04);
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 6px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }

    section[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
        background: rgba(99, 102, 241, 0.15);
        border-color: rgba(99, 102, 241, 0.35);
        transform: translateX(4px);
    }

    /* Streamlit standard buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #9333EA 100%);
        color: #FFFFFF !important;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0.65rem 1.4rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.35);
        transition: all 0.25s ease-in-out;
        letter-spacing: 0.02em;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #4338CA 0%, #6D28D9 50%, #7E22CE 100%);
        box-shadow: 0 6px 22px rgba(124, 58, 237, 0.55);
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.3);
    }

    div.stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.4);
    }

    /* Secondary / outline buttons */
    button[kind="secondary"] {
        background: rgba(15, 23, 42, 0.7) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        color: #C7D2FE !important;
        box-shadow: none !important;
    }

    button[kind="secondary"]:hover {
        background: rgba(99, 102, 241, 0.2) !important;
        border-color: rgba(99, 102, 241, 0.6) !important;
        color: #FFFFFF !important;
    }

    /* Inputs and Textareas */
    input[type="text"], textarea {
        background-color: rgba(13, 20, 38, 0.75) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        border-radius: 10px !important;
        color: #F8FAFC !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.2s ease !important;
        font-family: inherit !important;
    }

    input[type="text"]:focus, textarea:focus {
        border-color: #818CF8 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25) !important;
        background-color: rgba(17, 26, 48, 0.9) !important;
    }

    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.55);
        border: 2px dashed rgba(99, 102, 241, 0.35);
        border-radius: 14px;
        padding: 1.5rem 1rem;
        transition: all 0.25s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: rgba(168, 85, 247, 0.6);
        background: rgba(20, 30, 55, 0.65);
    }

    /* Glassmorphism custom card components */
    .glass-card {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(99, 102, 241, 0.18);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        transition: transform 0.25s ease, border-color 0.25s ease;
    }

    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.38);
    }

    /* Hero header badge */
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #A5B4FC;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    /* Hero main title */
    .hero-title {
        font-size: 2.85rem;
        font-weight: 800;
        line-height: 1.15;
        letter-spacing: -0.025em;
        background: linear-gradient(135deg, #FFFFFF 20%, #C7D2FE 60%, #E879F9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.75rem;
    }

    .hero-subtitle {
        font-size: 1.18rem;
        color: #94A3B8;
        font-weight: 400;
        line-height: 1.6;
        max-width: 680px;
        margin-bottom: 1.75rem;
    }

    /* Feature card */
    .feature-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 1.75rem 1.4rem;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        border-color: rgba(147, 51, 234, 0.45);
        background: rgba(20, 30, 55, 0.75);
        box-shadow: 0 14px 35px -10px rgba(124, 58, 237, 0.3);
    }

    .feature-icon-wrapper {
        width: 52px;
        height: 52px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        margin-bottom: 1.25rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(168, 85, 247, 0.25));
        border: 1px solid rgba(168, 85, 247, 0.35);
    }

    .feature-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 0.5rem;
    }

    .feature-desc {
        font-size: 0.92rem;
        color: #94A3B8;
        line-height: 1.55;
    }

    /* Stepper styles */
    .workflow-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 14px;
        padding: 0.85rem 1.25rem;
        margin-bottom: 2rem;
        overflow-x: auto;
    }

    .step-item {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 0.88rem;
        font-weight: 600;
        color: #64748B;
        white-space: nowrap;
    }

    .step-item.active {
        color: #F8FAFC;
    }

    .step-item.completed {
        color: #34D399;
    }

    .step-circle {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.78rem;
        font-weight: 700;
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #94A3B8;
    }

    .step-item.active .step-circle {
        background: linear-gradient(135deg, #6366F1, #A855F7);
        color: #FFFFFF;
        box-shadow: 0 0 14px rgba(124, 58, 237, 0.6);
        border: none;
    }

    .step-item.completed .step-circle {
        background: rgba(16, 185, 129, 0.2);
        border: 1px solid #10B981;
        color: #34D399;
    }

    .step-divider {
        flex: 1;
        height: 2px;
        background: rgba(255, 255, 255, 0.08);
        margin: 0 12px;
        min-width: 20px;
    }

    .step-divider.completed {
        background: linear-gradient(90deg, #10B981, rgba(99, 102, 241, 0.5));
    }

    .step-label {
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    @media (max-width: 860px) {
        .workflow-container {
            padding: 0.65rem 0.85rem;
            gap: 6px;
        }
        .step-item {
            gap: 6px;
        }
        .step-label {
            font-size: 0.76rem;
        }
        .step-divider {
            margin: 0 6px;
            min-width: 12px;
        }
        .step-circle {
            width: 24px;
            height: 24px;
            font-size: 0.72rem;
        }
    }

    /* Demonstration notice banner */
    .demo-banner {
        background: linear-gradient(90deg, rgba(234, 179, 8, 0.12) 0%, rgba(249, 115, 22, 0.12) 100%);
        border: 1px solid rgba(234, 179, 8, 0.35);
        border-radius: 12px;
        padding: 0.9rem 1.25rem;
        color: #FDE047;
        font-size: 0.88rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* Skill pill tags */
    .pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 9999px;
        font-size: 0.83rem;
        font-weight: 600;
        margin: 4px;
    }

    .pill-match {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #6EE7B7;
    }

    .pill-missing {
        background: rgba(244, 63, 94, 0.15);
        border: 1px solid rgba(244, 63, 94, 0.4);
        color: #FDA4AF;
    }

    .pill-partial {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #FCD34D;
    }

    .pill-tech {
        background: rgba(14, 165, 233, 0.15);
        border: 1px solid rgba(14, 165, 233, 0.4);
        color: #7DD3FC;
    }

    /* Score Radial Card */
    .score-card {
        background: radial-gradient(circle at center, rgba(30, 27, 75, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(168, 85, 247, 0.35);
        border-radius: 18px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.2);
    }

    .score-number {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin: 0.5rem 0;
    }

    .score-label {
        font-size: 0.95rem;
        color: #94A3B8;
        font-weight: 500;
    }

    /* Video card styling */
    .yt-video-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        overflow: hidden;
        transition: all 0.25s ease;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .yt-video-card:hover {
        border-color: rgba(239, 68, 68, 0.5);
        transform: translateY(-4px);
        box-shadow: 0 12px 28px -8px rgba(239, 68, 68, 0.25);
    }

    .yt-thumb-placeholder {
        background: linear-gradient(135deg, #1E1B4B 0%, #0F172A 100%);
        height: 140px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Real YouTube Thumbnail Container */
    .yt-thumb-container {
        position: relative;
        width: 100%;
        height: 155px;
        background: #090D16;
        overflow: hidden;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }

    .yt-thumb-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
        transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .yt-video-card:hover .yt-thumb-img {
        transform: scale(1.06);
    }

    .yt-thumb-overlay {
        position: absolute;
        inset: 0;
        background: rgba(15, 23, 42, 0.35);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.2s ease;
    }

    .yt-video-card:hover .yt-thumb-overlay {
        opacity: 1;
    }

    .yt-duration-badge {
        position: absolute;
        bottom: 8px;
        right: 8px;
        background: rgba(0, 0, 0, 0.85);
        color: #F8FAFC;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 7px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        z-index: 2;
    }

    .yt-play-icon {
        width: 44px;
        height: 44px;
        background: rgba(239, 68, 68, 0.9);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 18px rgba(239, 68, 68, 0.6);
        transition: transform 0.2s ease;
    }

    .yt-video-card:hover .yt-play-icon {
        transform: scale(1.12);
    }

    .yt-desc {
        font-size: 0.78rem;
        color: #94A3B8;
        line-height: 1.42;
        margin-top: 0.45rem;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .yt-body {
        padding: 1rem;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
        justify-content: space-between;
    }

    .yt-title {
        font-size: 0.92rem;
        font-weight: 600;
        color: #F1F5F9;
        margin-bottom: 0.4rem;
        line-height: 1.4;
    }

    .yt-channel {
        font-size: 0.8rem;
        color: #94A3B8;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .yt-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.35);
        color: #FCA5A5;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.75rem;
        text-decoration: none;
        transition: all 0.2s ease;
    }

    .yt-btn:hover {
        background: rgba(239, 68, 68, 0.3);
        color: #FFFFFF;
        border-color: rgba(239, 68, 68, 0.6);
    }

    /* Sidebar Logo Header */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 1.25rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 1.25rem;
    }

    .brand-logo-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }

    .brand-title {
        font-size: 1.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF, #C7D2FE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.01em;
        line-height: 1.2;
    }

    .brand-tagline {
        font-size: 0.76rem;
        color: #818CF8;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    /* Status indicator in sidebar */
    .status-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 8px 12px;
        font-size: 0.82rem;
        color: #94A3B8;
        margin-top: 1rem;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 8px #10B981;
    }
    
    .status-dot.idle {
        background-color: #64748B;
        box-shadow: none;
    }

    /* Custom File Card */
    .file-card {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 1rem 0;
    }

    .file-info {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .file-icon {
        width: 42px;
        height: 42px;
        border-radius: 8px;
        background: rgba(99, 102, 241, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }

    /* Analysis progress card */
    .progress-step-row {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 12px 16px;
        background: rgba(15, 23, 42, 0.5);
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid rgba(255, 255, 255, 0.04);
        transition: all 0.2s ease;
    }

    .progress-step-row.done {
        border-color: rgba(16, 185, 129, 0.3);
        background: rgba(16, 185, 129, 0.08);
    }

    .progress-step-row.current {
        border-color: rgba(99, 102, 241, 0.5);
        background: rgba(99, 102, 241, 0.12);
    }

    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
