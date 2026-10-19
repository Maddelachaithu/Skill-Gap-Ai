# ⚡ Skill Gap AI — AI-Powered Resume Analyzer & Learning Platform

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![YouTube Data API v3](https://img.shields.io/badge/YouTube%20API-v3-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://developers.google.com/youtube/v3)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**Skill Gap AI** is an intelligent, privacy-first career advancement platform that bridges the gap between candidate resumes and modern job postings. It parses resumes (`PDF` and `DOCX`), analyzes technical proficiencies against target role requirements, computes transparent, evidence-grounded alignment scores, and automatically curates **up to 10 high-impact YouTube video tutorials** for every identified skill gap via the official **YouTube Data API v3**.

---

## 🌟 Key Features

- **🚀 5-Stage Guided Analysis Pipeline**
  1. **Upload Resume**: High-fidelity text extraction from multi-page PDFs (PyMuPDF) and Word documents (python-docx) with live metrics (word, character, page count).
  2. **Job Description**: Target role configuration with support for custom postings or one-click sample tech roles.
  3. **Analyze Resume**: Rule-grounded taxonomy engine evaluating technical skills across Languages, Frameworks, Cloud, Databases, DevOps, Security, and Methodologies.
  4. **Skill Gap Report**: Detailed breakdown of **Matching**, **Partial**, and **Missing** competencies, weighted role alignment score (0–100%), and milestone-based action plan.
  5. **Personalized Learning Hub**: Up to **10 verified YouTube learning videos** per missing skill, complete with thumbnails, channel names, descriptions, durations, and direct watch links.

- **🎓 Dynamic YouTube Video Recommendations (10 Videos / Skill)**
  - Queries YouTube Data API v3 for targeted learning tutorials tailored to candidate skill gaps.
  - Returns up to **10 suitable, relevant video cards per skill** without fabricating placeholder links.
  - Smart deduplication by video ID across search responses and distinct skill topics.
  - Quota-conscious retrieval (initial batch retrieval of 25 results, with single-step pagination only when useful).
  - 1-hour Streamlit cache (`@st.cache_data`) to conserve YouTube API quota across page reruns.

- **💎 Futuristic Dark Navy Glassmorphism UI**
  - Custom responsive design with neon purple, indigo, and cyan accents.
  - Interactive stage stepper with step-gating to prevent out-of-order execution.
  - Real-time interactive API tester for exploring custom learning queries on demand.

- **🛡️ 100% Privacy & Zero Resume Leakage**
  - Resume contents and personal identifiable information (PII) are **never sent** to YouTube or third-party servers.
  - Only clean, sanitized skill query strings (e.g., `Splunk tutorial for beginners`) are sent to the YouTube search endpoint.

---

## 🏗️ Architecture & Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend & UI** | [Streamlit](https://streamlit.io/) | Interactive web dashboard, state management, and real-time reruns |
| **Styling & Theme** | Vanilla CSS (Glassmorphism) | Dark navy theme (`#070B14`), ambient glows, responsive 3-column video cards |
| **Document Parsing** | [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/), [python-docx](https://python-docx.readthedocs.io/) | High-accuracy text extraction from PDF and Word documents |
| **Taxonomy & Scoring** | Custom Rule-Based Engine | Deterministic classification without LLM hallucinations or opaque metrics |
| **Video Integration** | [YouTube Data API v3](https://developers.google.com/youtube/v3) | Live video metadata, thumbnails, durations, and channel titles |
| **Testing** | [pytest](https://docs.pytest.org/), Streamlit AppTest | 118+ comprehensive unit, integration, and end-to-end UI workflow tests |

---

## 📁 Repository Structure

```text
Skill-Gap-Ai/
├── app.py                         # Application entrypoint & view router
├── requirements.txt               # Project Python dependencies
├── .env.example                   # Environment variable template
├── .gitignore                     # Git ignore rules (protects .env & cache)
├── backend/                       # Core analytical and integration services
│   ├── __init__.py
│   ├── resume_parser.py           # PDF and DOCX text extraction
│   ├── skills_taxonomy.py         # Technical skill taxonomy & category mappings
│   ├── resume_analyzer.py         # Multi-level skill extraction & matching
│   ├── scoring_service.py         # Weighted alignment score calculator
│   ├── recommendation_service.py  # Personalized roadmap & YouTube query generator
│   ├── workflow_state.py          # Pipeline session state guards
│   └── youtube_service.py         # YouTube Data API v3 client (10-video limit)
├── components/                    # Reusable UI components
│   ├── __init__.py
│   ├── sidebar.py                 # Brand navigation & quick resets
│   ├── stepper.py                 # 5-step interactive workflow stepper
│   └── styles.py                  # Dark navy glassmorphic design system
├── views/                         # Workflow page views
│   ├── __init__.py
│   ├── home.py                    # Landing page & quick-start triggers
│   ├── step1_upload.py            # Resume upload & text preview
│   ├── step2_job_desc.py          # Job posting input & role samples
│   ├── step3_analysis.py          # Pipeline execution & scoring animation
│   ├── step4_report.py            # Alignment score & categorized skill gaps
│   ├── step5_learning.py          # YouTube video dashboard (up to 10 videos/skill)
│   └── about.py                   # System architecture & privacy documentation
├── tests/                         # Automated test suite (118 tests)
│   ├── test_navigation.py
│   ├── test_recommendation_service.py
│   ├── test_resume_analyzer.py
│   ├── test_resume_parser.py
│   ├── test_scoring_service.py
│   ├── test_stage3_integration.py
│   ├── test_step5_learning.py      # Tests for 10-video limits & counts
│   ├── test_stepper.py
│   ├── test_workflow_state.py
│   └── test_youtube_service.py    # Mocked API, deduplication & quota tests
└── scratch/                       # AppTest end-to-end browser simulation tests
    ├── test_apptest_workflow.py
    └── test_apptest_step5.py
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.10, 3.11, 3.12, 3.13)
- **Git**

### 2. Clone the Repository
```bash
git clone https://github.com/Maddelachaithu/Skill-Gap-Ai.git
cd Skill-Gap-Ai
```

### 3. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Your YouTube API Key
Create a `.env` file in the root directory by copying `.env.example`:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and add your YouTube Data API v3 key:
```env
YOUTUBE_API_KEY=your_actual_youtube_api_key_here
```

> **🔑 How to get a free YouTube Data API key:**
> 1. Open the [Google Cloud Console](https://console.cloud.google.com/).
> 2. Create or select a project.
> 3. Go to **APIs & Services > Library**, search for **YouTube Data API v3**, and click **Enable**.
> 4. Go to **APIs & Services > Credentials** and click **Create Credentials > API Key**.
> 5. Paste the key into your `.env` file. (Google provides a free tier of 10,000 units/day).

---

## 🚀 Running the Application

Launch the Streamlit web application:

```bash
streamlit run app.py
```

Open your browser to:
```text
http://localhost:8501
```

---

## 🧪 Running the Test Suite

Skill Gap AI includes 118 automated tests that execute without consuming your YouTube API quota (all external requests are strictly mocked):

```bash
pytest
```

To run with verbose output:
```bash
pytest -v
```

To run the end-to-end Streamlit AppTest simulation:
```bash
python scratch/test_apptest_step5.py
```

---

## 🔒 Privacy & Ethical AI

- **No Remote Storage**: Uploaded resumes are parsed purely in temporary memory during your active session. Files are never stored on external databases.
- **Deterministic Transparency**: Skill matching uses explicit keyword and synonym taxonomy scoring rather than unpredictable black-box generation.
- **Quota & Rate Safeguards**: Built-in 1-hour Streamlit caching and graceful fallbacks ensure that daily API quotas are respected and network dropouts do not crash the user experience.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
