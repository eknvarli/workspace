from __future__ import annotations

from django.conf import settings
from django.db import models


class Note(models.Model):
    class NoteType(models.TextChoices):
        NOTE = 'note', 'Note'
        DOCUMENTATION = 'documentation', 'Documentation'
        PLAN = 'plan', 'Plan'

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='notes')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='notes', blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=160, blank=True)
    content = models.TextField(blank=True)
    note_type = models.CharField(max_length=20, choices=NoteType.choices, default=NoteType.NOTE)
    tags = models.ManyToManyField('tasks.Tag', blank=True, related_name='notes')
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        indexes = [
            models.Index(fields=['organization', 'updated_at']),
            models.Index(fields=['project', 'note_type']),
        ]

    def __str__(self) -> str:
        return self.title or f'Note #{self.pk}'