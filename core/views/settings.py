from django.contrib import messages
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.models import UserSettings


@login_required
def settings_page(request):
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'preferences':
            user_settings.auto_save = request.POST.get('auto_save') == 'on'
            user_settings.theme = request.POST.get('theme', user_settings.theme)
            user_settings.language = request.POST.get('language', user_settings.language)
            user_settings.save(update_fields=['auto_save', 'theme', 'language', 'updated_at'])
            messages.success(request, 'Ayarlar kaydedildi.')
            return redirect('settings')

        if action == 'photo':
            uploaded_file = request.FILES.get('profile_photo')
            remove_photo = request.POST.get('remove_photo') == '1'

            if remove_photo:
                user_settings.profile_photo = None
                user_settings.save(update_fields=['profile_photo', 'updated_at'])
                messages.success(request, 'Profil fotoğrafı kaldırıldı.')
                return redirect('settings')

            if uploaded_file:
                user_settings.profile_photo = uploaded_file
                user_settings.save(update_fields=['profile_photo', 'updated_at'])
                messages.success(request, 'Profil fotoğrafı güncellendi.')
            else:
                messages.error(request, 'Lütfen bir dosya seçin.')
            return redirect('settings')

        if action == 'password':
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            new_password_confirm = request.POST.get('new_password_confirm', '')

            authenticated_user = authenticate(username=request.user.username, password=current_password)
            if not authenticated_user:
                messages.error(request, 'Mevcut şifre hatalı.')
                return redirect('settings')

            if len(new_password) < 8:
                messages.error(request, 'Yeni şifre en az 8 karakter olmalıdır.')
                return redirect('settings')

            if new_password != new_password_confirm:
                messages.error(request, 'Yeni şifreler eşleşmiyor.')
                return redirect('settings')

            request.user.set_password(new_password)
            request.user.save(update_fields=['password'])
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Şifre başarıyla güncellendi.')
            return redirect('settings')

    context = {
        'user_settings': user_settings,
    }
    return render(request, 'core/settings.html', context)
