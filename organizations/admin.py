from django.contrib import admin

from .models import Organization, OrganizationInvitation, WorkspaceMember


class WorkspaceMemberInline(admin.TabularInline):
    model = WorkspaceMember
    extra = 0


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'slug', 'created_at')
    search_fields = ('name', 'slug', 'owner__username')
    inlines = [WorkspaceMemberInline]


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = ('organization', 'user', 'role', 'joined_at')
    list_filter = ('role', 'organization')
    search_fields = ('organization__name', 'user__username', 'user__email')


@admin.register(OrganizationInvitation)
class OrganizationInvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'organization', 'role', 'expires_at', 'accepted_at')
    list_filter = ('role', 'organization')
    search_fields = ('email', 'organization__name')
