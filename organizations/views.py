from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch
from django.shortcuts import redirect, render

from accounts.models import AccountProfile
from activity_logs.models import ActivityLog
from notifications.models import Notification
from projects.models import Project, ProjectMembership
from tasks.models import Task

from .models import Organization, WorkspaceMember
from .services import get_current_organization


@login_required
def dashboard(request):
    AccountProfile.objects.get_or_create(user=request.user)
    current_org = get_current_organization(user=request.user, slug=request.GET.get('workspace'))
    view_mode = request.GET.get('view', 'list')
    tasks = (
        Task.objects.filter(organization=current_org)
        .select_related('project', 'assignee', 'creator', 'assignee__profile', 'creator__profile')
        .prefetch_related('tags', 'subtasks')
        .annotate(comments_count=Count('comments'), attachments_count=Count('attachments'))
        .order_by('sort_order', '-updated_at')
    )
    projects = (
        Project.objects.filter(organization=current_org)
        .select_related('owner', 'team')
        .prefetch_related(Prefetch('project_memberships', queryset=ProjectMembership.objects.select_related('user')))
        .order_by('name')
    )
    notifications = Notification.objects.filter(recipient=request.user, organization=current_org).select_related('actor', 'task')[:8]
    activity_logs = ActivityLog.objects.filter(organization=current_org).select_related('actor', 'task', 'project')[:10]
    memberships = current_org.memberships.select_related('user', 'user__profile').all()
    organizations = Organization.objects.filter(memberships__user=request.user).distinct().order_by('name')

    status_columns = []
    for status, label in Task.Status.choices:
        status_columns.append({'value': status, 'label': label, 'items': [task for task in tasks if task.status == status]})

    context = {
        'organizations': organizations,
        'current_organization': current_org,
        'memberships': memberships,
        'projects': projects[:8],
        'tasks': tasks[:25],
        'all_tasks': tasks,
        'status_columns': status_columns,
        'notifications': notifications,
        'activity_logs': activity_logs,
        'view_mode': view_mode,
        'task_statuses': Task.Status.choices,
        'task_priorities': Task.Priority.choices,
    }
    return render(request, 'collab/dashboard.html', context)


@login_required
def notifications_page(request):
    current_org = get_current_organization(user=request.user, slug=request.GET.get('workspace'))
    Notification.objects.filter(recipient=request.user, organization=current_org, is_read=False).update(is_read=True)
    return redirect(f'/?workspace={current_org.slug}')
