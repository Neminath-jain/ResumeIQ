import os
import json
from groq import Groq


from pathlib import Path
from dotenv import load_dotenv

def get_groq_client():
    from django.conf import settings
    api_key = getattr(settings, "GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY")
    if not api_key:
        env_path = Path(__file__).resolve().parent.parent.parent / ".env"
        load_dotenv(dotenv_path=env_path)
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables or .env file")
    return Groq(api_key=api_key)


DEFAULT_MODELS = [
    os.getenv("GROQ_MODEL"),
    "groq/compound-mini",
    "groq/compound",
    "qwen/qwen3.6-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]
MODEL_CANDIDATES = [m for m in DEFAULT_MODELS if m]


def call_groq_chat(client, messages, temperature=0.1, max_tokens=None):
    last_error = None
    for model in MODEL_CANDIDATES:
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            return client.chat.completions.create(**kwargs)
        except Exception as e:
            print(f"=== GROQ MODEL {model} FAILED ({e}), TRYING NEXT CANDIDATE ===")
            last_error = e
            continue
    if last_error:
        raise last_error
    raise RuntimeError("No Groq models available")


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
    try:
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

        response = call_groq_chat(
            client,
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
        return json.loads(clean_json(content))
    except Exception as e:
        print("=== RESUME EXTRACT FALLBACK ===", e)
        try:
            from .skill_extractor import extract_skills
            extracted = extract_skills(resume_text)
        except Exception:
            extracted = []
        return {
            "technical_skills": extracted,
            "years_experience": "",
            "education": "",
            "projects": [],
            "quantified_achievements": []
        }

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
    try:
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

        response = call_groq_chat(
            client,
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
        return json.loads(clean_json(content))
    except Exception as e:
        print("=== JD EXTRACT FALLBACK ===", e)
        try:
            from .skill_extractor import extract_skills
            extracted = extract_skills(job_description)
        except Exception:
            extracted = []
        return {
            "required_skills": extracted,
            "preferred_skills": [],
            "experience_required": ""
        }


def improve_bullet_points(bullets):
    if not bullets:
        return []

    try:
        client = get_groq_client()

        prompt = f"""Rewrite these resume bullet points to be achievement-oriented, quantified, and ATS-optimized.

Return ONLY a raw JSON array. No markdown, no explanation.

Bullets:
{bullets}"""

        response = call_groq_chat(
            client,
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
        return json.loads(clean_json(content))
    except Exception as e:
        print("=== BULLETS PARSE ERROR ===", e)
        return bullets

