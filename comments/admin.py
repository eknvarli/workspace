from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'author', 'parent', 'created_at')
    list_filter = ('task__organization',)
    search_fields = ('task__title', 'author__username', 'body')
    filter_horizontal = ('mentions',)
