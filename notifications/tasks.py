from celery import shared_task

from .services import broadcast_user_event


@shared_task
def fanout_notification(user_id: int, title: str, message: str) -> None:
    broadcast_user_event(
        user_id=user_id,
        event_type='notification.created',
        payload={'title': title, 'message': message},
    )
