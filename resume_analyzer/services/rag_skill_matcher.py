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


# Known tech acronym / abbreviation mapping for exact aliases
TECH_ALIASES = {
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "reactjs": "react",
    "react.js": "react",
    "vuejs": "vue",
    "vue.js": "vue",
    "nextjs": "next.js",
    "nodejs": "node.js",
    "expressjs": "express.js",
    "gcp": "google cloud platform",
    "aws": "amazon web services",
    "ci/cd": "continuous integration continuous deployment",
}


def normalize_skill(skill):
    return skill.lower().strip()


def check_exact_or_alias(jd_skill_norm, resume_skill_norm):
    if jd_skill_norm == resume_skill_norm:
        return True
    
    # Check cleaned alphanumeric equality (e.g. node.js vs nodejs, c++ vs c++)
    clean_jd = "".join(ch for ch in jd_skill_norm if ch.isalnum())
    clean_res = "".join(ch for ch in resume_skill_norm if ch.isalnum())
    if clean_jd and clean_res and clean_jd == clean_res:
        return True
    
    # Check aliases
    jd_alias = TECH_ALIASES.get(jd_skill_norm, jd_skill_norm)
    res_alias = TECH_ALIASES.get(resume_skill_norm, resume_skill_norm)
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

