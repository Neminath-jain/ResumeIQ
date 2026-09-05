import re
import math


def compute_cosine_similarity(vec1, vec2):
    try:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot / (norm1 * norm2))
    except Exception:
        return 0.0


# Known tech acronym / abbreviation mapping for exact aliases (normalized lowercase)
TECH_ALIASES = {
    "ml": "machine learning",
    "machine learning": "machine learning",
    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",
    "dl": "deep learning",
    "deep learning": "deep learning",
    "nlp": "natural language processing",
    "natural language processing": "natural language processing",
    "cv": "computer vision",
    "computer vision": "computer vision",
    "llm": "large language models",
    "llms": "large language models",
    "large language models": "large language models",
    "rag": "retrieval augmented generation",
    "retrieval augmented generation": "retrieval augmented generation",
    "js": "javascript",
    "javascript": "javascript",
    "ts": "typescript",
    "typescript": "typescript",
    "py": "python",
    "python": "python",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "mongo": "mongodb",
    "mongodb": "mongodb",
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "react": "react",
    "reactjs": "react",
    "react.js": "react",
    "vue": "vue",
    "vuejs": "vue",
    "vue.js": "vue",
    "next": "next.js",
    "nextjs": "next.js",
    "next.js": "next.js",
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "express": "express.js",
    "expressjs": "express.js",
    "express.js": "express.js",
    "gcp": "google cloud platform",
    "google cloud": "google cloud platform",
    "google cloud platform": "google cloud platform",
    "aws": "amazon web services",
    "amazon web services": "amazon web services",
    "ci/cd": "continuous integration continuous deployment",
    "cicd": "continuous integration continuous deployment",
    "continuous integration": "continuous integration continuous deployment",
    "continuous deployment": "continuous integration continuous deployment",
    "continuous integration continuous deployment": "continuous integration continuous deployment",
    "go": "golang",
    "golang": "golang",
    "rest": "restful apis",
    "rest api": "restful apis",
    "rest apis": "restful apis",
    "restful api": "restful apis",
    "restful apis": "restful apis",
    "power bi": "power bi",
    "powerbi": "power bi",
    "vector db": "vector databases",
    "vector dbs": "vector databases",
    "vector database": "vector databases",
    "vector databases": "vector databases",
    "excel": "microsoft excel",
    "ms excel": "microsoft excel",
    "microsoft excel": "microsoft excel",
}


def normalize_skill(skill):
    return skill.lower().strip()


def get_skill_variants(skill_str):
    """
    Decompose compound skills into individual canonical variants.
    Handles parentheses like 'SQL (PostgreSQL, MySQL)', slashes 'CI/CD',
    and alternative phrases 'TensorFlow or PyTorch'.
    """
    if not skill_str:
        return set()

    skill_str = str(skill_str).strip()
    variants = {normalize_skill(skill_str)}

    # Remove parentheses content: "SQL (PostgreSQL, MySQL)" -> "sql"
    clean_no_parens = re.sub(r'\(.*?\)', '', skill_str).strip()
    if clean_no_parens:
        variants.add(normalize_skill(clean_no_parens))

    # Extract inside parens: "PostgreSQL, MySQL"
    inside_parens = re.findall(r'\((.*?)\)', skill_str)
    for group in inside_parens:
        for part in re.split(r'[,/|]|(?:\bor\b)', group):
            p = part.strip()
            if p:
                variants.add(normalize_skill(p))

    # Split slashes and 'or' (e.g., "Docker / Kubernetes", "TensorFlow or PyTorch")
    if ' / ' in skill_str or ' or ' in skill_str.lower() or ' | ' in skill_str:
        for part in re.split(r'\s*/\s*|\s+or\s+|\s*\|\s*', skill_str, flags=re.IGNORECASE):
            p = part.strip()
            if p:
                variants.add(normalize_skill(p))

    return variants


def check_exact_or_alias(jd_skill_norm, resume_skill_norm):
    jd_variants = get_skill_variants(jd_skill_norm)
    res_variants = get_skill_variants(resume_skill_norm)

    for jd_var in jd_variants:
        for res_var in res_variants:
            if jd_var == res_var:
                return True

            # Check cleaned alphanumeric equality (e.g. node.js vs nodejs, c++ vs c++)
            clean_jd = "".join(ch for ch in jd_var if ch.isalnum())
            clean_res = "".join(ch for ch in res_var if ch.isalnum())
            if clean_jd and clean_res and clean_jd == clean_res:
                return True

            # Check aliases
            jd_alias = TECH_ALIASES.get(jd_var, jd_var)
            res_alias = TECH_ALIASES.get(res_var, res_var)
            if jd_alias == res_alias:
                return True

    return False


_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print("=== SENTENCE TRANSFORMERS LOAD NOTICE ===", e)
            _embedding_model = False
    return _embedding_model


