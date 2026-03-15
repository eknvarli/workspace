from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class Announcement(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=180)
    body = models.TextField()
    is_pinned = models.BooleanField(default=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcements')
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-published_at']
        indexes = [models.Index(fields=['organization', 'published_at'])]

    def __str__(self) -> str:
        return self.title