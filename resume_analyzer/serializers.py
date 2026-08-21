from rest_framework import serializers
from .models import ResumeAnalysis


class AnalyzeRequestSerializer(serializers.Serializer):
    resume_file = serializers.FileField(required=False)
    resume_text = serializers.CharField(required=False, allow_blank=True)
    job_description = serializers.CharField(required=True)

    def validate(self, data):
        if not data.get('resume_file') and not data.get('resume_text', '').strip():
            raise serializers.ValidationError("Provide either a resume_file (PDF) or resume_text.")
        return data


class ResumeAnalysisSerializer(serializers.ModelSerializer):
    skill_match_breakdown = serializers.SerializerMethodField()

    class Meta:
        model = ResumeAnalysis
        fields = ['id','status','ats_score','keyword_score','semantic_score',
                  'experience_score','quality_score','skill_match_breakdown','detected_role',
                  'experience_level','critical_skill_gaps','advanced_skill_gaps',
                  'resume_weaknesses','career_roadmap','personalized_advice','created_at']

    def get_skill_match_breakdown(self, obj): return obj.skill_match_breakdown
