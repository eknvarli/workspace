from django.contrib import admin

from .models import AccountProfile, EmailVerificationToken, PasswordResetToken


@admin.register(AccountProfile)
class AccountProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'presence_status', 'is_email_verified', 'updated_at')
    list_filter = ('presence_status', 'is_email_verified')
    search_fields = ('user__username', 'user__email', 'job_title')


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'expires_at', 'used_at', 'created_at')
    search_fields = ('user__username', 'user__email')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'expires_at', 'used_at', 'created_at')
    search_fields = ('user__username', 'user__email')
