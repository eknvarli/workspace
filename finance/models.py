from __future__ import annotations

from django.conf import settings
from django.db import models


class FinanceAlert(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        REVIEW = 'review', 'In Review'
        RESOLVED = 'resolved', 'Resolved'

    class Severity(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='finance_alerts')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, blank=True, null=True, related_name='finance_alerts')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='finance_alerts_created')
    title = models.CharField(max_length=180)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default='TRY')
    due_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['status', '-created_at']
        indexes = [models.Index(fields=['organization', 'status']), models.Index(fields=['severity'])]

    def __str__(self) -> str:
        return self.title