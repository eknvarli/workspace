from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import EmailVerificationToken, PasswordResetToken
from comments.models import Comment
from notifications.models import Notification
from organizations.models import Organization, OrganizationInvitation, WorkspaceMember
from organizations.services import get_or_create_personal_workspace
from projects.models import Project
from tasks.models import Task

from .permissions import CanManageWorkspaceContent, IsWorkspaceMember
from .serializers import (
    CommentSerializer,
    NotificationSerializer,
    OrganizationSerializer,
    ProjectSerializer,
    RegisterSerializer,
    TaskSerializer,
    UserSerializer,
    WorkspaceTokenObtainPairSerializer,
)


User = get_user_model()


class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        get_or_create_personal_workspace(user)
        EmailVerificationToken.create_for_user(user)


class LoginAPIView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = WorkspaceTokenObtainPairSerializer


class PasswordResetRequestAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        user = User.objects.filter(email__iexact=email).first()
        if user:
            token = PasswordResetToken.create_for_user(user)
            send_mail('Password Reset', f'Use this token to reset your password: {token.token}', 'noreply@example.com', [user.email], fail_silently=True)
        return Response({'detail': 'If the email exists, a reset token has been generated.'})


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token_value = request.data.get('token')
        password = request.data.get('password', '')
        token = PasswordResetToken.objects.filter(token=token_value).select_related('user').first()
        if not token or not token.is_valid:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        token.user.set_password(password)
        token.user.save(update_fields=['password'])
        token.mark_used()
        return Response({'detail': 'Password updated.'})


class EmailVerificationRequestAPIView(APIView):
    def post(self, request):
        token = EmailVerificationToken.create_for_user(request.user)
        send_mail('Verify Email', f'Use this token to verify your email: {token.token}', 'noreply@example.com', [request.user.email], fail_silently=True)
        return Response({'detail': 'Verification token generated.'})


class EmailVerificationConfirmAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token_value = request.data.get('token')
        token = EmailVerificationToken.objects.filter(token=token_value).select_related('user').first()
        if not token or not token.is_valid:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        profile = token.user.profile
        profile.is_email_verified = True
        profile.save(update_fields=['is_email_verified'])
        token.mark_used()
        return Response({'detail': 'Email verified.'})


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    pagination_class = DefaultPagination
    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember, CanManageWorkspaceContent]

    def get_queryset(self):
        queryset = Project.objects.filter(organization__memberships__user=self.request.user).select_related('organization', 'owner', 'team').prefetch_related('project_memberships__user')
        organization_id = self.request.query_params.get('organization')
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset.order_by('name')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProjectDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageWorkspaceContent]
    queryset = Project.objects.select_related('organization', 'owner', 'team').prefetch_related('project_memberships__user')


class TaskListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    pagination_class = DefaultPagination
    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember, CanManageWorkspaceContent]

    def get_queryset(self):
        queryset = (
            Task.objects.filter(organization__memberships__user=self.request.user)
            .select_related('organization', 'project', 'creator', 'assignee', 'creator__profile', 'assignee__profile')
            .prefetch_related('tags', 'subtasks', 'comments__author__profile', 'attachments', 'activity_logs__actor__profile')
            .annotate(comments_count=Count('comments'), attachments_count=Count('attachments'))
        )
        organization_id = self.request.query_params.get('organization')
        project_id = self.request.query_params.get('project')
        status_value = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if status_value:
            queryset = queryset.filter(status=status_value)
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
        return queryset.order_by('sort_order', '-updated_at')

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class TaskDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageWorkspaceContent]
    queryset = (
        Task.objects.select_related('organization', 'project', 'creator', 'assignee', 'creator__profile', 'assignee__profile')
        .prefetch_related('tags', 'subtasks', 'comments__author__profile', 'comments__mentions__profile', 'attachments__uploaded_by__profile', 'activity_logs__actor__profile')
        .annotate(comments_count=Count('comments'), attachments_count=Count('attachments'))
    )


class TaskCommentCreateAPIView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs['pk'])
        serializer.save(task=task, author=self.request.user)


class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    pagination_class = DefaultPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user).select_related('actor', 'task', 'comment')
        organization_id = self.request.query_params.get('organization')
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset


class GlobalSearchAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        organization_id = request.query_params.get('organization')
        if not query:
            return Response({'tasks': [], 'projects': [], 'users': []})

        allowed_orgs = Organization.objects.filter(memberships__user=request.user)
        task_qs = Task.objects.filter(organization__in=allowed_orgs, title__icontains=query).select_related('assignee')
        project_qs = Project.objects.filter(organization__in=allowed_orgs, name__icontains=query)
        if organization_id:
            task_qs = task_qs.filter(organization_id=organization_id)
            project_qs = project_qs.filter(organization_id=organization_id)
        user_qs = User.objects.filter(workspace_memberships__organization__in=allowed_orgs).filter(Q(username__icontains=query) | Q(email__icontains=query)).distinct()
        return Response({
            'tasks': TaskSerializer(task_qs[:8], many=True, context={'request': request}).data,
            'projects': ProjectSerializer(project_qs[:8], many=True, context={'request': request}).data,
            'users': UserSerializer(user_qs[:8], many=True, context={'request': request}).data,
        })


class OrganizationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(memberships__user=self.request.user).prefetch_related('memberships__user', 'memberships__user__profile').distinct()

    def perform_create(self, serializer):
        organization = serializer.save(owner=self.request.user)
        WorkspaceMember.objects.get_or_create(organization=organization, user=self.request.user, defaults={'role': WorkspaceMember.Role.ADMIN})


class OrganizationInviteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        organization = get_object_or_404(Organization, pk=pk, memberships__user=request.user)
        membership = WorkspaceMember.objects.filter(organization=organization, user=request.user).first()
        if not membership or membership.role not in {WorkspaceMember.Role.ADMIN, WorkspaceMember.Role.MANAGER}:
            return Response({'detail': 'Invitation permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        email = request.data.get('email', '').strip()
        role = request.data.get('role', WorkspaceMember.Role.MEMBER)
        invitation = OrganizationInvitation.objects.create(
            organization=organization,
            email=email,
            role=role,
            invited_by=request.user,
        )
        send_mail(
            'Workspace Invitation',
            f'You have been invited to {organization.name}. Invitation token: {invitation.token}',
            'noreply@example.com',
            [email],
            fail_silently=True,
        )
        return Response({'detail': 'Invitation created.', 'token': str(invitation.token)}, status=status.HTTP_201_CREATED)
