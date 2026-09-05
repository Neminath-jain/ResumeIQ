import re
from .rag_skill_matcher import match_skills_rag, check_exact_or_alias, normalize_skill, get_skill_variants


def is_skill_present(skill, resume_skills_norm, resume_text):
    variants = get_skill_variants(skill)
    resume_text_lower = resume_text.lower()

    # 1. Check in extracted resume skills list using exact/alias matcher
    for v in variants:
        for r_norm in resume_skills_norm:
            if check_exact_or_alias(v, r_norm):
                return True

    # 2. Check each variant in full resume text using word boundary regex
    for v in variants:
        escaped = re.escape(v)
        pattern = r'(?i)\b' + escaped + r'\b'
        if re.search(pattern, resume_text_lower):
            return True

    return False


def compute_ats_score(resume_text, jd_text, resume_data, jd_data):

    resume_skills = [s.strip() for s in resume_data.get("technical_skills", []) if s and s.strip()]
    required_skills = [s.strip() for s in jd_data.get("required_skills", []) if s and s.strip()]
    preferred_skills = [s.strip() for s in jd_data.get("preferred_skills", []) if s and s.strip()]

    resume_skills_norm = [normalize_skill(s) for s in resume_skills]

    # 1. RAG EMBEDDING-BASED SKILL SEMANTIC MATCH (35%)
    rag_match = match_skills_rag(
        resume_skills=resume_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        similarity_threshold=0.75
    )
    semantic_score = rag_match.get("semantic_score", 50.0)

    # 2. KEYWORD MATCH (35%)
    if not required_skills:
        keyword_score = 50.0
    else:
        exact_matched_count = len(rag_match.get("exact_matches", []))
        additional_matched = 0
        for skill in rag_match.get("still_missing_skills", []):
            if is_skill_present(skill, resume_skills_norm, resume_text):
                additional_matched += 1

        matched_total = exact_matched_count + additional_matched
        keyword_score = (matched_total / len(required_skills)) * 100.0

    if preferred_skills:
        pref_matched = sum(
            1 for skill in preferred_skills
            if is_skill_present(skill, resume_skills_norm, resume_text)
        )
        pref_bonus = (pref_matched / len(preferred_skills)) * 10.0
        keyword_score = min(keyword_score + pref_bonus, 100.0)

    # 3. EXPERIENCE MATCH (15%)
    years_exp = resume_data.get("years_experience", "")
    exp_required = jd_data.get("experience_required", "")

    resume_years = 0
    jd_years = 0

    if years_exp:
        nums = re.findall(r'\d+', str(years_exp))
        if nums:
            resume_years = int(nums[0])

    if exp_required:
        nums = re.findall(r'\d+', str(exp_required))
        if nums:
            jd_years = int(nums[0])

    if resume_years == 0 and years_exp:
        experience_score = 60.0
    elif resume_years == 0:
        experience_score = 50.0
    elif jd_years == 0:
        experience_score = 75.0
    elif resume_years >= jd_years:
        experience_score = 100.0
    elif resume_years >= jd_years - 1:
        experience_score = 80.0
    elif resume_years >= jd_years - 2:
        experience_score = 60.0
    else:
        experience_score = 40.0

    # 4. RESUME QUALITY SCORE (15%)
    quality_score = 40.0

    achievements = resume_data.get("quantified_achievements", [])
    if achievements:
        quality_score += min(len(achievements) * 8, 30)

    projects = resume_data.get("projects", [])
    if projects:
        quality_score += min(len(projects) * 5, 15)

    education = resume_data.get("education", "")
    if education:
        quality_score += 10

    numbers_in_resume = len(re.findall(r'\d+%|\$\d+|\d+x|\d+\+', resume_text))
    quality_score += min(numbers_in_resume * 2, 15)

    quality_score = min(quality_score, 100.0)

    # ATS HYBRID OVERALL SCORE (35% / 35% / 15% / 15%)
    ats_score = (
        0.35 * keyword_score +
        0.35 * semantic_score +
        0.15 * experience_score +
        0.15 * quality_score
    )

    ats_score = round(min(ats_score, 100.0), 2)

    label = "Strong Match" if ats_score >= 75 else \
            "Moderate Match" if ats_score >= 50 else \
            "Needs Improvement"

    print(f"=== RAG ATS SCORES === keyword:{keyword_score:.1f} RAG-semantic:{semantic_score:.1f} experience:{experience_score:.1f} quality:{quality_score:.1f} -> ATS:{ats_score}")

    return {
        "ats_score": ats_score,
        "label": label,
        "rag_match": rag_match,
        "breakdown": {
            "keyword_score": round(keyword_score, 2),
            "semantic_score": round(semantic_score, 2),
            "experience_score": round(experience_score, 2),
            "quality_score": round(quality_score, 2),
        }
    }