from __future__ import annotations

from rest_framework.permissions import BasePermission

from organizations.models import WorkspaceMember


class IsWorkspaceMember(BasePermission):
    def has_permission(self, request, view):
        organization_id = request.query_params.get('organization') or request.data.get('organization')
        if not organization_id:
            return True
        return WorkspaceMember.objects.filter(organization_id=organization_id, user=request.user).exists()


class CanManageWorkspaceContent(BasePermission):
    allowed_roles = {
        WorkspaceMember.Role.ADMIN,
        WorkspaceMember.Role.MANAGER,
        WorkspaceMember.Role.MEMBER,
    }

    def has_object_permission(self, request, view, obj):
        organization = getattr(obj, 'organization', None)
        if organization is None and hasattr(obj, 'project'):
            organization = obj.project.organization
        if organization is None:
            return False
        membership = WorkspaceMember.objects.filter(organization=organization, user=request.user)
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return membership.exists()
        return membership.filter(role__in=self.allowed_roles).exists()

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.is_authenticated
        organization_id = request.data.get('organization') or request.query_params.get('organization')
        if not organization_id:
            return request.user.is_authenticated
        return WorkspaceMember.objects.filter(
            organization_id=organization_id,
            user=request.user,
            role__in=self.allowed_roles,
        ).exists()
