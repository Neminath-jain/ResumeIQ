from django.db import models
from django.contrib.auth.models import User
import json


class ResumeAnalysis(models.Model):

    STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='analyses'
    )

    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    resume_text = models.TextField(blank=True)
    job_description = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS, default='pending')

    # ===== Core ATS =====
    ats_score = models.FloatField(null=True, blank=True)
    keyword_score = models.FloatField(null=True, blank=True)
    semantic_score = models.FloatField(null=True, blank=True)
    experience_score = models.FloatField(null=True, blank=True)
    quality_score = models.FloatField(null=True, blank=True)

    # ===== AI Career Intelligence =====
    detected_role = models.CharField(max_length=200, blank=True)
    experience_level = models.CharField(max_length=100, blank=True)
    critical_skill_gaps_json = models.TextField(default='[]', blank=True)
    advanced_skill_gaps_json = models.TextField(default='[]', blank=True)
    resume_weaknesses_json = models.TextField(default='[]', blank=True)
    career_roadmap_json = models.TextField(default='[]', blank=True)
    personalized_advice = models.TextField(blank=True)

    # ===== RAG Skill Match Breakdown =====
    skill_match_breakdown_json = models.TextField(default='{}', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - Analysis #{self.pk}"

    # ===== JSON Helpers =====

    @property
    def skill_match_breakdown(self):
        try:
            return json.loads(self.skill_match_breakdown_json)
        except Exception:
            return {}

    @skill_match_breakdown.setter
    def skill_match_breakdown(self, value):
        self.skill_match_breakdown_json = json.dumps(value)

    @property
    def critical_skill_gaps(self):
        return json.loads(self.critical_skill_gaps_json)

    @critical_skill_gaps.setter
    def critical_skill_gaps(self, value):
        self.critical_skill_gaps_json = json.dumps(value)

    @property
    def advanced_skill_gaps(self):
        return json.loads(self.advanced_skill_gaps_json)

    @advanced_skill_gaps.setter
    def advanced_skill_gaps(self, value):
        self.advanced_skill_gaps_json = json.dumps(value)

    @property
    def resume_weaknesses(self):
        return json.loads(self.resume_weaknesses_json)

    @resume_weaknesses.setter
    def resume_weaknesses(self, value):
        self.resume_weaknesses_json = json.dumps(value)

    @property
    def career_roadmap(self):
        return json.loads(self.career_roadmap_json)

    @career_roadmap.setter
    def career_roadmap(self, value):
        self.career_roadmap_json = json.dumps(value)