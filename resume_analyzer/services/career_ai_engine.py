import os
import json
import traceback
from .llm_service import get_groq_client, call_groq_chat, parse_json_robustly


def generate_career_intelligence(resume_text, jd_text, rag_match=None):
    try:
        client = get_groq_client()

        rag_context = ""
        if rag_match and isinstance(rag_match, dict):
            sem_matches = rag_match.get("semantic_matches", [])
            missing = rag_match.get("still_missing_skills", [])
            
            sem_str = ", ".join([f"{m['jd_skill']} (matched via {m['resume_skill']}: {int(m['score']*100)}%)" for m in sem_matches])
            miss_str = ", ".join(missing)
            
            rag_context = f"\n\nRAG EMBEDDING MATCH BREAKDOWN:\n- Semantically Matched Related Skills: {sem_str if sem_str else 'None'}\n- Still Missing JD Skills: {miss_str if miss_str else 'None'}"

        prompt = f"""You are a top-tier senior technical recruiter and ATS career strategist.
Analyze this RESUME against the JOB DESCRIPTION (or target role) and perform a comprehensive, rigorous skill gap analysis.{rag_context}

RESUME:
{resume_text}

JOB DESCRIPTION / TARGET ROLE:
{jd_text}

INSTRUCTIONS:
1. "detected_role": Detect the candidate's exact primary target role based on the resume and job description.
2. "experience_level": Determine candidate level (Junior, Mid-level, Senior, Lead, Executive).
3. "critical_skill_gaps": Identify 3 to 5 CRITICAL technical skills required for this role that are missing or underdeveloped in the candidate's resume. MANDATORY: ALWAYS prioritize the exact skills listed under 'Still Missing JD Skills' above if any are present.
4. "advanced_skill_gaps": Identify 3 to 5 ADVANCED or NEXT-LEVEL skills/concepts (e.g., System Architecture, CI/CD, Cloud Deployment, Performance Optimization, Containerization) that would elevate this candidate. MANDATORY: ALWAYS return 3-5 items.
5. "resume_weaknesses": Identify 3 to 5 SPECIFIC weaknesses or areas of improvement in the resume (e.g. lack of quantified impact/metrics, missing testing experience, unexplicit experience level, lack of cloud/DevOps exposure). MANDATORY: ALWAYS return 3-5 items.
6. "career_roadmap": Provide 5 sequential, highly actionable career steps to overcome all gaps and achieve career growth.
7. "personalized_advice": Provide a detailed, 3-4 sentence strategic advice paragraph outlining exactly how the candidate can position themselves for maximum success.

Return ONLY a raw JSON object with these exact keys. No markdown, no code blocks, no explanation:
{{
  "detected_role": "Python Developer",
  "experience_level": "Junior",
  "critical_skill_gaps": ["Docker & Containerization", "CI/CD Pipelines (GitHub Actions)", "Automated Testing (Pytest)", "Cloud Services (AWS/GCP)"],
  "advanced_skill_gaps": ["Microservices Architecture", "System Design & Architecture", "Caching Strategies (Redis)", "Database Query Optimization"],
  "resume_weaknesses": ["No quantified metrics or KPIs in experience bullet points", "Lack of documented CI/CD and DevOps experience", "Missing unit and integration testing frameworks", "No cloud deployment or server hosting mentioned"],
  "career_roadmap": ["Learn Docker and containerize all personal projects", "Implement automated CI/CD pipelines using GitHub Actions", "Master unit testing with Pytest and achieve high code coverage", "Deploy a full-stack application to AWS or GCP", "Study system design principles and build scalable APIs"],
  "personalized_advice": "Focus on turning academic and prototype projects into production-ready software by introducing testing, containerization, and CI/CD. Quantify your achievements in bullet points with measurable impact. Learning cloud deployment will significantly increase your ATS score and interview callbacks."
}}"""

        response = call_groq_chat(
            client,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert career advisor. You ONLY respond with raw valid JSON. Never use markdown code blocks, never add explanatory text. Output ONLY the raw JSON object."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        content = response.choices[0].message.content
        result = parse_json_robustly(content)

        return {
            "detected_role": result.get("detected_role", "Software Engineer"),
            "experience_level": result.get("experience_level", "Mid-level"),
            "critical_skill_gaps": result.get("critical_skill_gaps") or [],
            "advanced_skill_gaps": result.get("advanced_skill_gaps") or [],
            "resume_weaknesses": result.get("resume_weaknesses") or [],
            "career_roadmap": result.get("career_roadmap") or [],
            "personalized_advice": result.get("personalized_advice") or "",
        }
    except Exception as e:
        print("=== CAREER AI ERROR ===", e)
        print(traceback.format_exc())
        return {}