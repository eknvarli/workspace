from __future__ import annotations

from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='activity_logs')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='activity_events')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, blank=True, null=True, related_name='activity_logs')
    task = models.ForeignKey('tasks.Task', on_delete=models.SET_NULL, blank=True, null=True, related_name='activity_logs')
    comment = models.ForeignKey('comments.Comment', on_delete=models.SET_NULL, blank=True, null=True, related_name='activity_logs')
    verb = models.CharField(max_length=120)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['organization', 'created_at']), models.Index(fields=['verb'])]

    def __str__(self) -> str:
        return self.verb
