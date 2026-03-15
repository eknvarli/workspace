from __future__ import annotations

from django.conf import settings
from django.db import models


class Attachment(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='attachments')
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, blank=True, null=True, related_name='attachments')
    comment = models.ForeignKey('comments.Comment', on_delete=models.CASCADE, blank=True, null=True, related_name='attachments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_attachments')
    file = models.FileField(upload_to='attachments/%Y/%m/')
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=120, blank=True)
    size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.original_name
