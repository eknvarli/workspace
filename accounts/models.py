from __future__ import annotations

import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class AccountProfile(models.Model):
    """Extended profile data for a Django auth user."""

    class PresenceStatus(models.TextChoices):
        ONLINE = 'online', 'Online'
        AWAY = 'away', 'Away'
        DO_NOT_DISTURB = 'dnd', 'Do Not Disturb'
        OFFLINE = 'offline', 'Offline'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    job_title = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    locale = models.CharField(max_length=10, default='tr')
    timezone = models.CharField(max_length=50, default='Europe/Istanbul')
    is_email_verified = models.BooleanField(default=False)
    presence_status = models.CharField(max_length=20, choices=PresenceStatus.choices, default=PresenceStatus.OFFLINE)
    last_seen_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__username']

    def __str__(self) -> str:
        return f'{self.user.username} profile'


class BaseToken(models.Model):
    """Common token model for email verification and password reset flows."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def mark_used(self) -> None:
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])

    @property
    def is_valid(self) -> bool:
        return self.used_at is None and self.expires_at > timezone.now()


class EmailVerificationToken(BaseToken):
    @classmethod
    def create_for_user(cls, user):
        return cls.objects.create(user=user, expires_at=timezone.now() + timedelta(days=2))


class PasswordResetToken(BaseToken):
    @classmethod
    def create_for_user(cls, user):
        return cls.objects.create(user=user, expires_at=timezone.now() + timedelta(hours=2))
