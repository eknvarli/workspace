from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from activity_logs.services import log_comment_event
from notifications.services import create_comment_notifications

from .models import Comment


@receiver(post_save, sender=Comment)
def handle_comment_saved(sender, instance: Comment, created: bool, **kwargs):
    if not created:
        return
    log_comment_event(comment=instance, actor=instance.author, verb='comment.created')
    create_comment_notifications(comment=instance)
