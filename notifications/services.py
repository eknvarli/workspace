from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def broadcast_workspace_event(*, organization_id: str, event_type: str, payload: dict) -> None:
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        f'organization_{organization_id}',
        {'type': 'workspace.event', 'event': event_type, 'payload': payload},
    )


def broadcast_user_event(*, user_id: int, event_type: str, payload: dict) -> None:
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {'type': 'workspace.event', 'event': event_type, 'payload': payload},
    )


def create_task_notification(*, task, notification_type: str) -> Notification | None:
    if not task.assignee_id:
        return None
    title = 'Yeni görev atandı' if notification_type == Notification.Type.TASK_ASSIGNED else 'Görev güncellendi'
    message = f'{task.title} görevi sizinle ilişkilendirildi.' if notification_type == Notification.Type.TASK_ASSIGNED else f'{task.title} görevi güncellendi.'
    notification = Notification.objects.create(
        recipient=task.assignee,
        organization=task.organization,
        actor=task.creator,
        task=task,
        type=notification_type,
        title=title,
        message=message,
        data={'task_id': task.id, 'project_id': task.project_id},
    )
    broadcast_user_event(user_id=task.assignee_id, event_type='notification.created', payload={'id': notification.id, 'title': title, 'message': message})
    broadcast_workspace_event(organization_id=str(task.organization_id), event_type='task.changed', payload={'task_id': task.id, 'status': task.status, 'priority': task.priority})
    return notification


def create_comment_notifications(*, comment) -> list[Notification]:
    notifications = []
    recipients = set(comment.mentions.exclude(id=comment.author_id).values_list('id', flat=True))
    if comment.task.assignee_id and comment.task.assignee_id != comment.author_id:
        recipients.add(comment.task.assignee_id)

    for user_id in recipients:
        notification_type = Notification.Type.COMMENT_MENTION if comment.mentions.filter(id=user_id).exists() else Notification.Type.COMMENT_ADDED
        title = 'Yorumda etiketlendiniz' if notification_type == Notification.Type.COMMENT_MENTION else 'Göreve yeni yorum eklendi'
        notification = Notification.objects.create(
            recipient_id=user_id,
            organization=comment.task.organization,
            actor=comment.author,
            task=comment.task,
            comment=comment,
            type=notification_type,
            title=title,
            message=comment.body[:180],
            data={'task_id': comment.task_id, 'comment_id': comment.id},
        )
        notifications.append(notification)
        broadcast_user_event(user_id=user_id, event_type='notification.created', payload={'id': notification.id, 'title': notification.title, 'message': notification.message})

    broadcast_workspace_event(organization_id=str(comment.task.organization_id), event_type='comment.created', payload={'task_id': comment.task_id, 'comment_id': comment.id, 'author': comment.author.username})
    return notifications
