"""
Unit Tests for Skill Gap AI - Resume Analyzer Engine
Tests skill extraction, normalization, evidence retrieval, classification, and edge cases.
"""

import pytest
from backend.resume_analyzer import (
    analyze_resume_against_job,
    extract_skills_from_job_description,
    evaluate_skill_against_resume,
    find_context_sentence,
)
from backend.skills_taxonomy import normalize_skill_name


class TestSkillTaxonomyAndNormalization:
    """Test normalization and alias mapping."""

    def test_alias_normalization(self):
        assert normalize_skill_name("postgres") == "PostgreSQL"
        assert normalize_skill_name("postgresql") == "PostgreSQL"
        assert normalize_skill_name("reactjs") == "React"
        assert normalize_skill_name("k8s") == "Kubernetes"
        assert normalize_skill_name("golang") == "Go"
        assert normalize_skill_name("unknown_tool") == "unknown_tool"

    def test_case_insensitivity_in_taxonomy(self):
        assert normalize_skill_name("pYtHoN") == "Python"
        assert normalize_skill_name("DOCKER") == "Docker"
        assert normalize_skill_name("aws") == "AWS"


class TestJobSkillExtraction:
    """Test extraction of required skills and importance weighting from job descriptions."""

    def test_extract_software_engineering_skills(self):
        job_text = """
        Position: Backend Engineer
        Requirements:
        - Required: 4+ years of Python and PostgreSQL experience.
        - Must have deep knowledge of Docker and REST APIs.
        - Nice to have: Familiarity with Kubernetes and GraphQL.
        """
        skills = extract_skills_from_job_description(job_text)
        skill_names = [s["name"] for s in skills]

        assert "Python" in skill_names
        assert "PostgreSQL" in skill_names
        assert "Docker" in skill_names
        assert "REST APIs" in skill_names
        assert "Kubernetes" in skill_names
        assert "GraphQL" in skill_names

        # Verify importance tagging
        python_skill = next(s for s in skills if s["name"] == "Python")
        assert python_skill["importance"] == "High"

        graphql_skill = next(s for s in skills if s["name"] == "GraphQL")
        assert graphql_skill["importance"] == "Low"

    def test_extract_data_analytics_skills(self):
        job_text = """
        Data Scientist needed.
        Requirements:
        - Must have proficiency in Machine Learning, Pandas, and SQL.
        - Preferred: Tableau for business reporting and PyTorch for neural networks.
        """
        skills = extract_skills_from_job_description(job_text)
        skill_names = [s["name"] for s in skills]

        assert "Machine Learning" in skill_names
        assert "Pandas" in skill_names
        assert "SQL" in skill_names
        assert "Tableau" in skill_names
        assert "PyTorch" in skill_names

    def test_extract_cybersecurity_skills(self):
        job_text = """
        Security Analyst Role.
        Must have hands-on experience in Penetration Testing, SIEM monitoring, and Network Security.
        Nice to have: Wireshark packet capture analysis.
        """
        skills = extract_skills_from_job_description(job_text)
        skill_names = [s["name"] for s in skills]

        assert "Penetration Testing" in skill_names
        assert "SIEM" in skill_names
        assert "Network Security" in skill_names
        assert "Wireshark" in skill_names

    def test_duplicate_skills_deduplicated(self):
        job_text = "Looking for a PostgreSQL developer with Postgres database skills and PSQL mastery."
        skills = extract_skills_from_job_description(job_text)
        postgres_instances = [s for s in skills if s["name"] == "PostgreSQL"]
        assert len(postgres_instances) == 1


class TestResumeComparisonAndClassification:
    """Test classification of skills: Matching, Partial, Missing, Needs Verification."""

    def test_matching_skill_with_verbatim_evidence(self):
        resume = "Built microservices using Python and FastAPI serving 100k daily requests."
        req = {"name": "Python", "importance": "High", "category": "Languages"}

        result = evaluate_skill_against_resume(req, resume)
        assert result["status"] == "Matching"
        assert result["evidence"] is not None
        assert "Python" in result["evidence"]
        assert "FastAPI" in result["evidence"]

    def test_missing_skill_without_evidence(self):
        resume = "Front-end developer working exclusively with HTML and CSS."
        req = {"name": "Kubernetes", "importance": "High", "category": "DevOps"}

        result = evaluate_skill_against_resume(req, resume)
        assert result["status"] == "Missing"
        assert result["evidence"] is None
        assert "No direct or closely related evidence" in result["explanation"]

    def test_partial_match_via_related_skill(self):
        # Candidate has Docker, but Job requires Kubernetes (related skill)
        resume = "Containerized full-stack applications using Docker Compose and Dockerfile optimization."
        req = {"name": "Kubernetes", "importance": "High", "category": "DevOps"}

        result = evaluate_skill_against_resume(req, resume)
        assert result["status"] == "Partial"
        assert result["evidence"] is not None
        assert "Docker" in result["evidence"]
        assert "related proficiency in Docker" in result["explanation"]

    def test_case_insensitive_matching(self):
        resume = "PROFICIENT IN DOCKER, FASTAPI, AND POSTGRESQL."
        req = {"name": "Docker", "importance": "Medium", "category": "DevOps"}

        result = evaluate_skill_against_resume(req, resume)
        assert result["status"] == "Matching"
        assert "DOCKER" in result["evidence"].upper()


class TestFullAnalysisPipeline:
    """Tests for the complete analyze_resume_against_job function."""

    def test_empty_resume_returns_error(self):
        res = analyze_resume_against_job("", "Python developer required")
        assert res["success"] is False
        assert "Resume text is empty" in res["error"]

    def test_empty_job_returns_error(self):
        res = analyze_resume_against_job("Alex Python dev", "")
        assert res["success"] is False
        assert "Job description is empty" in res["error"]

    def test_synthetic_end_to_end_analysis(self):
        sample_resume = """
        Taylor Swift
        Senior Software Developer
        Skills: Python, React, PostgreSQL, Docker, Git
        Experience:
        - 5+ years of software development experience architecting web applications.
        - Designed and deployed FastAPI backend services with PostgreSQL database.
        - Containerized local developer environments using Docker Compose.
        """

        sample_job = """
        Role: Senior Cloud Full-Stack Engineer
        Requirements:
        - Required: 4+ years of Python and React experience.
        - Required: PostgreSQL relational database design.
        - Required: Kubernetes container orchestration in production.
        - Nice to have: GraphQL and Redis caching.
        """

        result = analyze_resume_against_job(sample_resume, sample_job, job_title="Senior Cloud Full-Stack Engineer")

        assert result["success"] is True
        assert result["error"] is None
        assert len(result["matching_skills"]) >= 3  # Python, React, PostgreSQL

        matching_names = [s["name"] for s in result["matching_skills"]]
        assert "Python" in matching_names
        assert "React" in matching_names
        assert "PostgreSQL" in matching_names

        # Kubernetes should be Partial (candidate has Docker)
        partial_names = [s["name"] for s in result["partial_skills"]]
        assert "Kubernetes" in partial_names

        # Redis or GraphQL should be Missing
        missing_names = [s["name"] for s in result["missing_skills"]]
        assert any(s in missing_names for s in ["GraphQL", "Redis"])

        # Score calculation is present
        scoring = result["scoring"]
        assert 0 < scoring["score_percentage"] < 100
        assert scoring["total_requirements"] > 0
        assert len(result["actionable_recommendations"]) > 0
