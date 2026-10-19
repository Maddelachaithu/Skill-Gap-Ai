"""
Personalized Recommendation Service for Skill Gap AI
Generates actionable, prioritized improvement recommendations and a structured
learning roadmap derived strictly from real resume-to-job analysis results.
"""

import re
from typing import Dict, List, Any, Optional, Tuple

from backend.skills_taxonomy import SKILLS_TAXONOMY, normalize_skill_name

# Skill-specific learning guidance and practical project blueprints
SKILL_LEARNING_GUIDANCE: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # CLOUD & DEVOPS
    # -------------------------------------------------------------------------
    "Docker": {
        "why_it_matters": "Containerization standardizes runtime environments across development and production, preventing configuration drift.",
        "what_to_learn": "Multi-stage Dockerfiles, image size minimization, layer caching, volume persistence, and Docker Compose networking.",
        "exercises": [
            "Write a multi-stage Dockerfile for a backend web service that keeps the final runtime image under 150MB.",
            "Configure a docker-compose.yml file linking a web API, a PostgreSQL database, and a Redis caching layer with health checks.",
        ],
        "project": "Build and containerize a multi-service web application using Docker Compose with volume mounts and published ports on GitHub.",
        "search_query": "Docker and Docker Compose tutorial for beginners",
        "prerequisites": ["Linux", "Git"],
    },
    "Kubernetes": {
        "why_it_matters": "Enterprise cloud environments rely on Kubernetes for automated deployment, scaling, rolling updates, and self-healing of containers.",
        "what_to_learn": "Pods, Deployments, Services (ClusterIP/NodePort/LoadBalancer), ConfigMaps, Secrets, Ingress controllers, and Helm charts.",
        "exercises": [
            "Deploy a local cluster using Minikube or Kind and launch a replicated Deployment with 3 pods.",
            "Write Kubernetes manifests configuring a Deployment, a ClusterIP Service, and an Ingress resource with path routing.",
            "Create a Helm chart to parameterize environment variables and replica counts across staging and production.",
        ],
        "project": "Deploy a multi-tier application onto Minikube managed via Helm, demonstrating horizontal pod autoscaling (HPA) under synthetic load.",
        "search_query": "Kubernetes tutorial for beginners hands on",
        "prerequisites": ["Docker"],
    },
    "AWS": {
        "why_it_matters": "AWS is the leading cloud infrastructure provider; roles require deploying, securing, and monitoring cloud-native workloads.",
        "what_to_learn": "EC2 provisioning, S3 bucket security policies, IAM role permissions, VPC networking, Lambda serverless functions, and CloudWatch.",
        "exercises": [
            "Deploy a containerized service to AWS ECS or App Runner with automated health monitoring.",
            "Configure an S3 bucket with least-privilege IAM policies, versioning, and lifecycle expiration rules.",
        ],
        "project": "Architect an automated serverless backend using AWS Lambda, API Gateway, and DynamoDB or S3.",
        "search_query": "AWS cloud practitioner and solutions architect tutorial",
        "prerequisites": ["Cloud & DevOps"],
    },
    "CI/CD": {
        "why_it_matters": "Automated pipelines ensure reliable testing, linting, security scans, and production deployments on every commit.",
        "what_to_learn": "GitHub Actions workflow syntax, secrets management, automated test execution, Docker build-and-push actions, and deployment triggers.",
        "exercises": [
            "Create a .github/workflows/ci.yml pipeline that runs linter checks and Pytest on all pull requests.",
            "Add automated Docker build and push actions pushing tagged images to a container registry upon merge to main.",
        ],
        "project": "Set up a complete GitHub Actions CI/CD pipeline that tests code, builds Docker containers, and deploys to staging.",
        "search_query": "GitHub Actions CI CD pipeline tutorial",
        "prerequisites": ["Git"],
    },

    # -------------------------------------------------------------------------
    # BACKEND & APIS
    # -------------------------------------------------------------------------
    "GraphQL": {
        "why_it_matters": "GraphQL allows clients to request exactly the data they need, reducing roundtrips and over-fetching in complex web and mobile apps.",
        "what_to_learn": "Schema Definition Language (SDL), Query resolvers, Mutation handling, Apollo Server/Client, and avoiding N+1 query traps.",
        "exercises": [
            "Define a GraphQL schema with Queries, Mutations, and custom types for a resource collection.",
            "Implement resolver functions with DataLoader to solve the N+1 database querying problem.",
        ],
        "project": "Build a GraphQL API server using Python (Strawberry/Ariadne) or Node.js Apollo Server connected to a relational database.",
        "search_query": "GraphQL full course tutorial for developers",
        "prerequisites": ["REST APIs"],
    },
    "REST APIs": {
        "why_it_matters": "RESTful services form the universal backbone of distributed systems, web architectures, and third-party integrations.",
        "what_to_learn": "HTTP status codes, REST resource naming conventions, idempotency, request validation, authentication headers, and Swagger/OpenAPI docs.",
        "exercises": [
            "Design clean REST endpoints following RESTful resource guidelines with pagination and filtering.",
            "Implement automated request schema validation and return structured HTTP error payloads.",
        ],
        "project": "Develop a production-grade CRUD microservice with OpenAPI documentation, authentication, and database integration.",
        "search_query": "REST API design best practices tutorial",
        "prerequisites": ["Python", "JavaScript"],
    },
    "System Design": {
        "why_it_matters": "Senior engineering roles require architecting resilient systems that handle high concurrency, data persistence, and failure recovery.",
        "what_to_learn": "Load balancing, horizontal vs. vertical scaling, distributed caching (Redis), database indexing/sharding, CAP theorem, and rate limiting.",
        "exercises": [
            "Diagram the high-availability architecture of a high-throughput URL shortener or message queue consumer.",
            "Implement a token-bucket rate limiter middleware preventing API endpoint abuse.",
        ],
        "project": "Design and document an end-to-end distributed system architecture with caching, message queue decoupling, and failover replicas.",
        "search_query": "System Design interview and architecture tutorial",
        "prerequisites": ["Databases", "Microservices"],
    },
    "Redis": {
        "why_it_matters": "In-memory datastores dramatically reduce database load and latency for session management, leaderboards, and caching.",
        "what_to_learn": "Data structures (strings, hashes, sets, sorted sets), TTL expiration policies, cache-aside patterns, pub/sub, and distributed locks.",
        "exercises": [
            "Implement a cache-aside query pattern in Python with configurable TTL expiration.",
            "Build a Redis pub/sub message broadcaster between two decoupled microservice processes.",
        ],
        "project": "Add Redis caching and API rate limiting to an existing web API, measuring response latency reduction.",
        "search_query": "Redis crash course and caching tutorial",
        "prerequisites": ["Databases"],
    },
    "PostgreSQL": {
        "why_it_matters": "PostgreSQL is the gold standard for reliable relational storage, ACID compliance, and advanced JSON/indexing queries.",
        "what_to_learn": "Complex joins, B-Tree and GIN indexing, EXPLAIN ANALYZE query planning, foreign key constraints, transactions, and connection pooling.",
        "exercises": [
            "Run EXPLAIN ANALYZE on a slow query and add targeted composite indexes to optimize execution time.",
            "Write a database migration script altering schemas safely without locking live production tables.",
        ],
        "project": "Design a normalized database schema with foreign keys, indexes, and automated migration scripts using SQLAlchemy or Prisma.",
        "search_query": "PostgreSQL database tutorial for developers",
        "prerequisites": ["SQL"],
    },
    "FastAPI": {
        "why_it_matters": "FastAPI is the modern standard for high-performance Python APIs, offering native async concurrency, Pydantic validation, and autogenerated docs.",
        "what_to_learn": "Path/query parameters, Pydantic request/response models, async/await concurrency, dependency injection, and Pytest test client.",
        "exercises": [
            "Create an async FastAPI endpoint validating request payloads with Pydantic and returning status 201.",
            "Write integration tests using HTTPX AsyncClient and Pytest validating status codes and response schemas.",
        ],
        "project": "Build an async REST microservice using FastAPI, SQLAlchemy async session, and Alembic database migrations.",
        "search_query": "FastAPI Python tutorial for beginners",
        "prerequisites": ["Python"],
    },
    "TypeScript": {
        "why_it_matters": "TypeScript catches type errors at compile time, improving maintainability and developer velocity in enterprise codebases.",
        "what_to_learn": "Interfaces, type aliases, generics, union/intersection types, narrowing, utility types, and strict mode configuration.",
        "exercises": [
            "Refactor a JavaScript utility file to strict TypeScript with complete parameter and return type signatures.",
            "Write a generic API fetcher function parameterized by response model types.",
        ],
        "project": "Convert or build a React application with strict TypeScript types for all components, props, and state.",
        "search_query": "TypeScript tutorial for beginners",
        "prerequisites": ["JavaScript"],
    },

    # -------------------------------------------------------------------------
    # DATA ANALYTICS & MACHINE LEARNING
    # -------------------------------------------------------------------------
    "Pandas": {
        "why_it_matters": "Pandas is the primary library for data manipulation, cleaning, aggregation, and feature engineering in Python.",
        "what_to_learn": "DataFrames, Series, filtering, groupby aggregations, handling missing values, merge/join operations, and datetime manipulation.",
        "exercises": [
            "Load a raw CSV dataset, clean missing null values, and calculate summary statistics grouped by categorical variables.",
            "Perform vectorized transformations and save cleaned aggregated tables.",
        ],
        "project": "Conduct an Exploratory Data Analysis (EDA) on a public dataset using Pandas, documenting actionable insights in a Jupyter notebook.",
        "search_query": "Pandas Python tutorial for data analysis",
        "prerequisites": ["Python"],
    },
    "Machine Learning": {
        "why_it_matters": "Predictive modeling and statistical learning extract automated patterns and decision boundaries from historical data.",
        "what_to_learn": "Supervised vs unsupervised learning, train/test splitting, cross-validation, feature scaling, evaluation metrics (ROC-AUC, F1, RMSE).",
        "exercises": [
            "Train and evaluate a classification model with Scikit-Learn, outputting confusion matrix and classification reports.",
            "Implement feature scaling and hyperparameter tuning using GridSearchCV.",
        ],
        "project": "Build an end-to-end predictive machine learning model with feature engineering, validation, and a trained model artifact.",
        "search_query": "Machine Learning tutorial for beginners Scikit-Learn",
        "prerequisites": ["Python", "Pandas"],
    },
    "Tableau": {
        "why_it_matters": "Tableau transforms complex tabular datasets into interactive visual dashboards accessible to non-technical stakeholders.",
        "what_to_learn": "Data sources connection, calculated fields, parameters, interactive filters, dashboard layout design, and drill-down charts.",
        "exercises": [
            "Connect Tableau to a relational database or CSV and create a multi-metric summary dashboard.",
            "Write calculated fields calculating running totals and percent-of-total metrics.",
        ],
        "project": "Publish an interactive Tableau Public executive dashboard visualizing key operational metrics with dynamic filters.",
        "search_query": "Tableau tutorial for beginners full course",
        "prerequisites": ["Data Analytics"],
    },

    # -------------------------------------------------------------------------
    # CYBERSECURITY
    # -------------------------------------------------------------------------
    "SIEM": {
        "why_it_matters": "SIEM systems aggregate and correlate security events across networks and hosts to detect intrusions and compliance violations.",
        "what_to_learn": "Log ingestion, correlation rules, Splunk SPL query language, alert triage, incident escalation, and IOC detection.",
        "exercises": [
            "Set up Splunk Free or Elastic SIEM in a lab environment and ingest sample Windows/Linux security event logs.",
            "Write search queries detecting failed brute-force authentication attempts across a 15-minute window.",
        ],
        "project": "Build a home lab SIEM dashboard analyzing simulated cyber attack logs with custom alert triggers.",
        "search_query": "Splunk SIEM tutorial for beginners",
        "prerequisites": ["Network Security"],
    },
    "Penetration Testing": {
        "why_it_matters": "Proactive security testing uncovers exploitable vulnerabilities in applications and infrastructure before attackers find them.",
        "what_to_learn": "Reconnaissance, scanning (Nmap), vulnerability assessment, web exploitation (OWASP Top 10), and responsible reporting.",
        "exercises": [
            "Scan a vulnerable virtual machine in an authorized lab (e.g. TryHackMe/HackTheBox) using Nmap and document open attack surfaces.",
            "Identify and exploit a simulated SQL injection vulnerability in a testing sandbox, documenting remediation steps.",
        ],
        "project": "Complete a structured penetration testing report on an authorized lab machine with executive summary, CVSS scores, and remediation.",
        "search_query": "Penetration testing tutorial for beginners ethical hacking",
        "prerequisites": ["Network Security", "Linux"],
    },
    "Wireshark": {
        "why_it_matters": "Packet-level inspection is fundamental for diagnosing network latency, protocol anomalies, and unencrypted credential leaks.",
        "what_to_learn": "Packet capture filters, display filters, TCP handshake analysis, TLS handshake inspection, and stream reassembly.",
        "exercises": [
            "Capture live traffic in a local sandbox and filter for DNS and HTTP protocol anomalies.",
            "Analyze a sample pcap file from a malware capture to trace destination IP connections.",
        ],
        "project": "Analyze and document a network traffic capture investigating a simulated malicious beaconing event.",
        "search_query": "Wireshark packet analysis tutorial",
        "prerequisites": ["Network Security"],
    },
}


