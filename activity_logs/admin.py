from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('verb', 'organization', 'actor', 'project', 'task', 'created_at')
    list_filter = ('organization', 'verb')
    search_fields = ('verb', 'actor__username', 'project__name', 'task__title')
