from __future__ import annotations

import re

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import AccountProfile
from activity_logs.models import ActivityLog
from attachments.models import Attachment
from comments.models import Comment
from notifications.models import Notification
from organizations.models import Organization, OrganizationInvitation, WorkspaceMember
from projects.models import Project, ProjectMembership
from tasks.models import SubTask, Tag, Task


User = get_user_model()


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

    class Meta:
        model = Comment
        fields = ('id', 'task', 'author', 'parent', 'body', 'mentions', 'created_at', 'updated_at')
        read_only_fields = ('author', 'mentions', 'created_at', 'updated_at')

    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        usernames = set(re.findall(r'@([\w.@+-]+)', comment.body))
        if usernames:
            mentioned_users = User.objects.filter(username__in=usernames)
            comment.mentions.set(mentioned_users)
        return comment


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color')


class SubTaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)

    class Meta:
        model = SubTask
        fields = ('id', 'title', 'assignee', 'due_date', 'is_completed', 'completed_at', 'sort_order')


class TaskSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='assignee', write_only=True, allow_null=True, required=False)
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), source='tags', many=True, write_only=True, required=False)
    tags = TagSerializer(many=True, read_only=True)
    subtasks = SubTaskSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    activity_logs = ActivityLogSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    attachments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'organization', 'project', 'project_name', 'title', 'description', 'status', 'priority', 'creator', 'assignee', 'assignee_id',
            'due_date', 'start_date', 'completed_at', 'archived_at', 'estimate_minutes', 'sort_order', 'tags', 'tag_ids', 'subtasks',
            'comments', 'attachments', 'activity_logs', 'comments_count', 'attachments_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('creator', 'completed_at', 'archived_at', 'created_at', 'updated_at')


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'type', 'title', 'message', 'is_read', 'created_at', 'actor', 'task', 'task_title', 'comment', 'data')
