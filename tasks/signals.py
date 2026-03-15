from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.services import create_task_notification
from activity_logs.services import log_task_event

from .models import Task


@receiver(post_save, sender=Task)
def handle_task_saved(sender, instance: Task, created: bool, **kwargs):
    action = 'created' if created else 'updated'
    log_task_event(task=instance, actor=instance.creator, verb=f'task.{action}')
    if instance.assignee_id:
        create_task_notification(task=instance, notification_type='task_assigned' if created else 'task_updated')
