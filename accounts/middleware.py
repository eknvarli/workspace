from __future__ import annotations

from datetime import datetime

from django.utils import timezone

from calendar_events.tasks import send_upcoming_meeting_notifications

from .models import AccountProfile


class AccountActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now = timezone.now()
            last_ping_iso = request.session.get('last_active_ping')
            should_update = True

            if last_ping_iso:
                try:
                    last_ping = datetime.fromisoformat(last_ping_iso)
                    if timezone.is_naive(last_ping):
                        last_ping = timezone.make_aware(last_ping, timezone.get_current_timezone())
                    should_update = (now - last_ping).total_seconds() >= 60
                except ValueError:
                    should_update = True

            if should_update:
                profile, _ = AccountProfile.objects.get_or_create(user=request.user)
                update_fields = ['last_seen_at']
                profile.last_seen_at = now
                if profile.presence_status == AccountProfile.PresenceStatus.OFFLINE:
                    profile.presence_status = AccountProfile.PresenceStatus.ONLINE
                    update_fields.append('presence_status')
                profile.save(update_fields=update_fields)
                request.session['last_active_ping'] = now.isoformat()

                last_meeting_check_iso = request.session.get('last_meeting_reminder_check')
                should_check_meetings = True
                if last_meeting_check_iso:
                    try:
                        last_meeting_check = datetime.fromisoformat(last_meeting_check_iso)
                        if timezone.is_naive(last_meeting_check):
                            last_meeting_check = timezone.make_aware(last_meeting_check, timezone.get_current_timezone())
                        should_check_meetings = (now - last_meeting_check).total_seconds() >= 300
                    except ValueError:
                        should_check_meetings = True

                if should_check_meetings:
                    try:
                        send_upcoming_meeting_notifications.delay()
                    except Exception:
                        send_upcoming_meeting_notifications()
                    request.session['last_meeting_reminder_check'] = now.isoformat()

        return self.get_response(request)