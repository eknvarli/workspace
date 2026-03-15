from __future__ import annotations

from django.conf import settings
from django.db import models


class Conversation(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='conversations')
    name = models.CharField(max_length=160, blank=True)
    is_direct = models.BooleanField(default=False)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ConversationParticipant', related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [models.Index(fields=['organization', 'updated_at'])]

    def __str__(self) -> str:
        return self.name or f'Conversation #{self.pk}'


class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='conversation_participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversation_participants')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('conversation', 'user')
        ordering = ['conversation_id', 'user__username']


class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['conversation', 'created_at'])]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Conversation.objects.filter(pk=self.conversation_id).update(updated_at=self.created_at)

    def __str__(self) -> str:
        return f'Message #{self.pk}'