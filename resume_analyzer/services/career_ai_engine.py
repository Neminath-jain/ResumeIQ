import os
import json
from groq import Groq


def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found")
    return Groq(api_key=api_key)


def generate_career_intelligence(resume_text, jd_text):
    client = get_client()

    prompt = f"""Analyze this resume against the job description and return a JSON object.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Return ONLY a JSON object with these exact keys. No markdown, no explanation, just JSON:
{{
  "detected_role": "actual role name detected from resume",
  "experience_level": "Junior or Mid-level or Senior or Lead or Executive",
  "critical_skill_gaps": ["skill1", "skill2"," skill"3,"skill4"],
  "advanced_skill_gaps": ["skill1", "skill2", "skill3", "skill4"],
  "resume_weaknesses": ["weakness1", "weakness2", "weakness3"],
  "career_roadmap": ["action1", "action2", "action3", "action4", "action5"],
  "personalized_advice": "your personalized advice here"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an expert career advisor. You only respond with valid JSON. Never include markdown, code blocks, or explanation. Only output the raw JSON object."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content.strip()
    print("=== RAW GROQ RESPONSE ===", content)

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

    try:
        result = json.loads(content)
        return {
            "detected_role": result.get("detected_role", ""),
            "experience_level": result.get("experience_level", ""),
            "critical_skill_gaps": result.get("critical_skill_gaps", []),
            "advanced_skill_gaps": result.get("advanced_skill_gaps", []),
            "resume_weaknesses": result.get("resume_weaknesses", []),
            "career_roadmap": result.get("career_roadmap", []),
            "personalized_advice": result.get("personalized_advice", ""),
        }
    except Exception as e:
        print("=== JSON PARSE ERROR ===", e)
        return {
            "detected_role": "",
            "experience_level": "",
            "critical_skill_gaps": [],
            "advanced_skill_gaps": [],
            "resume_weaknesses": [],
            "career_roadmap": [],
            "personalized_advice": "",
        }