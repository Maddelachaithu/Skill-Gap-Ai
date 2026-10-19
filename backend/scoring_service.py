"""
Transparent Match Scoring Service for Skill Gap AI
Calculates deterministic compatibility scores using weighted requirement analysis.
Zero random or LLM-hallucinated numbers. Fully configurable and explainable.
"""

from typing import Dict, List, Any

# Configurable Weights by Requirement Importance
DEFAULT_IMPORTANCE_WEIGHTS: Dict[str, float] = {
    "High": 3.0,
    "Medium": 2.0,
    "Low": 1.0,
}

# Configurable Credit Multipliers by Match Classification
DEFAULT_STATUS_CREDIT: Dict[str, float] = {
    "Matching": 1.0,           # 100% credit
    "Partial": 0.5,            # 50% partial credit
    "Needs verification": 0.3, # 30% tentative credit
    "Missing": 0.0,            # 0% credit
}


def calculate_match_score(
    classified_skills: List[Dict[str, Any]],
    importance_weights: Dict[str, float] = None,
    status_credit: Dict[str, float] = None,
) -> Dict[str, Any]:
    """
    Computes a transparent, weighted alignment score from classified skills.
    
    Formula:
      Score = (Total Earned Points / Total Possible Points) * 100
      Where:
        - Each requirement has a weight based on importance (High: 3, Medium: 2, Low: 1)
        - Matching skills earn 100% of their weight
        - Partial matches earn 50% of their weight
        - Needs-verification skills earn 30% of their weight
        - Missing skills earn 0%
    """
    weights = importance_weights or DEFAULT_IMPORTANCE_WEIGHTS
    credit_map = status_credit or DEFAULT_STATUS_CREDIT

    if not classified_skills:
        return {
            "score_percentage": 0.0,
            "display_score": 0,
            "total_requirements": 0,
            "matching_count": 0,
            "partial_count": 0,
            "missing_count": 0,
            "needs_verification_count": 0,
            "earned_points": 0.0,
            "total_possible_points": 0.0,
            "formula_explanation": "No requirements were supplied or identified in the job description.",
            "disclaimer": (
                "This compatibility score is a deterministic estimate based strictly on the skills extracted "
                "from the provided job description and your resume. It is not an official Applicant Tracking System (ATS) "
                "verdict or a guarantee of interview selection."
            ),
        }

    total_possible_points = 0.0
    earned_points = 0.0

    matching_count = 0
    partial_count = 0
    missing_count = 0
    needs_verification_count = 0

    for item in classified_skills:
        importance = item.get("importance", "Medium")
        status = item.get("status", "Missing")

        weight = weights.get(importance, 2.0)
        multiplier = credit_map.get(status, 0.0)

        total_possible_points += weight
        earned_points += weight * multiplier

        if status == "Matching":
            matching_count += 1
        elif status == "Partial":
            partial_count += 1
        elif status == "Needs verification":
            needs_verification_count += 1
        else:
            missing_count += 1

    if total_possible_points > 0:
        score_percentage = round((earned_points / total_possible_points) * 100, 1)
        display_score = int(round(score_percentage))
    else:
        score_percentage = 0.0
        display_score = 0

    formula_explanation = (
        f"Score is derived from {len(classified_skills)} job requirements. "
        f"Earned {earned_points:.1f} out of {total_possible_points:.1f} total weighted points "
        f"({matching_count} fully matching @ 100%, {partial_count} partial @ 50%, "
        f"{needs_verification_count} under verification @ 30%, and {missing_count} missing @ 0%)."
    )

    return {
        "score_percentage": score_percentage,
        "display_score": display_score,
        "total_requirements": len(classified_skills),
        "matching_count": matching_count,
        "partial_count": partial_count,
        "missing_count": missing_count,
        "needs_verification_count": needs_verification_count,
        "earned_points": round(earned_points, 2),
        "total_possible_points": round(total_possible_points, 2),
        "formula_explanation": formula_explanation,
        "disclaimer": (
            "This compatibility score estimates alignment with the supplied job description using explicit "
            "skill verification. It is an educational guide, not an official ATS score or hiring guarantee."
        ),
    }
