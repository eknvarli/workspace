from __future__ import annotations

from zoneinfo import ZoneInfo

from celery import shared_task
from django.utils import timezone

from notifications.models import Notification
from notifications.services import broadcast_user_event
from organizations.models import WorkspaceMember

from .models import CalendarEvent


@shared_task
def send_upcoming_meeting_notifications() -> int:
    now = timezone.now()
    sent_count = 0
    events = CalendarEvent.objects.filter(
        event_type=CalendarEvent.EventType.MEETING,
        reminders_sent_at__isnull=True,
        start_at__gte=now,
    ).select_related('organization', 'created_by').prefetch_related('attendees__profile')

    for event in events:
        reminder_at = event.start_at - timezone.timedelta(minutes=event.reminder_minutes_before)
        if reminder_at > now:
            continue

        recipients = set(event.attendees.all())
        if event.attendee_roles:
            role_users = WorkspaceMember.objects.filter(
                organization=event.organization,
                role__in=event.attendee_roles,
            ).select_related('user', 'user__profile')
            recipients.update(member.user for member in role_users)

        for user in recipients:
            profile = getattr(user, 'profile', None)
            timezone_name = getattr(profile, 'timezone', 'Europe/Istanbul') or 'Europe/Istanbul'
            try:
                local_start = timezone.localtime(event.start_at, ZoneInfo(timezone_name))
            except Exception:
                local_start = timezone.localtime(event.start_at)
            message = f'{event.title} toplantisi {local_start.strftime("%d.%m.%Y %H:%M")} saatinde basliyor.'
            notification = Notification.objects.create(
                recipient=user,
                organization=event.organization,
                actor=event.created_by,
                type=Notification.Type.MEETING_REMINDER,
                title='Yaklasan toplanti',
                message=message,
                data={'calendar_event_id': event.id, 'meeting_url': event.meeting_url},
            )
            broadcast_user_event(user_id=user.id, event_type='notification.created', payload={'id': notification.id, 'title': notification.title, 'message': notification.message})
            sent_count += 1

        event.reminders_sent_at = now
        event.save(update_fields=['reminders_sent_at'])

    return sent_count