"""
Resume Analysis Engine for Skill Gap AI
Compares extracted resume text against job description requirements using
a domain-specific skill taxonomy, contextual evidence extraction,
and deterministic skill classification (Matching, Partial, Missing, Needs Verification).
"""

import re
from typing import Dict, List, Any, Optional, Tuple

from backend.skills_taxonomy import SKILLS_TAXONOMY, normalize_skill_name
from backend.scoring_service import calculate_match_score


def find_context_sentence(text: str, term: str, max_chars: int = 180) -> Optional[str]:
    """
    Extracts the surrounding sentence or clause where term appears.
    Normalizes whitespace and limits snippet length.
    """
    if not text or not term:
        return None

    # Escape term for regex word boundary search
    escaped_term = re.escape(term)
    # Split text into candidate sentences or major clause segments
    raw_sentences = re.split(r"(?<=[.!?\n\r])\s+|[;•\-\*]\s+", text)

    pattern = re.compile(rf"\b{escaped_term}\b", re.IGNORECASE)

    for sentence in raw_sentences:
        clean_s = " ".join(sentence.strip().split())
        if pattern.search(clean_s):
            if len(clean_s) > max_chars:
                # Find match index and take a window around it
                m = pattern.search(clean_s)
                start = max(0, m.start() - 40)
                end = min(len(clean_s), m.end() + 100)
                snippet = clean_s[start:end].strip()
                if start > 0:
                    snippet = "..." + snippet
                if end < len(clean_s):
                    snippet = snippet + "..."
                return snippet
            return clean_s

    return None


def extract_skills_from_job_description(job_text: str) -> List[Dict[str, Any]]:
    """
    Identifies all relevant skills requested in the job description,
    normalizes them, and assigns importance (High, Medium, Low) based on context.
    """
    if not job_text or not job_text.strip():
        return []

    identified_skills: Dict[str, Dict[str, Any]] = {}
    lower_job = job_text.lower()

    # Search for each canonical skill and its aliases in job description
    for canonical_name, data in SKILLS_TAXONOMY.items():
        all_patterns = [canonical_name.lower()] + [a.lower() for a in data.get("aliases", [])]

        match_found = False
        matched_term = ""

        for pat in all_patterns:
            # Check with word boundaries
            if re.search(rf"\b{re.escape(pat)}\b", lower_job):
                match_found = True
                matched_term = pat
                break

        # Check ambiguous aliases with extra strictness
        if not match_found and "ambiguous_aliases" in data:
            for ambig in data["ambiguous_aliases"]:
                if re.search(rf"\b{re.escape(ambig)}\s+(?:programming|language|developer|engineer|code)\b", lower_job):
                    match_found = True
                    matched_term = ambig
                    break

        if match_found:
            # Determine requirement importance from surrounding context
            context = find_context_sentence(job_text, matched_term) or ""
            lower_ctx = context.lower()

            high_keywords = [
                "required", "must have", "minimum", "essential", "core",
                "expert", "deep knowledge", "years of experience", "proficient in",
                "key requirement", "mandatory"
            ]
            low_keywords = [
                "nice to have", "plus", "preferred", "bonus", "optional",
                "familiarity with", "exposure to", "beneficial"
            ]

            if any(k in lower_ctx for k in high_keywords):
                importance = "High"
            elif any(k in lower_ctx for k in low_keywords):
                importance = "Low"
            else:
                importance = "Medium"

            identified_skills[canonical_name] = {
                "name": canonical_name,
                "importance": importance,
                "category": data.get("category", "General"),
                "domain": data.get("domain", "general"),
                "matched_term": matched_term,
                "job_context": context,
            }

    # Return list of identified requirements sorted by High -> Medium -> Low
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    sorted_skills = sorted(
        identified_skills.values(),
        key=lambda s: (priority_order.get(s["importance"], 1), s["name"]),
    )
    return sorted_skills


