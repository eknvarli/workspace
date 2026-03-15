from __future__ import annotations

from django.conf import settings
from django.db import models


class Customer(models.Model):
    class Status(models.TextChoices):
        LEAD = 'lead', 'Lead'
        ACTIVE = 'active', 'Active'
        AT_RISK = 'at_risk', 'At Risk'
        INACTIVE = 'inactive', 'Inactive'

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='customers')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_customers')
    name = models.CharField(max_length=160)
    company = models.CharField(max_length=180, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.LEAD)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['organization', 'status'])]

    def __str__(self) -> str:
        return self.name