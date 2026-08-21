import os
import json
import traceback
from .llm_service import get_groq_client, call_groq_chat


def generate_career_intelligence(resume_text, jd_text):
    try:
        client = get_groq_client()

        prompt = f"""You are a top-tier senior technical recruiter and ATS career strategist.
Analyze this RESUME against the JOB DESCRIPTION (or target role) and perform a comprehensive, rigorous skill gap analysis.

RESUME:
{resume_text}

JOB DESCRIPTION / TARGET ROLE:
{jd_text}

INSTRUCTIONS:
1. "detected_role": Detect the candidate's exact primary target role based on the resume and job description.
2. "experience_level": Determine candidate level (Junior, Mid-level, Senior, Lead, Executive).
3. "critical_skill_gaps": Identify 3 to 5 CRITICAL technical skills, tools, or methodologies required for this role that are missing or underdeveloped in the candidate's resume. MANDATORY: ALWAYS return 3-5 items, never leave empty.
4. "advanced_skill_gaps": Identify 3 to 5 ADVANCED or NEXT-LEVEL skills/concepts (e.g., System Architecture, CI/CD, Cloud Deployment, Performance Optimization, Containerization) that would elevate this candidate. MANDATORY: ALWAYS return 3-5 items, never leave empty.
5. "resume_weaknesses": Identify 3 to 5 SPECIFIC weaknesses or areas of improvement in the resume (e.g. lack of quantified impact/metrics, missing testing experience, unexplicit experience level, lack of cloud/DevOps exposure). MANDATORY: ALWAYS return 3-5 items, never leave empty.
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

        content = response.choices[0].message.content.strip()

        # Clean up if model still adds markdown
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        # Find JSON object in response
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            content = content[start:end]

        result = json.loads(content)
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
        return None