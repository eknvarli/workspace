from django.urls import path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import (
    EmailVerificationConfirmAPIView,
    EmailVerificationRequestAPIView,
    GlobalSearchAPIView,
    LoginAPIView,
    NotificationListAPIView,
    OrganizationInviteAPIView,
    OrganizationListCreateAPIView,
    PasswordResetConfirmAPIView,
    PasswordResetRequestAPIView,
    ProjectDetailAPIView,
    ProjectListCreateAPIView,
    RegisterAPIView,
    TaskCommentCreateAPIView,
    TaskDetailAPIView,
    TaskListCreateAPIView,
)


urlpatterns = [
    path('schema', SpectacularAPIView.as_view(), name='api_schema'),
    path('docs', SpectacularSwaggerView.as_view(url_name='api_schema'), name='api_docs'),
    path('auth/register', RegisterAPIView.as_view(), name='api_register'),
    path('auth/login', LoginAPIView.as_view(), name='api_login'),
    path('auth/password-reset/request', PasswordResetRequestAPIView.as_view(), name='api_password_reset_request'),
    path('auth/password-reset/confirm', PasswordResetConfirmAPIView.as_view(), name='api_password_reset_confirm'),
    path('auth/email-verification/request', EmailVerificationRequestAPIView.as_view(), name='api_email_verification_request'),
    path('auth/email-verification/confirm', EmailVerificationConfirmAPIView.as_view(), name='api_email_verification_confirm'),
    path('organizations', OrganizationListCreateAPIView.as_view(), name='api_organizations'),
    path('organizations/<uuid:pk>/invite', OrganizationInviteAPIView.as_view(), name='api_organization_invite'),
    path('projects', ProjectListCreateAPIView.as_view(), name='api_projects'),
    path('projects/<int:pk>', ProjectDetailAPIView.as_view(), name='api_project_detail'),
    path('tasks', TaskListCreateAPIView.as_view(), name='api_tasks'),
    path('tasks/<int:pk>', TaskDetailAPIView.as_view(), name='api_task_detail'),
    path('tasks/<int:pk>/comments', TaskCommentCreateAPIView.as_view(), name='api_task_comments'),
    path('notifications', NotificationListAPIView.as_view(), name='api_notifications'),
    path('search', GlobalSearchAPIView.as_view(), name='api_search'),
]
