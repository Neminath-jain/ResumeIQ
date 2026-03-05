from django.contrib import admin
from .models import ResumeAnalysis
@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id','status','ats_score','created_at']
    list_filter = ['status']
