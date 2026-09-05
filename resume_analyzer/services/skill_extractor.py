import re

# Comprehensive catalog of technical skills across modern software engineering, data, AI, and DevOps
TECHNICAL_SKILLS_CATALOG = {
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "golang", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "dart", "shell", "bash", "powershell",
    "sql", "html", "html5", "css", "css3", "sass", "scss",

    # Web & Backend Frameworks
    "django", "fastapi", "flask", "express", "express.js", "node.js", "nodejs", "nestjs",
    "spring", "spring boot", "asp.net", ".net", "laravel", "ruby on rails", "rails",
    "graphql", "rest", "rest api", "restful apis", "grpc", "microservices",

    # Frontend Libraries & Frameworks
    "react", "react.js", "reactjs", "next.js", "nextjs", "vue", "vue.js", "vuejs",
    "nuxt.js", "angular", "svelte", "sveltekit", "redux", "zustand", "tailwind css",
    "bootstrap", "material-ui", "webpack", "vite",

    # Databases & Storage
    "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "firebase", "supabase", "mariadb", "neo4j", "oracle",
    "qdrant", "chroma", "chromadb", "pinecone", "milvus", "weaviate",

    # AI, ML & Data Science
    "machine learning", "deep learning", "artificial intelligence", "data science",
    "neural networks", "nlp", "natural language processing", "computer vision", "llm",
    "large language models", "prompt engineering", "rag", "retrieval augmented generation",
    "langchain", "llamaindex", "huggingface", "transformers", "pytorch", "tensorflow",
    "keras", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "scipy",
    "opencv", "spacy", "nltk", "xgboost", "lightgbm",

    # Cloud, DevOps & Infrastructure
    "aws", "amazon web services", "azure", "gcp", "google cloud platform", "google cloud",
    "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins", "github actions",
    "gitlab ci", "ci/cd", "continuous integration", "helm", "linux", "unix", "nginx",
    "apache", "serverless", "lambda",

    # Data Engineering & Analytics
    "power bi", "powerbi", "tableau", "excel", "ms excel", "spark", "apache spark",
    "hadoop", "kafka", "airflow", "dbt", "snowflake", "bigquery", "data modeling",
    "etl", "data pipelines", "statistics", "data analysis",

    # Testing & Software Engineering Practices
    "pytest", "unittest", "jest", "cypress", "selenium", "mocha", "junit",
    "automated testing", "unit testing", "integration testing", "tdd", "bdd",
    "git", "github", "gitlab", "bitbucket", "jira", "agile", "scrum",
    "oop", "object oriented programming", "system design", "data structures", "algorithms"
}

# Standard skill sets mapped to common target role titles
ROLE_SKILL_MAP = {
    "full stack": [
        "JavaScript", "TypeScript", "React", "Node.js", "Python", "HTML5", "CSS3",
        "REST APIs", "SQL", "PostgreSQL", "Git", "Docker", "CI/CD"
    ],
    "frontend": [
        "JavaScript", "TypeScript", "React", "Next.js", "HTML5", "CSS3",
        "Tailwind CSS", "Redux", "REST APIs", "Git", "Vite", "Responsive Design"
    ],
    "backend": [
        "Python", "Django", "FastAPI", "Node.js", "PostgreSQL", "SQL",
        "REST APIs", "Redis", "Docker", "Microservices", "Git", "CI/CD", "Automated Testing"
    ],
    "ai engineer": [
        "Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow",
        "LLMs", "RAG", "LangChain", "NLP", "Pandas", "NumPy", "Docker", "Git", "Vector Databases"
    ],
    "ai developer": [
        "Python", "Machine Learning", "Deep Learning", "LLMs", "Prompt Engineering",
        "RAG", "LangChain", "FastAPI", "Pandas", "NumPy", "Git", "Vector Databases"
    ],
    "machine learning": [
        "Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow",
        "Scikit-learn", "Pandas", "NumPy", "Feature Engineering", "Data Modeling", "Git", "SQL"
    ],
    "data scientist": [
        "Python", "R", "SQL", "Machine Learning", "Pandas", "NumPy",
        "Scikit-learn", "Statistics", "Data Visualization", "Matplotlib", "Git"
    ],
    "data analyst": [
        "SQL", "Python", "Pandas", "Excel", "Power BI", "Tableau",
        "Data Visualization", "Data Modeling", "Statistics", "ETL"
    ],
    "devops": [
        "Docker", "Kubernetes", "AWS", "CI/CD", "GitHub Actions", "Terraform",
        "Linux", "Python", "Bash", "Monitoring", "Git", "Ansible"
    ],
    "cloud engineer": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
        "Linux", "CI/CD", "Networking", "Python", "Git"
    ],
    "software engineer": [
        "Python", "Java", "JavaScript", "SQL", "Git", "Data Structures",
        "Algorithms", "OOP", "REST APIs", "Automated Testing", "Docker", "System Design"
    ]
}


def extract_skills(text):
    """
    Rule-based skill extractor that searches for known technical skills in text
    using word-boundary regex matching.
    """
    if not text:
        return []

    text_lower = text.lower()
    matched_skills = []

    for skill in sorted(TECHNICAL_SKILLS_CATALOG, key=len, reverse=True):
        escaped = re.escape(skill)
        pattern = r'(?i)\b' + escaped + r'\b'
        if re.search(pattern, text_lower):
            # Format nicely
            matched_skills.append(skill.title() if len(skill) > 3 else skill.upper())

    return list(dict.fromkeys(matched_skills))


def infer_skills_from_role(role_title):
    """
    Infer standard industry technical skills for a role title.
    """
    if not role_title:
        return []

    role_clean = role_title.lower()
    for key, skills in ROLE_SKILL_MAP.items():
        if key in role_clean:
            return skills

    # Fallback to software engineer skills if role isn't specifically mapped
    return ROLE_SKILL_MAP["software engineer"]
