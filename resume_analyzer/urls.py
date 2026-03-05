from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('result/<int:pk>/', views.result_view, name='result'),
    path('history/', views.history_view, name='history'),

    # API
    path('api/analyze/', views.AnalyzeResumeView.as_view(), name='api-analyze'),
    path('api/analysis/<int:pk>/', views.AnalysisDetailView.as_view(), name='api-detail'),

    # 🔐 Register page
    path('register/', views.register_view, name='register'),
]