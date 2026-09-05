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
    "qwen/qwen3.8-27b",
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
                "timeout": 15.0,
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



import re

def clean_json(content):
    """Strip markdown code fences and extract JSON object/array substring."""
    if not content:
        return ""
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
    first_brace = content.find("{")
    first_bracket = content.find("[")
    
    if first_brace == -1:
        start = first_bracket
    elif first_bracket == -1:
        start = first_brace
    else:
        start = min(first_brace, first_bracket)

    end_brace = content.rfind("}")
    end_bracket = content.rfind("]")
    end = max(end_brace, end_bracket) + 1
    
    if start != -1 and end > start:
        content = content[start:end]
    return content


def parse_json_robustly(content):
    """Parse JSON string robustly, repairing invalid backslashes, trailing commas, and control chars."""
    cleaned = clean_json(content)
    if not cleaned:
        raise ValueError("Empty content after JSON extraction")

    # 1. Direct standard parse attempt
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2. Fix unescaped backslashes (e.g. C:\path or \d+ or invalid escapes like \P)
    # Replace backslashes not followed by standard escape characters (", \, /, b, f, n, r, t, uXXXX)
    repaired = re.sub(r'\\(?![/"bfnrtu]|u[0-9a-fA-F]{4})', r'\\\\', cleaned)

    # 3. Remove trailing commas in objects and arrays
    repaired = re.sub(r',\s*([\}\]])', r'\1', repaired)

    # Retry standard parse
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # 4. Strict replacement of raw newlines inside JSON string values
    repaired_strict = re.sub(r'(?<!\\)\n', r'\\n', repaired)
    return json.loads(repaired_strict)


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
        return parse_json_robustly(content)
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


def extract_jd_data(job_description):
    try:
        client = get_groq_client()

        prompt = f"""Analyze this job description or target role and extract all technical requirements and skills.

INSTRUCTIONS:
1. If the input is a detailed job description:
   - "required_skills": List all technical skills, programming languages, frameworks, libraries, databases, cloud tools, containerization, and methodologies required.
   - "preferred_skills": List nice-to-have or preferred skills.
   - "experience_required": Required years of experience (e.g. "3 years", "5+ years", "Entry-level").
2. If the input is a job title or target role (e.g. "Full Stack Engineer", "AI Developer", "Data Analyst"):
   - INFER 8-12 industry-standard required technical skills and tools expected for this role.
   - INFER 3-5 standard preferred skills for this role.
   - Estimate typical experience required (e.g. "2+ years").
3. CRITICAL: List skills as individual, atomic names ONLY (e.g. "Python", "React", "PostgreSQL", "Docker"). Never group skills with slashes or parentheses like "SQL (PostgreSQL, MySQL)" or "TensorFlow or PyTorch".

Return ONLY a raw JSON object with no markdown, no code blocks, no explanation:

{{
  "required_skills": ["Python", "Django", "Docker", "CI/CD", "PostgreSQL", "Automated Testing"],
  "preferred_skills": ["Redis", "Kubernetes", "AWS"],
  "experience_required": "3 years"
}}

Job Description / Target Role:
{job_description}"""

        response = call_groq_chat(
            client,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert technical job parser and recruiter. Return only raw JSON. No markdown, no code blocks, no explanation."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        content = response.choices[0].message.content
        result = parse_json_robustly(content)

        # If required_skills is still empty, fallback to role inference
        if not result.get("required_skills"):
            from .skill_extractor import infer_skills_from_role, extract_skills
            inferred = infer_skills_from_role(job_description) or extract_skills(job_description)
            result["required_skills"] = inferred

        return result
    except Exception as e:
        print("=== JD EXTRACT FALLBACK ===", e)
        try:
            from .skill_extractor import extract_skills, infer_skills_from_role
            extracted = extract_skills(job_description)
            if not extracted:
                extracted = infer_skills_from_role(job_description)
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
        return parse_json_robustly(content)
    except Exception as e:
        print("=== BULLETS PARSE ERROR ===", e)
        return bullets


