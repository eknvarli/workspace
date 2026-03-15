from __future__ import annotations

from django.conf import settings
from django.db import models


class Tag(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='task_tags')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='slate')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('organization', 'name')
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'todo', 'To Do'
        IN_PROGRESS = 'in_progress', 'In Progress'
        IN_REVIEW = 'in_review', 'In Review'
        COMPLETED = 'completed', 'Completed'
        ARCHIVED = 'archived', 'Archived'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='tasks')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_tasks_v2')
    due_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    archived_at = models.DateTimeField(blank=True, null=True)
    estimate_minutes = models.PositiveIntegerField(default=0)
    sort_order = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks')
    watchers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='watched_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', '-updated_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'priority']),
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assignee', 'status']),
            models.Index(fields=['due_date']),
        ]

    @property
    def progress_percentage(self) -> int:
        prefetched_subtasks = getattr(self, '_prefetched_objects_cache', {}).get('subtasks')
        if prefetched_subtasks is not None:
            total = len(prefetched_subtasks)
            completed = sum(1 for item in prefetched_subtasks if item.is_completed)
        else:
            total = self.subtasks.count() if self.pk else 0
            completed = self.subtasks.filter(is_completed=True).count() if total else 0

        if total:
            return int((completed / total) * 100)

        status_defaults = {
            self.Status.TODO: 0,
            self.Status.IN_PROGRESS: 55,
            self.Status.IN_REVIEW: 85,
            self.Status.COMPLETED: 100,
            self.Status.ARCHIVED: 100,
        }
        return status_defaults.get(self.status, 0)

    def __str__(self) -> str:
        return self.title


class SubTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', blank=True, null=True)
    title = models.CharField(max_length=255)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_subtasks')
    due_date = models.DateField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'created_at']
        indexes = [models.Index(fields=['task', 'parent', 'sort_order'])]

    def __str__(self) -> str:
        return self.title
