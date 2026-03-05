from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from resume_analyzer.views import verify_email_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('resume_analyzer.urls')),

    path('login/',
         auth_views.LoginView.as_view(template_name='auth/login.html'),
         name='login'),

    path('logout/',
         auth_views.LogoutView.as_view(),
         name='logout'),

    path('verify-email/<uuid:token>/', verify_email_view, name='verify_email'),

    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='auth/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='auth/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)