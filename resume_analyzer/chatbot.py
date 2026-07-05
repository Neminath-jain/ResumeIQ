

import json
import os

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # free tier, fast + capable

SYSTEM_PROMPT = """You are the AI Career Assistant embedded inside ResumeIQ, \
an AI-powered resume analyzer with ATS compatibility scoring, career \
intelligence (role + experience level detection), and skill gap analysis.

You help with two kinds of questions:
1. How ResumeIQ works — uploading a resume (PDF or pasted text), pasting a \
job description, what the ATS score / keyword / semantic / experience / \
quality breakdown mean, what "skill gaps" and the "career roadmap" are.
2. General resume, career, and job-search advice — and, when the user's \
own analysis results are provided to you as context below, specific, \
personalized advice about their resume.

Rules:
- Keep answers concise and actionable — short paragraphs or a few bullet points.
- Never invent an ATS score, role, or skill gap that wasn't given to you in context.
- If you don't have the user's analysis context and they ask about "my score" \
or "my resume", ask them to run an analysis first or say you don't have that \
detail yet.
- Be warm and encouraging, but honest — don't sugarcoat real weaknesses.
"""


@require_POST
@csrf_protect
def chat_api(request):
    if not GROQ_API_KEY:
        return JsonResponse(
            {"error": "Chatbot is not configured. Set GROQ_API_KEY in your environment."},
            status=500,
        )

    try:
        data = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid request body."}, status=400)

    message = (data.get("message") or "").strip()
    history = data.get("history") or []
    context = data.get("context") or None

    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)
    if len(message) > 2000:
        return JsonResponse({"error": "Message is too long."}, status=400)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if context:
        # Only include fields that are actually present/meaningful.
        lines = []
        if context.get("ats_score") is not None:
            lines.append(f"- ATS score: {context['ats_score']}")
        if context.get("detected_role"):
            lines.append(f"- Detected role: {context['detected_role']}")
        if context.get("experience_level"):
            lines.append(f"- Experience level: {context['experience_level']}")
        if context.get("critical_skill_gaps"):
            lines.append(f"- Critical skill gaps: {', '.join(context['critical_skill_gaps'])}")
        if context.get("advanced_skill_gaps"):
            lines.append(f"- Advanced skill gaps: {', '.join(context['advanced_skill_gaps'])}")
        if context.get("resume_weaknesses"):
            lines.append(f"- Resume weaknesses: {', '.join(context['resume_weaknesses'])}")

        if lines:
            messages.append({
                "role": "system",
                "content": "The user's current resume analysis:\n" + "\n".join(lines),
            })

    # keep conversation short to control token usage / latency
    for turn in history[-10:]:
        role = turn.get("role")
        content = (turn.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message})

    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": 0.6,
                "max_tokens": 500,
            },
            timeout=30,
        )
        resp.raise_for_status()
        reply = resp.json()["choices"][0]["message"]["content"]
        return JsonResponse({"reply": reply})

    except requests.exceptions.RequestException:
        return JsonResponse(
            {"error": "Chat service is unavailable right now. Please try again shortly."},
            status=502,
        )
    except (KeyError, IndexError, ValueError):
        return JsonResponse({"error": "Unexpected response from chat service."}, status=502)
