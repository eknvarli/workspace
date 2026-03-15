from django.contrib import admin

from .models import Attachment


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'organization', 'task', 'comment', 'uploaded_by', 'created_at')
    list_filter = ('organization',)
    search_fields = ('original_name', 'uploaded_by__username', 'task__title')
