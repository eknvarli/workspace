from __future__ import annotations

from django.contrib.auth import get_user_model

from .models import Organization, WorkspaceMember


User = get_user_model()


def get_or_create_personal_workspace(user: User) -> Organization:
    membership = WorkspaceMember.objects.select_related('organization').filter(user=user).first()
    if membership:
        return membership.organization

    organization = Organization.objects.create(name=f'{user.username} Workspace', owner=user)
    WorkspaceMember.objects.create(organization=organization, user=user, role=WorkspaceMember.Role.ADMIN)
    return organization


def get_current_organization(*, user: User, slug: str | None = None) -> Organization:
    queryset = Organization.objects.filter(memberships__user=user).distinct()
    if slug:
        organization = queryset.filter(slug=slug).first()
        if organization:
            return organization
    organization = queryset.order_by('name').first()
    if organization:
        return organization
    return get_or_create_personal_workspace(user)
