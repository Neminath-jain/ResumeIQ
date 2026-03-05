from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.core.mail import send_mail
from django.conf import settings as django_settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated

from .models import ResumeAnalysis, EmailVerificationToken
from .serializers import AnalyzeRequestSerializer, ResumeAnalysisSerializer
from .services.pdf_extractor import extract_text_from_pdf
from .services.llm_service import (
    extract_resume_data,
    extract_jd_data,
    improve_bullet_points
)
from .services.scoring_engine import compute_ats_score
from .services.career_ai_engine import generate_career_intelligence

import os
import traceback


# =========================================================
# AUTH VIEW (REGISTER)
# =========================================================

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            token_obj = EmailVerificationToken.objects.create(user=user)

            verify_url = request.build_absolute_uri(
                f'/verify-email/{token_obj.token}/'
            )

            send_mail(
                subject='Verify your email - Resume Analyzer',
                message=f'Hi {user.username},\n\nClick the link below to verify your email:\n\n{verify_url}\n\nIf you did not register, ignore this email.',
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[form.cleaned_data['email']],
                fail_silently=False,
            )

            return render(request, 'auth/verify_email_sent.html', {
                'email': form.cleaned_data['email']
            })
    else:
        form = RegisterForm()

    return render(request, 'auth/register.html', {'form': form})


def verify_email_view(request, token):
    try:
        token_obj = EmailVerificationToken.objects.get(token=token)
        user = token_obj.user
        user.is_active = True
        user.save()
        token_obj.delete()
        return render(request, 'auth/verify_email_success.html')
    except EmailVerificationToken.DoesNotExist:
        return render(request, 'auth/verify_email_invalid.html')


# =========================================================
# NORMAL PAGES (Protected)
# =========================================================

@login_required
def index(request):
    return render(request, 'resume_analyzer/index.html')


@login_required
def result_view(request, pk):
    analysis = get_object_or_404(
        ResumeAnalysis,
        pk=pk,
        user=request.user
    )
    return render(request, 'resume_analyzer/result.html', {'analysis': analysis})


@login_required
def history_view(request):
    analyses = ResumeAnalysis.objects.filter(
        user=request.user
    ).order_by('-created_at')[:20]

    return render(request, 'resume_analyzer/history.html', {'analyses': analyses})


# =========================================================
# API VIEW - ANALYZE RESUME
# =========================================================