def calculate_skill_priority(
    skill_item: Dict[str, Any],
    job_description: str,
    resume_text: str,
) -> Tuple[str, str]:
    """
    Computes a transparent, deterministic priority (High, Medium, Low) for a missing or partial skill.
    
    Rules:
    - High Priority:
      - Job explicitly marks requirement as High / required / mandatory.
      - OR skill appears repeatedly (>= 2 times) in job requirements.
      - OR skill is a foundational prerequisite for other required technologies.
    - Medium Priority:
      - Job marks requirement as Medium, standard expectation.
      - OR Partial skill where candidate has related experience (high ROI gap).
    - Low Priority:
      - Job marks requirement as Low / preferred / nice-to-have / bonus.
      - OR skill is an optional secondary tool.
    
    Returns (priority, explanation_of_priority).
    """
    importance = skill_item.get("importance", "Medium")
    status = skill_item.get("status", "Missing")
    skill_name = skill_item.get("name", "")

    # Count mentions in job description
    lower_job = job_description.lower()
    canonical_data = SKILLS_TAXONOMY.get(skill_name, {})
    search_aliases = [skill_name.lower()] + [a.lower() for a in canonical_data.get("aliases", [])]

    mention_count = 0
    for alias in search_aliases:
        mention_count += len(re.findall(rf"\b{re.escape(alias)}\b", lower_job))

    # Deterministic priority evaluation
    if importance == "High":
        if mention_count >= 2:
            return "High", f"Designated as a core requirement and emphasized {mention_count} times in the job posting."
        return "High", "Explicitly identified as a required core competency in the job description."

    elif importance == "Low":
        return "Low", "Listed as a preferred or nice-to-have qualification in the job requirements."

    # Medium importance baseline:
    if status == "Partial":
        # Having a related skill makes bridging this gap a high-return, medium-effort priority
        return "Medium", "You possess related foundational competencies; closing this partial gap offers high return."

    if mention_count >= 2:
        return "High", f"Mentioned multiple times ({mention_count}x) across role responsibilities despite standard phrasing."

    return "Medium", "Standard technical requirement expected for proficient role execution."


