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
    resume_data = serializers.SerializerMethodField()
    jd_data = serializers.SerializerMethodField()
    missing_skills = serializers.SerializerMethodField()
    suggestions = serializers.SerializerMethodField()
    improved_bullets = serializers.SerializerMethodField()

    class Meta:
        model = ResumeAnalysis
        fields = ['id','status','ats_score','keyword_score','semantic_score',
                  'experience_score','quality_score','resume_data','jd_data',
                  'missing_skills','suggestions','improved_bullets','created_at']

    def get_resume_data(self, obj): return obj.resume_data
    def get_jd_data(self, obj): return obj.jd_data
    def get_missing_skills(self, obj): return obj.missing_skills
    def get_suggestions(self, obj): return obj.suggestions
    def get_improved_bullets(self, obj): return obj.improved_bullets
