from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'author', 'is_pinned', 'published_at')
    list_filter = ('organization', 'is_pinned')
    search_fields = ('title', 'body')