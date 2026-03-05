import os
import json
from groq import Groq


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables")
    return Groq(api_key=api_key)


MODEL_NAME = "llama-3.3-70b-versatile"


def clean_json(content):
    """Strip markdown code fences and extract JSON."""
    content = content.strip()
    if "```" in content:
        parts = content.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{") or part.startswith("["):
                content = part
                break
    # Find first { or [ and last } or ]
    start = min(
        content.find("{") if content.find("{") != -1 else len(content),
        content.find("[") if content.find("[") != -1 else len(content)
    )
    end_brace = content.rfind("}")
    end_bracket = content.rfind("]")
    end = max(end_brace, end_bracket) + 1
    if start < end:
        content = content[start:end]
    return content


def extract_resume_data(resume_text):
    client = get_groq_client()

    prompt = f"""Extract structured data from this resume.

Return ONLY a raw JSON object with no markdown, no explanation:

{{
  "technical_skills": ["skill1", "skill2"],
  "years_experience": "3",
  "education": "B.S. Computer Science",
  "projects": ["project1"],
  "quantified_achievements": ["achievement1"]
}}

Resume:
{resume_text}"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a resume parser. Return only raw JSON. No markdown, no code blocks, no explanation."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    content = response.choices[0].message.content
    print("=== RAW RESUME EXTRACT ===", content[:200])

    try:
        return json.loads(clean_json(content))
    except Exception as e:
        print("=== RESUME PARSE ERROR ===", e)
        return {
            "technical_skills": [],
            "years_experience": "",
            "education": "",
            "projects": [],
            "quantified_achievements": []
        }


def extract_jd_data(job_description):
    client = get_groq_client()

    prompt = f"""Extract required skills from this job description.

Return ONLY a raw JSON object with no markdown, no explanation:

{{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1"],
  "experience_required": "3 years"
}}

Job Description:
{job_description}"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a job description parser. Return only raw JSON. No markdown, no code blocks, no explanation."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    content = response.choices[0].message.content
    print("=== RAW JD EXTRACT ===", content[:200])

    try:
        return json.loads(clean_json(content))
    except Exception as e:
        print("=== JD PARSE ERROR ===", e)
        return {
            "required_skills": [],
            "preferred_skills": [],
            "experience_required": ""
        }


def improve_bullet_points(bullets):
    if not bullets:
        return []

    client = get_groq_client()

    prompt = f"""Rewrite these resume bullet points to be achievement-oriented, quantified, and ATS-optimized.

Return ONLY a raw JSON array. No markdown, no explanation.

Bullets:
{bullets}"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "Return only a raw JSON array. No markdown, no explanation."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    content = response.choices[0].message.content
    try:
        return json.loads(clean_json(content))
    except:
        return bullets

