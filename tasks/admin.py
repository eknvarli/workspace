from django.contrib import admin

from .models import SubTask, Tag, Task


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 0


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'color', 'created_at')
    list_filter = ('organization',)
    search_fields = ('name', 'organization__name')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'project', 'status', 'priority', 'assignee', 'due_date')
    list_filter = ('organization', 'status', 'priority', 'project')
    search_fields = ('title', 'description', 'project__name', 'assignee__username')
    filter_horizontal = ('tags', 'watchers')
    inlines = [SubTaskInline]


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'assignee', 'is_completed', 'due_date')
    list_filter = ('is_completed', 'task__organization')
    search_fields = ('title', 'task__title', 'assignee__username')
