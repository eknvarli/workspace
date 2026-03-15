from __future__ import annotations

from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        TASK_ASSIGNED = 'task_assigned', 'Task Assigned'
        TASK_UPDATED = 'task_updated', 'Task Updated'
        COMMENT_ADDED = 'comment_added', 'Comment Added'
        COMMENT_MENTION = 'comment_mention', 'Comment Mention'
        INVITATION = 'invitation', 'Invitation'

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='sent_notifications')
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, blank=True, null=True, related_name='notifications')
    comment = models.ForeignKey('comments.Comment', on_delete=models.CASCADE, blank=True, null=True, related_name='notifications')
    type = models.CharField(max_length=32, choices=Type.choices)
    title = models.CharField(max_length=160)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['recipient', 'is_read', 'created_at'])]

    def __str__(self) -> str:
        return f'{self.recipient} - {self.type}'
