"""
Unit Tests for Skill Gap AI - Recommendation Service
Tests recommendation generation, priority calculation, learning plan ordering,
deduplication, and edge cases using synthetic test fixtures.
"""

import pytest
from backend.recommendation_service import (
    generate_recommendations_for_analysis,
    calculate_skill_priority,
    generate_single_recommendation,
    build_personalized_learning_plan,
    generate_youtube_query,
)


class TestPriorityCalculation:
    """Tests for deterministic and transparent priority calculation."""

    def test_high_importance_job_skill_is_high_priority(self):
        skill = {"name": "Kubernetes", "importance": "High", "status": "Missing"}
        job = "Looking for a DevOps Engineer. Required: Kubernetes production management."
        priority, reason = calculate_skill_priority(skill, job, "")
        assert priority == "High"
        assert "core requirement" in reason or "explicitly" in reason

    def test_repeated_job_skill_gets_high_priority(self):
        skill = {"name": "Docker", "importance": "Medium", "status": "Missing"}
        job = "We use Docker extensively. Experience with Dockerfiles and Docker Compose is expected."
        priority, reason = calculate_skill_priority(skill, job, "")
        assert priority == "High"
        assert "multiple times" in reason or "emphasized" in reason

    def test_low_importance_job_skill_is_low_priority(self):
        skill = {"name": "GraphQL", "importance": "Low", "status": "Missing"}
        job = "Nice to have: familiarity with GraphQL."
        priority, reason = calculate_skill_priority(skill, job, "")
        assert priority == "Low"
        assert "preferred or nice-to-have" in reason

    def test_partial_skill_gets_medium_or_high_priority(self):
        # Candidate has related skill in resume
        skill = {"name": "Kubernetes", "importance": "Medium", "status": "Partial"}
        job = "Deploy microservices onto clusters."
        resume = "Built containers using Docker."
        priority, reason = calculate_skill_priority(skill, job, resume)
        assert priority in ["High", "Medium"]
        assert "related" in reason or "requirement" in reason


class TestSingleRecommendationGeneration:
    """Tests for individual skill recommendation outputs."""

    def test_missing_skill_structure(self):
        skill = {
            "name": "Docker",
            "importance": "High",
            "status": "Missing",
            "category": "Cloud & DevOps",
            "evidence": None,
        }
        rec = generate_single_recommendation(skill, "Required: Docker", "")

        assert rec["skill_name"] == "Docker"
        assert rec["status"] == "Missing"
        assert rec["priority"] == "High"
        assert "why_it_matters" in rec and len(rec["why_it_matters"]) > 10
        assert "what_to_learn" in rec and len(rec["what_to_learn"]) > 10
        assert len(rec["practical_exercises"]) >= 1
        assert "suggested_project" in rec
        assert "youtube_search_query" in rec
        assert "tutorial" in rec["youtube_search_query"].lower()
        assert rec["current_demonstration"] == "No sufficient evidence found in uploaded resume."

    def test_partial_skill_structure_includes_evidence(self):
        skill = {
            "name": "Kubernetes",
            "importance": "Medium",
            "status": "Partial",
            "category": "Cloud & DevOps",
            "evidence": "Experienced in containerization with Docker Compose.",
        }
        rec = generate_single_recommendation(skill, "Kubernetes required", "Docker Compose experience")

        assert rec["skill_name"] == "Kubernetes"
        assert rec["status"] == "Partial"
        assert "Docker Compose" in rec["current_demonstration"]
        assert "bridge" in rec["next_action"].lower() or "practical" in rec["next_action"].lower()

    def test_youtube_query_is_concise_and_relevant(self):
        q = generate_youtube_query("Docker")
        assert "docker" in q.lower()
        assert "tutorial" in q.lower()