def generate_youtube_query(skill_name: str, job_title: str = "") -> str:
    """
    Generates a focused, dynamic YouTube learning search query tailored to the skill and target job title.
    """
    clean_skill = skill_name.strip()
    clean_job = job_title.strip() if job_title else ""

    # Check if curated guidance has a specific search query
    if clean_skill in SKILL_LEARNING_GUIDANCE:
        return SKILL_LEARNING_GUIDANCE[clean_skill]["search_query"]

    # Dynamic query tailored with target job title if available
    if clean_job and clean_job.lower() not in clean_skill.lower():
        return f"{clean_skill} for {clean_job} tutorial for beginners"

    return f"{clean_skill} tutorial for beginners full course"


def generate_single_recommendation(
    skill_item: Dict[str, Any],
    job_description: str,
    resume_text: str,
    job_title: str = "",
) -> Dict[str, Any]:
    """
    Creates a comprehensive, evidence-grounded recommendation for a single
    missing, partial, or unverified skill.
    """
    skill_name = skill_item.get("name", "Unknown Skill")
    status = skill_item.get("status", "Missing")
    category = skill_item.get("category", "Technical")
    raw_evidence = skill_item.get("evidence")

    # Priority calculation
    priority, priority_reason = calculate_skill_priority(skill_item, job_description, resume_text)

    # Context-grounded educational search query tailored with job title
    yt_query = generate_youtube_query(skill_name, job_title)

    # Retrieval of curated or generated guidance
    guidance = SKILL_LEARNING_GUIDANCE.get(skill_name)
    if guidance:
        why_it_matters = guidance["why_it_matters"]
        what_to_learn = guidance["what_to_learn"]
        exercises = list(guidance["exercises"])
        project = guidance["project"]
    else:
        # Dynamic fallback for skills in taxonomy without hardcoded guidance
        why_it_matters = f"{skill_name} is a key tool in {category} requested by the target employer."
        what_to_learn = f"Core syntax, official documentation, practical workflows, and production best practices for {skill_name}."
        exercises = [
            f"Set up a local development environment for {skill_name} and complete a basic starter project.",
            f"Review official documentation and write unit tests or configurations demonstrating {skill_name}.",
        ]
        project = f"Build and publish a portfolio project on GitHub applying {skill_name} to solve a real-world problem."

    # Contextual evidence summary
    if status == "Matching":
        current_demo = f"Verified: Found evidence in resume: '{raw_evidence}'" if raw_evidence else "Explicitly listed in resume."
        next_action = f"Add measurable impact metrics detailing your accomplishments with {skill_name}."
    elif status == "Partial":
        current_demo = f"Related experience found: '{raw_evidence}'" if raw_evidence else "Related foundational skills detected in resume."
        next_action = f"Complete practical exercises to bridge from your existing experience to production {skill_name}."
    elif status == "Needs verification":
        current_demo = f"Ambiguous mention: '{raw_evidence}'" if raw_evidence else "Ambiguous token detected in resume text."
        next_action = f"Clarify your resume wording to explicitly list '{skill_name}' in your Skills and Work Experience sections."
    else:
        current_demo = "No sufficient evidence found in uploaded resume."
        next_action = f"Follow the suggested YouTube tutorial to complete the hands-on exercise for {skill_name}."

    return {
        "skill_name": skill_name,
        "status": status,
        "category": category,
        "priority": priority,
        "priority_reason": priority_reason,
        "why_it_matters": why_it_matters,
        "current_demonstration": current_demo,
        "what_to_learn": what_to_learn,
        "practical_exercises": exercises,
        "suggested_project": project,
        "youtube_search_query": yt_query,
        "next_action": next_action,
    }


