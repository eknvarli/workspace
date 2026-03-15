from __future__ import annotations

import re

import bleach
from django.contrib.auth import get_user_model
from django.utils import timezone
from markdown import markdown as render_markdown
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import AccountProfile
from activity_logs.models import ActivityLog
from announcements.models import Announcement
from attachments.models import Attachment
from calendar_events.models import CalendarEvent
from chat.models import ChatMessage, Conversation, ConversationParticipant
from comments.models import Comment
from comments.models import CommentReaction
from customers.models import Customer
from finance.models import FinanceAlert
from notes.models import Note
from notifications.models import Notification
from organizations.models import Organization, OrganizationInvitation, WorkspaceMember
from projects.models import Project, ProjectMembership
from tasks.models import SubTask, Tag, Task


User = get_user_model()

ALLOWED_MARKDOWN_TAGS = [
    'a', 'abbr', 'b', 'blockquote', 'br', 'code', 'em', 'i', 'li', 'ol', 'p', 'pre', 'strong', 'ul',
    'h1', 'h2', 'h3', 'h4', 'hr'
]
ALLOWED_MARKDOWN_ATTRIBUTES = {
    'a': ['href', 'title', 'rel', 'target'],
    'abbr': ['title'],
    'code': ['class'],
}


def sanitize_markdown(value: str) -> str:
    if not value:
        return ''
    rendered = render_markdown(value, extensions=['extra', 'sane_lists'])
    return bleach.clean(rendered, tags=ALLOWED_MARKDOWN_TAGS, attributes=ALLOWED_MARKDOWN_ATTRIBUTES, strip=True)


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    presence_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'presence_status')

    def get_avatar(self, obj):
        profile = getattr(obj, 'profile', None)
        if profile and profile.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(profile.avatar.url)
            return profile.avatar.url
        return None

    def get_presence_status(self, obj):
        profile = getattr(obj, 'profile', None)
        return getattr(profile, 'presence_status', 'offline')


class AccountProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AccountProfile
        fields = ('user', 'job_title', 'bio', 'locale', 'timezone', 'is_email_verified', 'presence_status', 'last_seen_at')


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    presence_status = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    workspace_roles = serializers.SerializerMethodField()
    teams = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'presence_status', 'profile', 'workspace_roles', 'teams', 'projects')

    def get_avatar(self, obj):
        return UserSerializer(obj, context=self.context).data.get('avatar')

    def get_presence_status(self, obj):
        return UserSerializer(obj, context=self.context).data.get('presence_status')

    def get_profile(self, obj):
        profile = getattr(obj, 'profile', None)
        if not profile:
            return None
        return {
            'job_title': profile.job_title,
            'bio': profile.bio,
            'locale': profile.locale,
            'timezone': profile.timezone,
            'last_seen_at': profile.last_seen_at,
            'is_email_verified': profile.is_email_verified,
        }

    def get_workspace_roles(self, obj):
        organization_id = self.context.get('organization_id')
        memberships = obj.workspace_memberships.select_related('organization')
        if organization_id:
            memberships = memberships.filter(organization_id=organization_id)
        return [
            {
                'organization': membership.organization.name,
                'organization_id': str(membership.organization_id),
                'role': membership.role,
                'title': membership.title,
            }
            for membership in memberships[:8]
        ]

    def get_teams(self, obj):
        memberships = obj.team_memberships.select_related('team')
        organization_id = self.context.get('organization_id')
        if organization_id:
            memberships = memberships.filter(team__organization_id=organization_id)
        return [
            {
                'id': membership.team_id,
                'name': membership.team.name,
                'role': membership.role,
            }
            for membership in memberships[:8]
        ]

    def get_projects(self, obj):
        memberships = obj.project_memberships.select_related('project')
        organization_id = self.context.get('organization_id')
        if organization_id:
            memberships = memberships.filter(project__organization_id=organization_id)
        return [
            {
                'id': membership.project_id,
                'name': membership.project.name,
                'role': membership.role,
            }
            for membership in memberships[:8]
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class WorkspaceTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user, context=self.context).data
        return data


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = WorkspaceMember
        fields = ('id', 'user', 'role', 'title', 'joined_at')


class OrganizationSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ('id', 'name', 'slug', 'description', 'color', 'members', 'created_at')

    def get_members(self, obj):
        memberships = obj.memberships.select_related('user', 'user__profile').all()[:8]
        return WorkspaceMemberSerializer(memberships, many=True, context=self.context).data


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInvitation
        fields = ('id', 'email', 'role', 'token', 'expires_at', 'accepted_at', 'created_at')
        read_only_fields = ('token', 'accepted_at', 'created_at')


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'organization', 'team', 'name', 'slug', 'description', 'color', 'visibility', 'status', 'owner', 'members', 'start_date', 'due_date', 'created_at', 'updated_at')
        read_only_fields = ('slug', 'owner', 'created_at', 'updated_at')

    def get_members(self, obj):
        memberships = obj.project_memberships.select_related('user', 'user__profile').all()
        return [
            {
                'id': membership.user_id,
                'username': membership.user.username,
                'role': membership.role,
            }
            for membership in memberships
        ]