def evaluate_skill_against_resume(
    skill_req: Dict[str, Any],
    resume_text: str,
) -> Dict[str, Any]:
    """
    Evaluates whether a single job requirement is Matching, Partial, Missing,
    or Needs Verification in the candidate resume without fabricating evidence.
    """
    canonical_name = skill_req["name"]
    importance = skill_req["importance"]
    category = skill_req.get("category", "Technical")
    taxonomy_data = SKILLS_TAXONOMY.get(canonical_name, {})

    aliases = [canonical_name.lower()] + [a.lower() for a in taxonomy_data.get("aliases", [])]
    ambiguous_aliases = [a.lower() for a in taxonomy_data.get("ambiguous_aliases", [])]
    related_skills = taxonomy_data.get("related", [])

    lower_resume = resume_text.lower()

    # 1. Search for direct unambiguous matches
    direct_match_term = None
    for alias in aliases:
        if re.search(rf"\b{re.escape(alias)}\b", lower_resume):
            direct_match_term = alias
            break

    if direct_match_term:
        evidence = find_context_sentence(resume_text, direct_match_term)
        return {
            "name": canonical_name,
            "importance": importance,
            "category": category,
            "status": "Matching",
            "evidence": evidence or f"Explicit mention of '{canonical_name}' in resume.",
            "explanation": f"Verified direct evidence of {canonical_name} in candidate profile.",
            "suggestion": f"Maintain strong competency. Highlight specific project scale, metrics, or business outcomes achieved with {canonical_name}.",
        }

    # 2. Check ambiguous aliases (e.g. 'go' or 'c')
    for ambig in ambiguous_aliases:
        if re.search(rf"\b{re.escape(ambig)}\b", lower_resume):
            evidence = find_context_sentence(resume_text, ambig)
            # Check if clearly in tech context
            if evidence and any(w in evidence.lower() for w in ["developer", "engineer", "programming", "code", "backend", "framework", "skills"]):
                return {
                    "name": canonical_name,
                    "importance": importance,
                    "category": category,
                    "status": "Matching",
                    "evidence": evidence,
                    "explanation": f"Verified competency in {canonical_name} from technical context.",
                    "suggestion": f"Clarify exact {canonical_name} project deliverables on resume.",
                }
            else:
                return {
                    "name": canonical_name,
                    "importance": importance,
                    "category": category,
                    "status": "Needs verification",
                    "evidence": evidence,
                    "explanation": f"Ambiguous mention of term '{ambig}' detected. Candidate confirmation recommended.",
                    "suggestion": f"Specify '{canonical_name}' explicitly in your Skills and Experience sections to eliminate ambiguity.",
                }

    # 3. Check for related competency (Partial Match)
    for rel in related_skills:
        rel_canonical = normalize_skill_name(rel)
        rel_data = SKILLS_TAXONOMY.get(rel_canonical, {})
        rel_aliases = [rel.lower()] + [a.lower() for a in rel_data.get("aliases", [])]

        for rel_alias in rel_aliases:
            if re.search(rf"\b{re.escape(rel_alias)}\b", lower_resume):
                evidence = find_context_sentence(resume_text, rel_alias)
                return {
                    "name": canonical_name,
                    "importance": importance,
                    "category": category,
                    "status": "Partial",
                    "evidence": evidence or f"Evidence of related skill '{rel}' found in resume.",
                    "explanation": f"Resume demonstrates related proficiency in {rel}, but specific production experience with {canonical_name} was not explicitly identified.",
                    "suggestion": f"Leverage your experience in {rel} to demonstrate transferable capability in {canonical_name}. Add hands-on {canonical_name} projects to your resume.",
                }

    # 4. No evidence or related skill found (Missing)
    return {
        "name": canonical_name,
        "importance": importance,
        "category": category,
        "status": "Missing",
        "evidence": None,
        "explanation": f"No direct or closely related evidence for {canonical_name} was found in the uploaded resume.",
        "suggestion": f"Acquire core competencies in {canonical_name}. Complete a project or tutorial series and add it under your Technical Skills section.",
    }


def extract_experience_insights(resume_text: str, job_text: str) -> List[str]:
    """
    Extracts and contrasts seniority and years of experience mentions between
    the job posting and resume.
    """
    insights = []

    # Search for year patterns: e.g. "4+ years", "3-5 years", "2 years"
    year_pattern = re.compile(r"\b(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of\s+experience)?\b", re.IGNORECASE)

    job_years = year_pattern.findall(job_text)
    resume_years = year_pattern.findall(resume_text)

    if job_years:
        max_job_req = max([float(y) for y in job_years if float(y) < 25], default=None)
        if max_job_req:
            if resume_years:
                max_cand_exp = max([float(y) for y in resume_years if float(y) < 40], default=None)
                if max_cand_exp and max_cand_exp >= max_job_req:
                    insights.append(
                        f"Experience Alignment: Job requests ~{max_job_req:.0f}+ years; resume indicates up to {max_cand_exp:.1f}+ years of production experience (Satisfied)."
                    )
                elif max_cand_exp:
                    insights.append(
                        f"Experience Depth Gap: Target position requests ~{max_job_req:.0f}+ years; candidate mentions ~{max_cand_exp:.1f}+ years. Emphasize project complexity and technical ownership."
                    )
            else:
                insights.append(
                    f"Experience Specification: Target role requests ~{max_job_req:.0f}+ years of industry experience. Ensure your total career duration is prominently highlighted."
                )

    # Check for Senior/Lead/Architect keywords
    senior_keywords = ["senior", "lead", "architect", "staff", "principal"]
    job_senior = any(re.search(rf"\b{k}\b", job_text, re.IGNORECASE) for k in senior_keywords)
    resume_senior = any(re.search(rf"\b{k}\b", resume_text, re.IGNORECASE) for k in senior_keywords)

    if job_senior and not resume_senior:
        insights.append(
            "Leadership & Seniority Gap: Job emphasizes senior/leadership expectations. Frame resume bullet points around architectural design decisions and mentoring rather than individual task execution."
        )

    # General fallback if no numeric years detected
    if not insights:
        insights.append(
            "Production Breadth: Ensure bullet points across recent roles detail system scale, team collaboration, and measurable business impact."
        )

    return insights


