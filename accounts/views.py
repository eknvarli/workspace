from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render

from .forms import AccountProfileForm, AccountUserForm, StyledPasswordChangeForm
from .models import AccountProfile
from organizations.services import get_or_create_personal_workspace


def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = AuthenticationForm(request, data=request.POST or None)
    for field in form.fields.values():
        field.widget.attrs['class'] = 'ws-input'
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        get_or_create_personal_workspace(form.get_user())
        return redirect('dashboard')
    return render(request, 'collab/login.html', {'form': form})


def register_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = UserCreationForm(request.POST or None)
    for field in form.fields.values():
        field.widget.attrs['class'] = 'ws-input'
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        get_or_create_personal_workspace(user)
        login(request, user)
        messages.success(request, 'Hesabınız oluşturuldu.')
        return redirect('dashboard')
    return render(request, 'collab/register.html', {'form': form})


@login_required
def logout_page(request):
    logout(request)
    return redirect('login')


@login_required
def settings_page(request):
    profile, _ = AccountProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST' and request.POST.get('action') == 'password':
        user_form = AccountUserForm(instance=request.user)
        profile_form = AccountProfileForm(instance=profile)
        password_form = StyledPasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Sifreniz guncellendi.')
            return redirect('settings')
    elif request.method == 'POST':
        user_form = AccountUserForm(request.POST, instance=request.user)
        profile_form = AccountProfileForm(request.POST, request.FILES, instance=profile)
        password_form = StyledPasswordChangeForm(request.user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Hesap ayarlariniz kaydedildi.')
            return redirect('settings')
    else:
        user_form = AccountUserForm(instance=request.user)
        profile_form = AccountProfileForm(instance=profile)
        password_form = StyledPasswordChangeForm(request.user)

    return render(
        request,
        'collab/settings.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form,
            'profile': profile,
        },
    )