class TestPersonalizedLearningPlan:
    """Tests for the personalized learning plan ordering and milestones."""

    def test_learning_plan_prioritizes_top_3(self):
        recs = [
            {"skill_name": "GraphQL", "priority": "Low", "status": "Missing", "what_to_learn": "Schemas", "youtube_search_query": "graphql tutorial", "suggested_project": "GraphQL api"},
            {"skill_name": "Docker", "priority": "High", "status": "Partial", "what_to_learn": "Containers", "youtube_search_query": "docker tutorial", "suggested_project": "Docker app"},
            {"skill_name": "Kubernetes", "priority": "High", "status": "Missing", "what_to_learn": "Pods", "youtube_search_query": "k8s tutorial", "suggested_project": "K8s cluster"},
            {"skill_name": "Redis", "priority": "Medium", "status": "Missing", "what_to_learn": "Caching", "youtube_search_query": "redis tutorial", "suggested_project": "Redis cache"},
        ]
        plan = build_personalized_learning_plan(recs)

        assert len(plan["top_skills_to_improve"]) == 3
        # High priority items should be in top 3
        assert "Docker" in plan["top_skills_to_improve"]
        assert "Kubernetes" in plan["top_skills_to_improve"]
        assert len(plan["learning_order"]) == 4
        assert len(plan["completion_goals"]) >= 2
        assert "disclaimer" in plan

    def test_empty_recommendations_handled_gracefully(self):
        plan = build_personalized_learning_plan([])
        assert plan["top_skills_to_improve"] == []
        assert plan["learning_order"] == []
        assert len(plan["completion_goals"]) > 0


class TestFullRecommendationPipeline:
    """Tests for generate_recommendations_for_analysis."""

    def test_empty_analysis_returns_gracefully(self):
        res = generate_recommendations_for_analysis({})
        assert res["success"] is False
        assert res["recommendations"] == []

    def test_analysis_with_all_matching_skills_produces_empty_recommendations(self):
        fake_analysis = {
            "success": True,
            "classified_skills": [
                {"name": "Python", "status": "Matching", "importance": "High"},
                {"name": "React", "status": "Matching", "importance": "Medium"},
            ],
        }
        res = generate_recommendations_for_analysis(fake_analysis, "Python React required", "Python React")
        assert res["success"] is True
        assert res["recommendations"] == []
        assert res["total_recommendations"] == 0

    def test_duplicate_skills_deduplicated_in_recommendations(self):
        fake_analysis = {
            "success": True,
            "classified_skills": [
                {"name": "Docker", "status": "Missing", "importance": "High"},
                {"name": "Docker", "status": "Missing", "importance": "High"},
            ],
        }
        res = generate_recommendations_for_analysis(fake_analysis, "Docker required", "")
        assert res["success"] is True
        assert len(res["recommendations"]) == 1
        assert res["recommendations"][0]["skill_name"] == "Docker"

    def test_end_to_end_recommendations_generation(self):
        fake_analysis = {
            "success": True,
            "classified_skills": [
                {"name": "Python", "status": "Matching", "importance": "High", "evidence": "5 years Python."},
                {"name": "Docker", "status": "Partial", "importance": "High", "evidence": "Used containers."},
                {"name": "Kubernetes", "status": "Missing", "importance": "High", "evidence": None},
                {"name": "GraphQL", "status": "Missing", "importance": "Low", "evidence": None},
            ],
        }
        job = "Senior Engineer. Required: Python, Docker, Kubernetes. Preferred: GraphQL."
        resume = "5 years Python. Used containers."

        res = generate_recommendations_for_analysis(fake_analysis, job, resume, job_title="Senior Engineer")
        assert res["success"] is True
        assert res["total_recommendations"] == 3  # Docker, Kubernetes, GraphQL

        rec_names = [r["skill_name"] for r in res["recommendations"]]
        assert "Docker" in rec_names
        assert "Kubernetes" in rec_names
        assert "GraphQL" in rec_names

        # Verify priority distribution
        docker_rec = next(r for r in res["recommendations"] if r["skill_name"] == "Docker")
        assert docker_rec["priority"] in ["High", "Medium"]

        graphql_rec = next(r for r in res["recommendations"] if r["skill_name"] == "GraphQL")
        assert graphql_rec["priority"] == "Low"

        # Verify learning plan top skills
        assert len(res["learning_plan"]["top_skills_to_improve"]) == 3