def generate_actionable_recommendations(
    classified_skills: List[Dict[str, Any]],
    experience_insights: List[str],
) -> List[str]:
    """
    Synthesizes actionable, prioritized resume improvements based on actual gaps.
    """
    recommendations = []

    missing = [s for s in classified_skills if s["status"] == "Missing"]
    partial = [s for s in classified_skills if s["status"] == "Partial"]

    # Priority 1: High-importance missing skills
    high_missing = [s["name"] for s in missing if s["importance"] == "High"]
    if high_missing:
        recommendations.append(
            f"Prioritize High-Value Deficits: The job designates {', '.join(high_missing[:3])} as core requirements. Add practical proof (projects, certifications) for these technologies."
        )

    # Priority 2: Partial skills
    if partial:
        names = [s["name"] for s in partial[:2]]
        recommendations.append(
            f"Bridge Partial Competencies: You possess transferable foundations for {', '.join(names)}. Explicitly highlight tools and direct workflows used with them."
        )

    # Priority 3: Quantify impact
    recommendations.append(
        "Quantify Business Impact: Structure resume bullet points using the Google XYZ formula: 'Accomplished [X], as measured by [Y], by doing [Z]'."
    )

    # Priority 4: Reorganize technical section
    if missing or partial:
        recommendations.append(
            "Targeted Skill Taxonomy: Group your skills into clean subheadings (Languages, Frameworks, Cloud & DevOps, Databases) matching the target job description format."
        )

    return recommendations


def analyze_resume_against_job(
    resume_text: str,
    job_description: str,
    job_title: str = "",
) -> Dict[str, Any]:
    """
    Main orchestration entry point:
    Validates inputs, extracts job skills, evaluates resume evidence,
    and returns comprehensive, non-fabricated analysis results.
    """
    if not resume_text or not resume_text.strip():
        return {
            "success": False,
            "error": "Resume text is empty or unreadable.",
            "classified_skills": [],
            "matching_skills": [],
            "partial_skills": [],
            "missing_skills": [],
            "needs_verification_skills": [],
            "scoring": {},
            "experience_insights": [],
            "actionable_recommendations": [],
            "total_skills_detected": 0,
        }

    if not job_description or not job_description.strip():
        return {
            "success": False,
            "error": "Job description is empty.",
            "classified_skills": [],
            "matching_skills": [],
            "partial_skills": [],
            "missing_skills": [],
            "needs_verification_skills": [],
            "scoring": {},
            "experience_insights": [],
            "actionable_recommendations": [],
            "total_skills_detected": 0,
        }

    # 1. Identify skills required in the job description
    # Also include job title in context search
    combined_job_text = f"{job_title}\n\n{job_description}" if job_title else job_description
    job_skills = extract_skills_from_job_description(combined_job_text)

    # Fallback if no skills from taxonomy matched
    if not job_skills:
        # Provide general fallback analysis rather than empty failure
        return {
            "success": True,
            "error": None,
            "classified_skills": [],
            "matching_skills": [],
            "partial_skills": [],
            "missing_skills": [],
            "needs_verification_skills": [],
            "scoring": calculate_match_score([]),
            "experience_insights": extract_experience_insights(resume_text, combined_job_text),
            "actionable_recommendations": [
                "Ensure your job description specifies core programming languages, frameworks, and tools so Skill Gap AI can evaluate technical alignment."
            ],
            "total_skills_detected": 0,
        }

    # 2. Evaluate each job requirement against resume evidence
    classified_skills = []
    matching_skills = []
    partial_skills = []
    missing_skills = []
    needs_verification_skills = []

    for req in job_skills:
        eval_result = evaluate_skill_against_resume(req, resume_text)
        classified_skills.append(eval_result)

        status = eval_result["status"]
        if status == "Matching":
            matching_skills.append(eval_result)
        elif status == "Partial":
            partial_skills.append(eval_result)
        elif status == "Needs verification":
            needs_verification_skills.append(eval_result)
        else:
            missing_skills.append(eval_result)

    # 3. Calculate score
    scoring = calculate_match_score(classified_skills)

    # 4. Extract experience insights & recommendations
    exp_insights = extract_experience_insights(resume_text, combined_job_text)
    recommendations = generate_actionable_recommendations(classified_skills, exp_insights)

    return {
        "success": True,
        "error": None,
        "classified_skills": classified_skills,
        "matching_skills": matching_skills,
        "partial_skills": partial_skills,
        "missing_skills": missing_skills,
        "needs_verification_skills": needs_verification_skills,
        "scoring": scoring,
        "experience_insights": exp_insights,
        "actionable_recommendations": recommendations,
        "total_skills_detected": len(classified_skills),
    }