class AnalyzeResumeView(APIView):
    parser_classes = [MultiPartParser, JSONParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = AnalyzeRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        jd_text = data['job_description']

        # ---------------------------------
        # Extract Resume Text
        # ---------------------------------

        try:
            if data.get('resume_file'):
                resume_text = extract_text_from_pdf(data['resume_file'])
            else:
                resume_text = data.get('resume_text', '')
        except Exception as e:
            return Response({'error': str(e)}, status=400)

        # ---------------------------------
        # Create Initial Record
        # ---------------------------------

        analysis = ResumeAnalysis.objects.create(
            user=request.user,
            resume_text=resume_text,
            job_description=jd_text,
            status='processing'
        )

        try:
            # =====================================================
            # STEP 1: ATS SCORING
            # =====================================================

            resume_data = extract_resume_data(resume_text)
            jd_data = extract_jd_data(jd_text)

            print("=== RESUME DATA ===", resume_data)
            print("=== JD DATA ===", jd_data)

            score_result = compute_ats_score(
                resume_text,
                jd_text,
                resume_data,
                jd_data
            )

            breakdown = score_result.get("breakdown", {})

            analysis.ats_score = score_result.get("ats_score", 0)
            analysis.keyword_score = breakdown.get("keyword_score", 0)
            analysis.semantic_score = breakdown.get("semantic_score", 0)
            analysis.experience_score = breakdown.get("experience_score", 0)
            analysis.quality_score = breakdown.get("quality_score", 0)

            # =====================================================
            # STEP 2: AI CAREER INTELLIGENCE
            # =====================================================

            try:
                career_ai = generate_career_intelligence(
                    resume_text,
                    jd_text
                )
                print("=== CAREER AI OUTPUT ===", career_ai)

            except Exception as career_err:
                print("=== CAREER AI ERROR ===", str(career_err))
                print(traceback.format_exc())
                career_ai = {}

            resume_skills = [s.lower() for s in resume_data.get("technical_skills", [])]
            required_skills = [s.lower() for s in jd_data.get("required_skills", [])]
            preferred_skills = [s.lower() for s in jd_data.get("preferred_skills", [])]

            # Detected Role
            detected_role = career_ai.get("detected_role", "")
            if not detected_role:
                detected_role = jd_data.get("experience_required", "") or "Software Engineer"

            # Experience Level
            experience_level = career_ai.get("experience_level", "")
            if not experience_level:
                exp = resume_data.get("years_experience", "")
                experience_level = f"{exp} years experience" if exp else "Mid-level"

            # Critical Skill Gaps
            critical_skill_gaps = career_ai.get("critical_skill_gaps", [])
            if not critical_skill_gaps:
                critical_skill_gaps = [
                    skill.title() for skill in required_skills
                    if skill not in resume_skills
                ]

            # Advanced Skill Gaps
            advanced_skill_gaps = career_ai.get("advanced_skill_gaps", [])
            if not advanced_skill_gaps:
                advanced_skill_gaps = [
                    skill.title() for skill in preferred_skills
                    if skill not in resume_skills
                ]

            # Resume Weaknesses
            resume_weaknesses = career_ai.get("resume_weaknesses", [])
            if not resume_weaknesses:
                resume_weaknesses = []
                if not resume_data.get("quantified_achievements"):
                    resume_weaknesses.append("No quantified achievements found — add numbers and metrics to your bullet points.")
                if not resume_data.get("years_experience"):
                    resume_weaknesses.append("Years of experience not clearly stated — make it explicit.")
                if not resume_data.get("projects"):
                    resume_weaknesses.append("No projects listed — add relevant projects to strengthen your resume.")
                if not resume_weaknesses:
                    resume_weaknesses.append("Resume looks good but could use more specific technical details.")

            # Career Roadmap
            career_roadmap = career_ai.get("career_roadmap", [])
            if not career_roadmap:
                career_roadmap = []
                if critical_skill_gaps:
                    career_roadmap.append(f"Learn critical missing skills: {', '.join(critical_skill_gaps[:3])}")
                if advanced_skill_gaps:
                    career_roadmap.append(f"Strengthen advanced skills: {', '.join(advanced_skill_gaps[:3])}")
                career_roadmap.append("Add quantified achievements to every bullet point in your experience section.")
                career_roadmap.append("Build 2-3 portfolio projects that directly match the job requirements.")
                career_roadmap.append("Tailor your resume summary specifically for this role.")

            # Personalized Advice
            personalized_advice = career_ai.get("personalized_advice", "")
            if not personalized_advice:
                matched = len(required_skills) - len(critical_skill_gaps)
                total = len(required_skills) if required_skills else 1
                pct = int((matched / total) * 100)
                personalized_advice = (
                    f"Your resume matches approximately {pct}% of the required skills for this role. "
                    f"Focus on closing the skill gaps in {', '.join(critical_skill_gaps[:2]) if critical_skill_gaps else 'key technical areas'}. "
                    f"Strengthening your resume with quantified achievements and tailoring it to this specific job description will significantly improve your ATS score."
                )

            analysis.detected_role = detected_role
            analysis.experience_level = experience_level
            analysis.critical_skill_gaps = critical_skill_gaps
            analysis.advanced_skill_gaps = advanced_skill_gaps
            analysis.resume_weaknesses = resume_weaknesses
            analysis.career_roadmap = career_roadmap
            analysis.personalized_advice = personalized_advice

            # =====================================================
            # COMPLETE
            # =====================================================

            analysis.status = 'completed'
            analysis.save()

        except Exception as e:
            print("=== FULL ERROR ===", str(e))
            print(traceback.format_exc())
            analysis.status = 'failed'
            analysis.save()
            return Response({'error': str(e)}, status=500)

        return Response(
            {'result_url': f'/result/{analysis.pk}/'},
            status=201
        )


# =========================================================
# API VIEW - GET ANALYSIS DETAIL
# =========================================================

class AnalysisDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        analysis = get_object_or_404(
            ResumeAnalysis,
            pk=pk,
            user=request.user
        )
        return Response(ResumeAnalysisSerializer(analysis).data)