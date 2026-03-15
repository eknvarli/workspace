from django.contrib import admin

from .models import ChatMessage, Conversation, ConversationParticipant


class ConversationParticipantInline(admin.TabularInline):
    model = ConversationParticipant
    extra = 0


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization', 'name', 'is_direct', 'updated_at')
    list_filter = ('organization', 'is_direct')
    search_fields = ('name',)
    inlines = [ConversationParticipantInline]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'created_at')
    list_filter = ('conversation__organization',)
    search_fields = ('body', 'sender__username')