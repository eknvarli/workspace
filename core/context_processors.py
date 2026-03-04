from core.models import UserSettings


def active_theme(request):
    if not request.user.is_authenticated:
        return {'active_theme': 'dark'}

    settings_obj = UserSettings.objects.filter(user=request.user).only('theme').first()
    return {'active_theme': settings_obj.theme if settings_obj else 'dark'}
