from django.contrib import admin

from .models import CalendarEvent


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'event_type', 'start_at', 'end_at')
    list_filter = ('organization', 'event_type')
    search_fields = ('title', 'description', 'location')