def build_personalized_learning_plan(
    recommendations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Constructs a structured, prioritized learning plan containing:
    - Top 3 skills to improve first
    - Logical learning sequence (foundational prerequisites first)
    - Concrete project milestones
    - Clear completion goals without false hiring promises
    """
    if not recommendations:
        return {
            "top_skills_to_improve": [],
            "learning_order": [],
            "completion_goals": [
                "Your resume already demonstrates alignment with the required skills in this posting.",
                "Continue refining bullet points with quantified business metrics (latency, revenue, users).",
            ],
            "disclaimer": "This learning plan is an educational guide derived from skill comparison. It does not promise or guarantee employment.",
        }

    # Ordering logic:
    # 1. High priority first, then Medium, then Low
    # 2. Within priority: Partial skills first (quickest ROI to bridge), then Missing, then Needs verification
    priority_rank = {"High": 0, "Medium": 1, "Low": 2}
    status_rank = {"Partial": 0, "Missing": 1, "Needs verification": 2, "Matching": 3}

    sorted_recs = sorted(
        recommendations,
        key=lambda r: (priority_rank.get(r["priority"], 1), status_rank.get(r["status"], 1), r["skill_name"]),
    )

    # Top 3 skills to improve first
    top_3 = sorted_recs[:3]

    learning_order = []
    for idx, rec in enumerate(sorted_recs, start=1):
        learning_order.append({
            "step": idx,
            "skill_name": rec["skill_name"],
            "priority": rec["priority"],
            "status": rec["status"],
            "focus": rec["what_to_learn"],
            "youtube_query": rec["youtube_search_query"],
            "project_suggestion": rec["suggested_project"],
        })

    completion_goals = [
        "Milestone 1: Complete practical exercises for the top prioritized skills to eliminate core blockers.",
        "Milestone 2: Build and publish at least one working portfolio project on GitHub covering missing tools.",
        "Milestone 3: Update your resume skills section and work experience bullets using the Google XYZ formula: 'Accomplished [X] as measured by [Y] by doing [Z]'.",
    ]

    return {
        "top_skills_to_improve": [r["skill_name"] for r in top_3],
        "top_recommendations": top_3,
        "learning_order": learning_order,
        "total_skills_to_improve": len(sorted_recs),
        "completion_goals": completion_goals,
        "disclaimer": (
            "This personalized learning plan is designed as an educational roadmap based on skill matching. "
            "It does not guarantee interview selection, hiring outcomes, or official certification completion."
        ),
    }


def generate_recommendations_for_analysis(
    analysis_result: Dict[str, Any],
    job_description: str = "",
    resume_text: str = "",
    job_title: str = "",
) -> Dict[str, Any]:
    """
    Main entry point:
    Accepts Stage 3 analysis results and generates individualized recommendations
    for all partial, missing, and unverified skills, plus a structured learning plan.
    """
    if not analysis_result or not analysis_result.get("success", False):
        return {
            "success": False,
            "error": "No valid analysis results provided.",
            "recommendations": [],
            "learning_plan": build_personalized_learning_plan([]),
            "total_recommendations": 0,
        }

    classified = analysis_result.get("classified_skills", [])
    if not classified:
        return {
            "success": True,
            "error": None,
            "recommendations": [],
            "learning_plan": build_personalized_learning_plan([]),
            "total_recommendations": 0,
        }

    # Filter for skills needing improvement: Missing, Partial, Needs verification
    skills_needing_improvement = [
        s for s in classified if s.get("status") in ["Missing", "Partial", "Needs verification"]
    ]

    recommendations = []
    seen_skills = set()

    for skill_item in skills_needing_improvement:
        name = skill_item.get("name")
        if name in seen_skills:
            continue
        seen_skills.add(name)

        rec = generate_single_recommendation(
            skill_item=skill_item,
            job_description=job_description,
            resume_text=resume_text,
            job_title=job_title,
        )
        recommendations.append(rec)

    # Sort recommendations by Priority (High -> Medium -> Low)
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    recommendations.sort(key=lambda r: (priority_order.get(r["priority"], 1), r["skill_name"]))

    # Build personalized learning plan
    learning_plan = build_personalized_learning_plan(recommendations)

    return {
        "success": True,
        "error": None,
        "recommendations": recommendations,
        "learning_plan": learning_plan,
        "total_recommendations": len(recommendations),
    }
