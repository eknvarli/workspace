from django.contrib import admin

from .models import Team, TeamMembership


class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 0


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'lead', 'updated_at')
    list_filter = ('organization',)
    search_fields = ('name', 'organization__name')
    inlines = [TeamMembershipInline]


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('team', 'user', 'role', 'created_at')
    list_filter = ('role', 'team__organization')
    search_fields = ('team__name', 'user__username', 'user__email')
