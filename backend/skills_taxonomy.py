"""
Skill Taxonomy and Alias Mapping for Skill Gap AI
Comprehensive, configurable dictionary of skills across Software Development,
Data Analytics, and Cybersecurity with alias normalization and related skill graphs.
"""

from typing import Dict, List, Any

# Structured taxonomy of canonical skills with aliases and related competencies
SKILLS_TAXONOMY: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # SOFTWARE DEVELOPMENT & WEB ENGINEERING
    # =========================================================================
    "Python": {
        "category": "Programming Languages",
        "aliases": ["python", "python3", "python 3", "py"],
        "related": ["FastAPI", "Django", "Flask", "Pandas"],
        "domain": "software_development",
    },
    "JavaScript": {
        "category": "Programming Languages",
        "aliases": ["javascript", "js", "ecmascript", "es6", "es6+"],
        "related": ["TypeScript", "React", "Node.js", "Vue.js"],
        "domain": "software_development",
    },
    "TypeScript": {
        "category": "Programming Languages",
        "aliases": ["typescript", "ts"],
        "related": ["JavaScript", "React", "Angular", "Node.js"],
        "domain": "software_development",
    },
    "Java": {
        "category": "Programming Languages",
        "aliases": ["java", "java 8", "java 11", "java 17", "java 21"],
        "related": ["Spring Boot", "Kotlin", "Hibernate"],
        "domain": "software_development",
    },
    "C++": {
        "category": "Programming Languages",
        "aliases": ["c++", "cpp"],
        "related": ["C", "Rust", "Embedded Systems"],
        "domain": "software_development",
    },
    "C#": {
        "category": "Programming Languages",
        "aliases": ["c#", "csharp", ".net", "dotnet"],
        "related": ["ASP.NET", "Unity", "Azure"],
        "domain": "software_development",
    },
    "Go": {
        "category": "Programming Languages",
        "aliases": ["golang", "go language", "go lang"],
        "ambiguous_aliases": ["go"],  # requires contextual verification
        "related": ["Docker", "Kubernetes", "Microservices", "gRPC"],
        "domain": "software_development",
    },
    "Rust": {
        "category": "Programming Languages",
        "aliases": ["rust", "rustlang"],
        "related": ["C++", "Systems Programming", "WebAssembly"],
        "domain": "software_development",
    },
    "SQL": {
        "category": "Databases & Querying",
        "aliases": ["sql", "structured query language"],
        "related": ["PostgreSQL", "MySQL", "Database Design"],
        "domain": "software_development",
    },
    "React": {
        "category": "Frontend Frameworks",
        "aliases": ["react", "react.js", "reactjs", "react native"],
        "related": ["Next.js", "JavaScript", "TypeScript", "Redux", "Frontend Development"],
        "domain": "software_development",
    },
    "Next.js": {
        "category": "Frontend Frameworks",
        "aliases": ["next.js", "nextjs", "next js"],
        "related": ["React", "JavaScript", "TypeScript", "SSR"],
        "domain": "software_development",
    },
    "Vue.js": {
        "category": "Frontend Frameworks",
        "aliases": ["vue", "vue.js", "vuejs"],
        "related": ["JavaScript", "React", "Nuxt.js"],
        "domain": "software_development",
    },
    "Angular": {
        "category": "Frontend Frameworks",
        "aliases": ["angular", "angularjs", "angular 2+"],
        "related": ["TypeScript", "JavaScript", "RxJS"],
        "domain": "software_development",
    },
    "Node.js": {
        "category": "Backend Frameworks",
        "aliases": ["node.js", "nodejs", "node js", "node"],
        "related": ["Express", "JavaScript", "TypeScript", "REST APIs"],
        "domain": "software_development",
    },
    "FastAPI": {
        "category": "Backend Frameworks",
        "aliases": ["fastapi", "fast api"],
        "related": ["Python", "REST APIs", "AsyncIO", "Pydantic"],
        "domain": "software_development",
    },
    "Django": {
        "category": "Backend Frameworks",
        "aliases": ["django", "django rest framework", "drf"],
        "related": ["Python", "PostgreSQL", "REST APIs"],
        "domain": "software_development",
    },
    "Flask": {
        "category": "Backend Frameworks",
        "aliases": ["flask"],
        "related": ["Python", "FastAPI", "Microservices"],
        "domain": "software_development",
    },
    "Spring Boot": {
        "category": "Backend Frameworks",
        "aliases": ["spring boot", "springboot", "spring framework", "spring"],
        "related": ["Java", "Microservices", "REST APIs"],
        "domain": "software_development",
    },
    "PostgreSQL": {
        "category": "Databases & Storage",
        "aliases": ["postgresql", "postgres", "psql"],
        "related": ["SQL", "Relational Databases", "MySQL", "Database Optimization"],
        "domain": "software_development",
    },
    "MySQL": {
        "category": "Databases & Storage",
        "aliases": ["mysql"],
        "related": ["PostgreSQL", "SQL", "Relational Databases"],
        "domain": "software_development",
    },
    "MongoDB": {
        "category": "Databases & Storage",
        "aliases": ["mongodb", "mongo"],
        "related": ["NoSQL", "Document Databases", "Redis"],
        "domain": "software_development",
    },
    "Redis": {
        "category": "Databases & Storage",
        "aliases": ["redis", "redis cache"],
        "related": ["Caching", "In-Memory Databases", "Distributed Systems"],
        "domain": "software_development",
    },
    "REST APIs": {
        "category": "API & Architecture",
        "aliases": ["rest api", "restful", "restful apis", "rest apis", "restful services", "rest web services"],
        "related": ["FastAPI", "GraphQL", "API Design", "Microservices"],
        "domain": "software_development",
    },
    "GraphQL": {
        "category": "API & Architecture",
        "aliases": ["graphql", "graph ql", "apollo graphql"],
        "related": ["REST APIs", "API Design", "Node.js"],
        "domain": "software_development",
    },
    "Microservices": {
        "category": "API & Architecture",
        "aliases": ["microservices", "microservice architecture", "distributed architectures"],
        "related": ["Docker", "Kubernetes", "System Design", "REST APIs"],
        "domain": "software_development",
    },
    "System Design": {
        "category": "Architecture",
        "aliases": ["system design", "distributed systems", "high availability", "scalability", "software architecture"],
        "related": ["Microservices", "Redis", "Cloud Architecture"],
        "domain": "software_development",
    },
    "Docker": {
        "category": "Cloud & DevOps",
        "aliases": ["docker", "dockerfile", "docker compose", "docker-compose", "containerization", "containers"],
        "related": ["Kubernetes", "CI/CD", "DevOps"],
        "domain": "software_development",
    },
    "Kubernetes": {
        "category": "Cloud & DevOps",
        "aliases": ["kubernetes", "k8s", "helm charts", "kubectl"],
        "related": ["Docker", "Container Orchestration", "Cloud Infrastructure"],
        "domain": "software_development",
    },
    "AWS": {
        "category": "Cloud & DevOps",
        "aliases": ["aws", "amazon web services", "ec2", "s3", "aws lambda", "cloudwatch"],
        "related": ["Cloud Computing", "Google Cloud", "Azure", "Terraform"],
        "domain": "software_development",
    },
    "Google Cloud": {
        "category": "Cloud & DevOps",
        "aliases": ["google cloud", "gcp", "google cloud platform", "bigquery"],
        "related": ["AWS", "Azure", "Kubernetes"],
        "domain": "software_development",
    },
    "Azure": {
        "category": "Cloud & DevOps",
        "aliases": ["azure", "microsoft azure"],
        "related": ["AWS", "Google Cloud", "C#"],
        "domain": "software_development",
    },
    "CI/CD": {
        "category": "Cloud & DevOps",
        "aliases": ["ci/cd", "ci cd", "continuous integration", "continuous deployment", "github actions", "gitlab ci", "jenkins"],
        "related": ["DevOps", "Docker", "Automated Testing"],
        "domain": "software_development",
    },
    "Git": {
        "category": "Version Control",
        "aliases": ["git", "github", "gitlab", "version control"],
        "related": ["CI/CD", "Collaborative Workflows"],
        "domain": "software_development",
    },
    "Automated Testing": {
        "category": "Quality Assurance",
        "aliases": ["pytest", "automated testing", "unit testing", "integration testing", "playwright", "cypress", "jest"],
        "related": ["Pytest", "Jest", "CI/CD"],
        "domain": "software_development",
    },

    # =========================================================================
    # DATA ANALYTICS, DATA SCIENCE & MACHINE LEARNING
    # =========================================================================
    "Pandas": {
        "category": "Data Analytics",
        "aliases": ["pandas"],
        "related": ["Python", "NumPy", "Data Analysis"],
        "domain": "data_analytics",
    },
    "NumPy": {
        "category": "Data Analytics",
        "aliases": ["numpy"],
        "related": ["Python", "Pandas", "Scikit-Learn"],
        "domain": "data_analytics",
    },
    "Scikit-Learn": {
        "category": "Machine Learning",
        "aliases": ["scikit-learn", "scikit learn", "sklearn"],
        "related": ["Python", "Machine Learning", "Pandas"],
        "domain": "data_analytics",
    },
    "Machine Learning": {
        "category": "Machine Learning",
        "aliases": ["machine learning", "ml", "predictive modeling", "supervised learning", "unsupervised learning"],
        "related": ["Scikit-Learn", "Deep Learning", "Data Science", "Python"],
        "domain": "data_analytics",
    },
    "Deep Learning": {
        "category": "Machine Learning",
        "aliases": ["deep learning", "neural networks", "cnn", "rnn", "transformers"],
        "related": ["PyTorch", "TensorFlow", "Machine Learning"],
        "domain": "data_analytics",
    },
    "PyTorch": {
        "category": "Machine Learning",
        "aliases": ["pytorch"],
        "related": ["Deep Learning", "TensorFlow", "Python"],
        "domain": "data_analytics",
    },
    "TensorFlow": {
        "category": "Machine Learning",
        "aliases": ["tensorflow", "keras"],
        "related": ["Deep Learning", "PyTorch", "Python"],
        "domain": "data_analytics",
    },
    "Tableau": {
        "category": "Data Visualization",
        "aliases": ["tableau", "tableau desktop"],
        "related": ["Power BI", "Data Visualization", "SQL"],
        "domain": "data_analytics",
    },
    "Power BI": {
        "category": "Data Visualization",
        "aliases": ["power bi", "powerbi", "dax"],
        "related": ["Tableau", "Data Visualization", "Excel"],
        "domain": "data_analytics",
    },
    "Excel": {
        "category": "Data Analytics",
        "aliases": ["excel", "microsoft excel", "vlookup", "pivot tables"],
        "related": ["Power BI", "Data Analysis"],
        "domain": "data_analytics",
    },
    "Apache Spark": {
        "category": "Big Data & Engineering",
        "aliases": ["spark", "apache spark", "pyspark"],
        "related": ["Hadoop", "Data Engineering", "SQL"],
        "domain": "data_analytics",
    },
    "Snowflake": {
        "category": "Data Warehousing",
        "aliases": ["snowflake", "data warehouse"],
        "related": ["BigQuery", "SQL", "Data Engineering"],
        "domain": "data_analytics",
    },
    "ETL": {
        "category": "Data Engineering",
        "aliases": ["etl", "extract transform load", "data pipelines", "airflow", "apache airflow"],
        "related": ["SQL", "Data Engineering", "Python"],
        "domain": "data_analytics",
    },
    "NLP": {
        "category": "Artificial Intelligence",
        "aliases": ["nlp", "natural language processing", "llm", "large language models", "prompt engineering"],
        "related": ["Machine Learning", "Deep Learning", "Python"],
        "domain": "data_analytics",
    },

    # =========================================================================
    # CYBERSECURITY & INFORMATION SECURITY
    # =========================================================================
    "Penetration Testing": {
        "category": "Offensive Security",
        "aliases": ["penetration testing", "pen testing", "ethical hacking", "vulnerability assessment"],
        "related": ["Metasploit", "Burp Suite", "Kali Linux", "Network Security"],
        "domain": "cybersecurity",
    },
    "Network Security": {
        "category": "Security Engineering",
        "aliases": ["network security", "firewalls", "ids/ips", "vpn", "tcp/ip security"],
        "related": ["Wireshark", "Cybersecurity", "Zero Trust"],
        "domain": "cybersecurity",
    },
    "SIEM": {
        "category": "Security Operations",
        "aliases": ["siem", "splunk", "security information and event management", "soc"],
        "related": ["Incident Response", "Threat Hunting", "Log Analysis"],
        "domain": "cybersecurity",
    },
    "Incident Response": {
        "category": "Security Operations",
        "aliases": ["incident response", "digital forensics", "dfir", "threat containment"],
        "related": ["SIEM", "Cybersecurity", "Malware Analysis"],
        "domain": "cybersecurity",
    },
    "Vulnerability Management": {
        "category": "Security Operations",
        "aliases": ["vulnerability management", "vulnerability scanning", "qualys", "nessus"],
        "related": ["Penetration Testing", "Security Compliance"],
        "domain": "cybersecurity",
    },
    "Identity & Access Management": {
        "category": "Security Engineering",
        "aliases": ["iam", "identity and access management", "oauth", "saml", "active directory", "sso", "rbac"],
        "related": ["Zero Trust", "Cloud Security"],
        "domain": "cybersecurity",
    },
    "Zero Trust": {
        "category": "Security Architecture",
        "aliases": ["zero trust", "zero trust architecture", "zta"],
        "related": ["Identity & Access Management", "Network Security"],
        "domain": "cybersecurity",
    },
    "Cryptography": {
        "category": "Security Engineering",
        "aliases": ["cryptography", "encryption", "tls/ssl", "pki", "public key infrastructure"],
        "related": ["Cybersecurity", "Network Security"],
        "domain": "cybersecurity",
    },
    "Security Compliance": {
        "category": "Governance & Compliance",
        "aliases": ["iso 27001", "nist", "soc 2", "gdpr", "hipaa", "owasp", "owasp top 10", "cis controls"],
        "related": ["Cybersecurity", "Threat Modeling"],
        "domain": "cybersecurity",
    },
    "Wireshark": {
        "category": "Security Tools",
        "aliases": ["wireshark", "packet analysis", "pcap"],
        "related": ["Network Security", "Nmap"],
        "domain": "cybersecurity",
    },
    "Metasploit": {
        "category": "Security Tools",
        "aliases": ["metasploit", "metasploit framework"],
        "related": ["Penetration Testing", "Burp Suite", "Kali Linux"],
        "domain": "cybersecurity",
    },
    "Burp Suite": {
        "category": "Security Tools",
        "aliases": ["burp suite", "burpsuite"],
        "related": ["Penetration Testing", "Web Application Security"],
        "domain": "cybersecurity",
    },
}


def get_all_canonical_skills() -> List[str]:
    """Returns a list of all canonical skill names in the taxonomy."""
    return list(SKILLS_TAXONOMY.keys())


def normalize_skill_name(raw_name: str) -> str:
    """
    Given any skill term or alias, returns the canonical skill name if recognized.
    Returns the cleaned raw_name if not recognized in taxonomy.
    """
    clean_term = raw_name.strip().lower()
    for canonical, data in SKILLS_TAXONOMY.items():
        if canonical.lower() == clean_term:
            return canonical
        for alias in data.get("aliases", []):
            if alias.lower() == clean_term:
                return canonical
        for ambig in data.get("ambiguous_aliases", []):
            if ambig.lower() == clean_term:
                return canonical
    return raw_name.strip()