class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = Attachment
        fields = ('id', 'original_name', 'content_type', 'size', 'created_at', 'uploaded_by', 'file')


class ActivityLogSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)

    class Meta:
        model = ActivityLog
        fields = ('id', 'verb', 'metadata', 'created_at', 'actor')


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    mentions = UserSerializer(many=True, read_only=True)
    rendered_body = serializers.SerializerMethodField()
    reaction_summary = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'task', 'author', 'parent', 'body', 'rendered_body', 'mentions', 'reaction_summary', 'created_at', 'updated_at')
        read_only_fields = ('task', 'author', 'mentions', 'created_at', 'updated_at')

    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        usernames = set(re.findall(r'@([\w.@+-]+)', comment.body))
        if usernames:
            mentioned_users = User.objects.filter(username__in=usernames)
            comment.mentions.set(mentioned_users)
        return comment

    def get_rendered_body(self, obj):
        return sanitize_markdown(obj.body)

    def get_reaction_summary(self, obj):
        summary = {}
        request = self.context.get('request')
        current_user_id = request.user.id if request and request.user.is_authenticated else None
        for reaction in obj.reactions.all():
            bucket = summary.setdefault(reaction.emoji, {'emoji': reaction.emoji, 'count': 0, 'active': False})
            bucket['count'] += 1
            if current_user_id and reaction.user_id == current_user_id:
                bucket['active'] = True
        return list(summary.values())


class CommentReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CommentReaction
        fields = ('id', 'emoji', 'user', 'created_at')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'organization', 'name', 'color')
        read_only_fields = ('organization',)


class SubTaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='assignee', write_only=True, allow_null=True, required=False)
    parent_id = serializers.PrimaryKeyRelatedField(queryset=SubTask.objects.all(), source='parent', write_only=True, allow_null=True, required=False)
    children = serializers.SerializerMethodField()

    class Meta:
        model = SubTask
        fields = ('id', 'task', 'title', 'assignee', 'assignee_id', 'parent', 'parent_id', 'due_date', 'is_completed', 'completed_at', 'sort_order', 'children')
        read_only_fields = ('task', 'completed_at', 'parent')

    def validate(self, attrs):
        task = attrs.get('task') or getattr(self.instance, 'task', None)
        parent = attrs.get('parent') or getattr(self.instance, 'parent', None)
        assignee = attrs.get('assignee') or getattr(self.instance, 'assignee', None)

        if parent and task and parent.task_id != task.id:
            raise serializers.ValidationError({'parent_id': 'Parent subtask must belong to the same task.'})

        if assignee and task:
            allowed_user_ids = set(task.project.members.values_list('id', flat=True))
            allowed_user_ids.add(task.creator_id)
            if assignee.id not in allowed_user_ids:
                raise serializers.ValidationError({'assignee_id': 'Assignee must be a project member.'})

        return attrs

    def create(self, validated_data):
        is_completed = validated_data.get('is_completed', False)
        if is_completed:
            validated_data['completed_at'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'is_completed' in validated_data:
            validated_data['completed_at'] = timezone.now() if validated_data['is_completed'] else None
        return super().update(instance, validated_data)

    def get_children(self, obj):
        children = obj.children.select_related('assignee', 'assignee__profile').all()
        return SubTaskSerializer(children, many=True, context=self.context).data


class TaskSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='assignee', write_only=True, allow_null=True, required=False)
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), source='tags', many=True, write_only=True, required=False)
    tags = TagSerializer(many=True, read_only=True)
    subtasks = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    activity_logs = ActivityLogSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    attachments_count = serializers.IntegerField(read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'organization', 'project', 'project_name', 'title', 'description', 'status', 'priority', 'creator', 'assignee', 'assignee_id',
            'due_date', 'start_date', 'completed_at', 'archived_at', 'estimate_minutes', 'sort_order', 'tags', 'tag_ids', 'subtasks',
            'comments', 'attachments', 'activity_logs', 'comments_count', 'attachments_count', 'progress_percentage', 'created_at', 'updated_at'
        )
        read_only_fields = ('creator', 'completed_at', 'archived_at', 'created_at', 'updated_at')

    def validate(self, attrs):
        organization = attrs.get('organization') or getattr(self.instance, 'organization', None)
        project = attrs.get('project') or getattr(self.instance, 'project', None)
        assignee = attrs.get('assignee') or getattr(self.instance, 'assignee', None)
        tags = attrs.get('tags') if 'tags' in attrs else getattr(self.instance, 'tags', Tag.objects.none())

        if project and organization and project.organization_id != organization.id:
            raise serializers.ValidationError({'project': 'Project must belong to the selected organization.'})

        if assignee and organization and not WorkspaceMember.objects.filter(organization=organization, user=assignee).exists():
            raise serializers.ValidationError({'assignee_id': 'Assignee must belong to the selected workspace.'})

        if organization:
            invalid_tags = [tag.id for tag in tags if tag.organization_id != organization.id]
            if invalid_tags:
                raise serializers.ValidationError({'tag_ids': 'All tags must belong to the selected workspace.'})

        return attrs

    def get_subtasks(self, obj):
        roots = [subtask for subtask in obj.subtasks.all() if subtask.parent_id is None]
        return SubTaskSerializer(roots, many=True, context=self.context).data


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'type', 'title', 'message', 'is_read', 'created_at', 'actor', 'task', 'task_title', 'comment', 'data')


class NoteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    rendered_content = serializers.SerializerMethodField()
    project_summary = serializers.SerializerMethodField()
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), source='tags', many=True, write_only=True, required=False)
    tags = TagSerializer(many=True, read_only=True)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Note
        fields = (
            'id', 'organization', 'project', 'project_summary', 'author', 'title', 'content', 'rendered_content',
            'note_type', 'tags', 'tag_ids', 'is_pinned', 'created_at', 'updated_at'
        )
        read_only_fields = ('author', 'created_at', 'updated_at')

    def validate(self, attrs):
        organization = attrs.get('organization') or getattr(self.instance, 'organization', None)
        project = attrs.get('project') or getattr(self.instance, 'project', None)
        tags = attrs.get('tags') if 'tags' in attrs else getattr(self.instance, 'tags', Tag.objects.none())

        if project and organization and project.organization_id != organization.id:
            raise serializers.ValidationError({'project': 'Project must belong to the selected workspace.'})

        if organization:
            invalid_tags = [tag.id for tag in tags if tag.organization_id != organization.id]
            if invalid_tags:
                raise serializers.ValidationError({'tag_ids': 'All tags must belong to the selected workspace.'})

        return attrs

    def get_rendered_content(self, obj):
        return sanitize_markdown(obj.content)

    def get_project_summary(self, obj):
        if not obj.project_id:
            return None
        return {
            'id': obj.project_id,
            'name': obj.project.name,
            'color': obj.project.color,
        }


class AnnouncementSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    rendered_body = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = ('id', 'organization', 'title', 'body', 'rendered_body', 'is_pinned', 'author', 'published_at', 'created_at')
        read_only_fields = ('author', 'published_at', 'created_at')

    def get_rendered_body(self, obj):
        return sanitize_markdown(obj.body)


class CalendarEventSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    attendees = UserSerializer(many=True, read_only=True)
    attendee_ids = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='attendees', many=True, write_only=True, required=False)

    class Meta:
        model = CalendarEvent
        fields = (
            'id', 'organization', 'project', 'title', 'description', 'event_type', 'start_at', 'end_at',
            'location', 'meeting_url', 'created_by', 'attendees', 'attendee_ids', 'attendee_roles', 'reminder_minutes_before', 'created_at'
        )
        read_only_fields = ('created_by', 'created_at')


class CustomerSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = ('id', 'organization', 'owner', 'name', 'company', 'email', 'phone', 'status', 'notes', 'created_at')
        read_only_fields = ('owner', 'created_at')


class FinanceAlertSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = FinanceAlert
        fields = ('id', 'organization', 'project', 'title', 'status', 'severity', 'amount', 'currency', 'due_at', 'notes', 'created_by', 'created_at')
        read_only_fields = ('created_by', 'created_at')


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    rendered_body = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ('id', 'conversation', 'sender', 'body', 'rendered_body', 'created_at')
        read_only_fields = ('conversation', 'sender', 'created_at')

    def get_rendered_body(self, obj):
        return sanitize_markdown(obj.body)


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='participants', many=True, write_only=True, required=False)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'organization', 'name', 'is_direct', 'participants', 'participant_ids', 'last_message', 'updated_at', 'created_at')
        read_only_fields = ('updated_at', 'created_at')

    def get_last_message(self, obj):
        message = obj.messages.select_related('sender', 'sender__profile').order_by('-created_at').first()
        if not message:
            return None
        return ChatMessageSerializer(message, context=self.context).data

    def create(self, validated_data):
        participants = validated_data.pop('participants', [])
        conversation = Conversation.objects.create(**validated_data)
        actor = self.context['request'].user
        ConversationParticipant.objects.get_or_create(conversation=conversation, user=actor)
        for user in participants:
            ConversationParticipant.objects.get_or_create(conversation=conversation, user=user)
        return conversation
