from django.utils import timezone
from core.models import UserPresence


class LastActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now = timezone.now()
            last_ping_iso = request.session.get('last_active_ping')
            should_update = True

            if last_ping_iso:
                try:
                    last_ping = timezone.datetime.fromisoformat(last_ping_iso)
                    if timezone.is_naive(last_ping):
                        last_ping = timezone.make_aware(last_ping, timezone.get_current_timezone())
                    should_update = (now - last_ping).total_seconds() >= 60
                except ValueError:
                    should_update = True

            if should_update:
                UserPresence.objects.update_or_create(
                    user=request.user,
                    defaults={'last_active_at': now},
                )
                request.session['last_active_ping'] = now.isoformat()

        return self.get_response(request)
