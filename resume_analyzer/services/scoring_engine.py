import re


def compute_ats_score(resume_text, jd_text, resume_data, jd_data):

    resume_skills = [s.lower().strip() for s in resume_data.get("technical_skills", [])]
    required_skills = [s.lower().strip() for s in jd_data.get("required_skills", [])]
    preferred_skills = [s.lower().strip() for s in jd_data.get("preferred_skills", [])]

    resume_text_lower = resume_text.lower()
    jd_text_lower = jd_text.lower()

    if not required_skills:
        keyword_score = 50
    else:
        matched = sum(
            1 for skill in required_skills
            if skill in resume_skills or skill in resume_text_lower
        )
        keyword_score = (matched / len(required_skills)) * 100

    if preferred_skills:
        pref_matched = sum(
            1 for skill in preferred_skills
            if skill in resume_skills or skill in resume_text_lower
        )
        pref_bonus = (pref_matched / len(preferred_skills)) * 15
        keyword_score = min(keyword_score + pref_bonus, 100)

    stop_words = {
        'the','a','an','and','or','but','in','on','at','to','for',
        'of','with','by','from','is','are','was','were','be','been',
        'has','have','had','will','would','could','should','may','might',
        'we','you','they','he','she','it','this','that','these','those',
        'our','your','their','its','as','if','then','than','so','yet',
        'both','either','not','no','nor','just','also','into','about',
        'up','out','over','after','before','through','during','i','me'
    }

    resume_words = set(resume_text_lower.split()) - stop_words
    jd_words = set(jd_text_lower.split()) - stop_words

    if jd_words:
        common_words = resume_words & jd_words
        semantic_score = min((len(common_words) / len(jd_words)) * 100 * 2, 100)
    else:
        semantic_score = 50

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
        experience_score = 60
    elif resume_years == 0:
        experience_score = 40
    elif jd_years == 0:
        experience_score = 70
    elif resume_years >= jd_years:
        experience_score = 100
    elif resume_years >= jd_years - 1:
        experience_score = 80
    elif resume_years >= jd_years - 2:
        experience_score = 60
    else:
        experience_score = 40

    quality_score = 40

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

    quality_score = min(quality_score, 100)

    ats_score = (
        0.40 * keyword_score +
        0.25 * semantic_score +
        0.20 * experience_score +
        0.15 * quality_score
    )

    ats_score = round(min(ats_score, 100), 2)

    label = "Strong Match" if ats_score >= 75 else \
            "Moderate Match" if ats_score >= 50 else \
            "Needs Improvement"

    print(f"=== SCORES === keyword:{keyword_score:.1f} semantic:{semantic_score:.1f} experience:{experience_score:.1f} quality:{quality_score:.1f} → ATS:{ats_score}")

    return {
        "ats_score": ats_score,
        "label": label,
        "breakdown": {
            "keyword_score": round(keyword_score, 2),
            "semantic_score": round(semantic_score, 2),
            "experience_score": round(experience_score, 2),
            "quality_score": round(quality_score, 2),
        }
    }