def match_skills_rag(resume_skills, required_skills, preferred_skills=None, similarity_threshold=0.75):
    """
    High-Performance Lightweight RAG & Vector Skill Matcher.
    Uses TF-IDF character n-gram cosine similarity & SequenceMatcher.
    
    Returns structured dict:
    {
        "exact_matches": [{"jd_skill": ..., "resume_skill": ...}],
        "semantic_matches": [{"jd_skill": ..., "resume_skill": ..., "score": ...}],
        "still_missing_skills": [...],
        "semantic_score": float (0-100),
        "total_required": int
    }
    """
    if preferred_skills is None:
        preferred_skills = []
        
    resume_skills_clean = [s.strip() for s in resume_skills if s and s.strip()]
    required_skills_clean = [s.strip() for s in required_skills if s and s.strip()]
    
    if not required_skills_clean:
        return {
            "exact_matches": [],
            "semantic_matches": [],
            "still_missing_skills": [],
            "semantic_score": 50.0,
            "total_required": 0
        }
        
    if not resume_skills_clean:
        return {
            "exact_matches": [],
            "semantic_matches": [],
            "still_missing_skills": required_skills_clean,
            "semantic_score": 0.0,
            "total_required": len(required_skills_clean)
        }

    exact_matches = []
    semantic_matches = []
    still_missing_skills = []
    
    matched_resume_indices = set()
    unmatched_jd_skills = []
    
    # STEP 1: Exact & Substring Matching
    for jd_skill in required_skills_clean:
        jd_norm = normalize_skill(jd_skill)
        found_exact = False
        
        for idx, res_skill in enumerate(resume_skills_clean):
            res_norm = normalize_skill(res_skill)
            if check_exact_or_alias(jd_norm, res_norm):
                exact_matches.append({
                    "jd_skill": jd_skill,
                    "resume_skill": res_skill,
                    "score": 1.0
                })
                matched_resume_indices.add(idx)
                found_exact = True
                break
                
        if not found_exact:
            unmatched_jd_skills.append(jd_skill)

    # STEP 2: Lightweight Vector & Sub-word N-Gram TF-IDF Matcher
    if unmatched_jd_skills:
        import difflib
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            # Build TF-IDF n-gram vector space
            vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
            corpus = resume_skills_clean + unmatched_jd_skills
            tfidf_matrix = vectorizer.fit_transform([normalize_skill(s) for s in corpus])
            
            n_res = len(resume_skills_clean)
            res_vectors = tfidf_matrix[:n_res]
            jd_vectors = tfidf_matrix[n_res:]
            
            sim_matrix = cosine_similarity(jd_vectors, res_vectors)
            
            for i, jd_skill in enumerate(unmatched_jd_skills):
                jd_norm = normalize_skill(jd_skill)
                best_score = 0.0
                best_match_skill = None
                
                for j, res_skill in enumerate(resume_skills_clean):
                    res_norm = normalize_skill(res_skill)
                    
                    # Compute TF-IDF cosine score
                    vec_score = float(sim_matrix[i, j])
                    
                    # Compute SequenceMatcher string similarity
                    seq_score = difflib.SequenceMatcher(None, jd_norm, res_norm).ratio()
                    
                    # Combined semantic score
                    combined_score = max(vec_score, seq_score)
                    
                    if combined_score > best_score:
                        best_score = combined_score
                        best_match_skill = res_skill
                
                if best_match_skill and best_score >= similarity_threshold:
                    semantic_matches.append({
                        "jd_skill": jd_skill,
                        "resume_skill": best_match_skill,
                        "score": round(float(best_score), 3)
                    })
                else:
                    still_missing_skills.append(jd_skill)

        except Exception as e:
            # Fallback pure difflib string matcher if sklearn is unavailable
            for jd_skill in unmatched_jd_skills:
                jd_norm = normalize_skill(jd_skill)
                best_score = 0.0
                best_match_skill = None
                for res_skill in resume_skills_clean:
                    res_norm = normalize_skill(res_skill)
                    ratio = difflib.SequenceMatcher(None, jd_norm, res_norm).ratio()
                    if ratio > best_score:
                        best_score = ratio
                        best_match_skill = res_skill
                if best_match_skill and best_score >= similarity_threshold:
                    semantic_matches.append({
                        "jd_skill": jd_skill,
                        "resume_skill": best_match_skill,
                        "score": round(float(best_score), 3)
                    })
                else:
                    still_missing_skills.append(jd_skill)

    # Calculate RAG Semantic Sub-score (0-100)
    exact_credits = len(exact_matches) * 1.0
    semantic_credits = sum(m["score"] for m in semantic_matches)
    total_credits = exact_credits + semantic_credits
    
    semantic_score = (total_credits / len(required_skills_clean)) * 100.0
    semantic_score = round(min(semantic_score, 100.0), 2)

    return {
        "exact_matches": exact_matches,
        "semantic_matches": semantic_matches,
        "still_missing_skills": still_missing_skills,
        "semantic_score": semantic_score,
        "total_required": len(required_skills_clean)
    }

