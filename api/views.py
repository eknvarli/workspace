from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import EmailVerificationToken, PasswordResetToken
from announcements.models import Announcement
from attachments.models import Attachment
from calendar_events.models import CalendarEvent
from chat.models import ChatMessage, Conversation
from comments.models import Comment
from comments.models import CommentReaction
from customers.models import Customer
from finance.models import FinanceAlert
from notes.models import Note
from notifications.models import Notification
from organizations.models import Organization, OrganizationInvitation, WorkspaceMember
from organizations.services import get_or_create_personal_workspace
from projects.models import Project
from tasks.models import SubTask, Tag, Task

from .permissions import CanManageWorkspaceContent, IsWorkspaceMember
from .serializers import (
    AnnouncementSerializer,
    CalendarEventSerializer,
    ChatMessageSerializer,
    CommentSerializer,
    ConversationSerializer,
    AttachmentSerializer,
    CustomerSerializer,
    FinanceAlertSerializer,
    NoteSerializer,
    NotificationSerializer,
    OrganizationSerializer,
    ProjectSerializer,
    RegisterSerializer,
    SubTaskSerializer,
    TagSerializer,
    TaskSerializer,
    UserProfileSerializer,
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
        .prefetch_related(
            'tags',
            'subtasks__assignee__profile',
            'subtasks__children__assignee__profile',
            'subtasks__children__children',
            'comments__author__profile',
            'comments__mentions__profile',
            'comments__reactions__user__profile',
            'attachments__uploaded_by__profile',
            'activity_logs__actor__profile',
        )
        .annotate(comments_count=Count('comments'), attachments_count=Count('attachments'))
    )


class TagListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember]

    def get_queryset(self):
        queryset = Tag.objects.filter(organization__memberships__user=self.request.user)
        organization_id = self.request.query_params.get('organization')
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset.order_by('name')

    def perform_create(self, serializer):
        organization = get_object_or_404(Organization.objects.filter(memberships__user=self.request.user), pk=self.request.data.get('organization'))
        serializer.save(organization=organization)


class TaskSubTaskListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SubTaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember]

    def get_task(self):
        return get_object_or_404(
            Task.objects.filter(organization__memberships__user=self.request.user).select_related('project', 'organization'),
            pk=self.kwargs['pk'],
        )

    def get_queryset(self):
        return self.get_task().subtasks.filter(parent__isnull=True).select_related('assignee', 'assignee__profile').prefetch_related('children__assignee__profile', 'children__children__assignee__profile')

    def perform_create(self, serializer):
        task = self.get_task()
        max_order = task.subtasks.filter(parent=serializer.validated_data.get('parent')).order_by('-sort_order').values_list('sort_order', flat=True).first()
        serializer.save(task=task, sort_order=(max_order or 0) + 1)


class SubTaskDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubTaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember]

    def get_queryset(self):
        return SubTask.objects.filter(task__organization__memberships__user=self.request.user).select_related('task', 'task__project', 'assignee', 'assignee__profile', 'parent').prefetch_related('children__assignee__profile')


class TaskSubTaskReorderAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember]

    def post(self, request, pk):
        task = get_object_or_404(Task.objects.filter(organization__memberships__user=request.user), pk=pk)
        items = request.data.get('items', [])
        if not isinstance(items, list):
            return Response({'detail': 'items must be a list.'}, status=status.HTTP_400_BAD_REQUEST)

        subtask_map = {subtask.id: subtask for subtask in task.subtasks.all()}
        with transaction.atomic():
            for index, item in enumerate(items):
                subtask_id = item.get('id')
                parent_id = item.get('parent_id')
                if subtask_id not in subtask_map:
                    return Response({'detail': 'Subtask does not belong to task.'}, status=status.HTTP_400_BAD_REQUEST)
                if parent_id and parent_id not in subtask_map:
                    return Response({'detail': 'Parent subtask does not belong to task.'}, status=status.HTTP_400_BAD_REQUEST)
                SubTask.objects.filter(pk=subtask_id).update(parent_id=parent_id, sort_order=index)

        roots = task.subtasks.filter(parent__isnull=True).select_related('assignee', 'assignee__profile').prefetch_related('children__assignee__profile', 'children__children__assignee__profile')
        return Response(SubTaskSerializer(roots, many=True, context={'request': request}).data)


class TaskCommentCreateAPIView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        task = get_object_or_404(Task.objects.filter(organization__memberships__user=self.request.user), pk=self.kwargs['pk'])
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


class NotificationMarkAllReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        organization_id = request.data.get('organization') or request.query_params.get('organization')
        queryset = Notification.objects.filter(recipient=request.user, is_read=False)
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        updated = queryset.update(is_read=True, read_at=timezone.now())
        return Response({'updated': updated})


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


class NoteListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    pagination_class = DefaultPagination
    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember]

    def get_queryset(self):
        queryset = Note.objects.filter(organization__memberships__user=self.request.user).select_related('author', 'author__profile', 'project').prefetch_related('tags')
        organization_id = self.request.query_params.get('organization')
        project_id = self.request.query_params.get('project')
        note_type = self.request.query_params.get('note_type')
        search = self.request.query_params.get('search')
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if note_type:
            queryset = queryset.filter(note_type=note_type)
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(content__icontains=search) | Q(tags__name__icontains=search)).distinct()
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class NoteDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(organization__memberships__user=self.request.user).select_related('author', 'author__profile', 'project').prefetch_related('tags')


class UserDetailAPIView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = User.objects.filter(workspace_memberships__organization__memberships__user=self.request.user).select_related('profile').prefetch_related(
            'workspace_memberships__organization',
            'team_memberships__team',
            'project_memberships__project',
        ).distinct()
        organization_id = self.request.query_params.get('organization')
        if organization_id:
            queryset = queryset.filter(workspace_memberships__organization_id=organization_id)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['organization_id'] = self.request.query_params.get('organization')
        return context


class TaskAttachmentUploadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        task = get_object_or_404(Task.objects.filter(organization__memberships__user=request.user), pk=pk)
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'detail': 'File is required.'}, status=status.HTTP_400_BAD_REQUEST)

        attachment = Attachment.objects.create(
            organization=task.organization,
            task=task,
            uploaded_by=request.user,
            file=uploaded_file,
            original_name=uploaded_file.name,
            content_type=getattr(uploaded_file, 'content_type', ''),
            size=uploaded_file.size,
        )
        return Response(AttachmentSerializer(attachment, context={'request': request}).data, status=status.HTTP_201_CREATED)


class CommentReactionToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        comment = get_object_or_404(Comment.objects.filter(task__organization__memberships__user=request.user).prefetch_related('reactions'), pk=pk)
        emoji = request.data.get('emoji', '').strip()
        if not emoji:
            return Response({'detail': 'Emoji is required.'}, status=status.HTTP_400_BAD_REQUEST)

        reaction, created = CommentReaction.objects.get_or_create(comment=comment, user=request.user, emoji=emoji)
        active = created
        if not created:
            reaction.delete()
            active = False

        comment = Comment.objects.prefetch_related('reactions').get(pk=comment.pk)
        return Response({'active': active, 'summary': CommentSerializer(comment, context={'request': request}).data['reaction_summary']})


class AnnouncementListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AnnouncementSerializer
    pagination_class = DefaultPagination
    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember, CanManageWorkspaceContent]

    def get_queryset(self):
        queryset = Announcement.objects.filter(organization__memberships__user=self.request.user).select_related('author')
        organization_id = self.request.query_params.get('organization')
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CalendarEventListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CalendarEventSerializer
    pagination_class = DefaultPagination
    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember, CanManageWorkspaceContent]

    def get_queryset(self):
        queryset = CalendarEvent.objects.filter(organization__memberships__user=self.request.user).select_related('project', 'created_by').prefetch_related('attendees__profile')
        organization_id = self.request.query_params.get('organization')
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CalendarEventDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CalendarEventSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageWorkspaceContent]

    def get_queryset(self):
        return CalendarEvent.objects.filter(organization__memberships__user=self.request.user).select_related('project', 'created_by').prefetch_related('attendees__profile')


class CustomerListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer
    pagination_class = DefaultPagination
    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember, CanManageWorkspaceContent]

    def get_queryset(self):
        queryset = Customer.objects.filter(organization__memberships__user=self.request.user).select_related('owner')
        organization_id = self.request.query_params.get('organization')
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CustomerDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageWorkspaceContent]

    def get_queryset(self):
        return Customer.objects.filter(organization__memberships__user=self.request.user).select_related('owner')


class FinanceAlertListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = FinanceAlertSerializer
    pagination_class = DefaultPagination
    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember, CanManageWorkspaceContent]

    def get_queryset(self):
        queryset = FinanceAlert.objects.filter(organization__memberships__user=self.request.user).select_related('project', 'created_by')
        organization_id = self.request.query_params.get('organization')
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class FinanceAlertDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FinanceAlertSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageWorkspaceContent]

    def get_queryset(self):
        return FinanceAlert.objects.filter(organization__memberships__user=self.request.user).select_related('project', 'created_by')


class ConversationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    pagination_class = DefaultPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Conversation.objects.filter(participants=self.request.user).select_related('organization').prefetch_related('participants__profile')
        organization_id = self.request.query_params.get('organization')
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset

    def perform_create(self, serializer):
        organization_id = self.request.data.get('organization')
        if not WorkspaceMember.objects.filter(organization_id=organization_id, user=self.request.user).exists():
            raise PermissionDenied('Conversation permission denied.')
        serializer.save()


class ConversationMessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    pagination_class = DefaultPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_conversation(self):
        return get_object_or_404(Conversation.objects.filter(participants=self.request.user), pk=self.kwargs['pk'])

    def get_queryset(self):
        return self.get_conversation().messages.select_related('sender', 'sender__profile')

    def perform_create(self, serializer):
        serializer.save(conversation=self.get_conversation(), sender=self.request.user)


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
