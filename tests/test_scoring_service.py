"""
Unit Tests for Skill Gap AI - Scoring Service
Tests formula correctness, weighting by importance, partial credit, and edge cases.
"""

import pytest
from backend.scoring_service import (
    calculate_match_score,
    DEFAULT_IMPORTANCE_WEIGHTS,
    DEFAULT_STATUS_CREDIT,
)


class TestScoringService:
    """Tests for the transparent scoring service."""

    def test_empty_requirements_returns_zero(self):
        result = calculate_match_score([])
        assert result["score_percentage"] == 0.0
        assert result["display_score"] == 0
        assert result["total_requirements"] == 0
        assert result["matching_count"] == 0
        assert "No requirements" in result["formula_explanation"]

    def test_all_matching_skills_scores_100(self):
        skills = [
            {"name": "Python", "importance": "High", "status": "Matching"},
            {"name": "React", "importance": "Medium", "status": "Matching"},
            {"name": "SQL", "importance": "Low", "status": "Matching"},
        ]
        # Total points = 3 + 2 + 1 = 6. Earned = 3 + 2 + 1 = 6. Score = 100%
        result = calculate_match_score(skills)
        assert result["score_percentage"] == 100.0
        assert result["display_score"] == 100
        assert result["matching_count"] == 3
        assert result["missing_count"] == 0
        assert result["total_possible_points"] == 6.0
        assert result["earned_points"] == 6.0

    def test_all_missing_skills_scores_zero(self):
        skills = [
            {"name": "Kubernetes", "importance": "High", "status": "Missing"},
            {"name": "Docker", "importance": "Medium", "status": "Missing"},
        ]
        # Total points = 3 + 2 = 5. Earned = 0. Score = 0%
        result = calculate_match_score(skills)
        assert result["score_percentage"] == 0.0
        assert result["display_score"] == 0
        assert result["missing_count"] == 2
        assert result["earned_points"] == 0.0

    def test_partial_matches_receive_half_credit(self):
        skills = [
            {"name": "TypeScript", "importance": "Medium", "status": "Partial"}, # 2 * 0.5 = 1
        ]
        # Total points = 2. Earned = 1. Score = 50%
        result = calculate_match_score(skills)
        assert result["score_percentage"] == 50.0
        assert result["display_score"] == 50
        assert result["partial_count"] == 1
        assert result["earned_points"] == 1.0

    def test_mixed_requirements_weighted_correctly(self):
        skills = [
            # High (weight 3): Matching -> 3.0 pts
            {"name": "Python", "importance": "High", "status": "Matching"},
            # Medium (weight 2): Partial -> 1.0 pt
            {"name": "Docker", "importance": "Medium", "status": "Partial"},
            # Low (weight 1): Missing -> 0.0 pts
            {"name": "GraphQL", "importance": "Low", "status": "Missing"},
        ]
        # Total points = 3 + 2 + 1 = 6.0
        # Earned points = 3.0 + 1.0 + 0 = 4.0
        # Expected score = (4.0 / 6.0) * 100 = 66.7%
        result = calculate_match_score(skills)
        assert result["score_percentage"] == 66.7
        assert result["display_score"] == 67
        assert result["total_possible_points"] == 6.0
        assert result["earned_points"] == 4.0
        assert result["matching_count"] == 1
        assert result["partial_count"] == 1
        assert result["missing_count"] == 1

    def test_custom_weights_configuration(self):
        custom_weights = {"High": 10.0, "Medium": 5.0, "Low": 1.0}
        skills = [
            {"name": "Python", "importance": "High", "status": "Matching"},  # 10 * 1.0 = 10
            {"name": "Java", "importance": "Low", "status": "Missing"},      # 1 * 0.0 = 0
        ]
        # Total = 11.0. Earned = 10.0. Score = (10/11)*100 = 90.9%
        result = calculate_match_score(skills, importance_weights=custom_weights)
        assert result["score_percentage"] == 90.9
        assert result["display_score"] == 91
