from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import AccountProfile
from activity_logs.models import ActivityLog
from announcements.models import Announcement
from calendar_events.models import CalendarEvent
from chat.models import Conversation
from customers.models import Customer
from finance.models import FinanceAlert
from notes.models import Note
from notifications.models import Notification
from projects.models import Project, ProjectMembership
from tasks.models import Tag, Task
from teams.models import Team

from .models import Organization, OrganizationInvitation, WorkspaceMember
from .services import get_current_organization


def get_workspace_shell_context(*, request, current_org: Organization) -> dict:
    organizations = Organization.objects.filter(memberships__user=request.user).distinct().order_by('name')
    memberships = current_org.memberships.select_related('user', 'user__profile').all()
    unread_notifications = Notification.objects.filter(recipient=request.user, organization=current_org, is_read=False).count()
    recent_notifications = Notification.objects.filter(recipient=request.user, organization=current_org).select_related('actor', 'task')[:8]
    sidebar_announcements = Announcement.objects.filter(organization=current_org).select_related('author')[:4]
    sidebar_conversations = Conversation.objects.filter(organization=current_org, participants=request.user).prefetch_related('participants__profile')[:8]
    sidebar_projects = (
        Project.objects.filter(organization=current_org)
        .annotate(open_tasks=Count('tasks', filter=~Q(tasks__status__in=[Task.Status.COMPLETED, Task.Status.ARCHIVED])))
        .order_by('name')[:8]
    )
    return {
        'organizations': organizations,
        'current_organization': current_org,
        'memberships': memberships,
        'sidebar_announcements': sidebar_announcements,
        'sidebar_conversations': sidebar_conversations,
        'sidebar_projects': sidebar_projects,
        'unread_notifications': unread_notifications,
        'recent_notifications': recent_notifications,
    }


@login_required
def dashboard(request):
    AccountProfile.objects.get_or_create(user=request.user)
    current_org = get_current_organization(user=request.user, slug=request.GET.get('workspace'))
    projects = (
        Project.objects.filter(organization=current_org)
        .select_related('owner', 'team')
        .prefetch_related(Prefetch('project_memberships', queryset=ProjectMembership.objects.select_related('user')))
        .order_by('name')
    )
    notes = Note.objects.filter(organization=current_org, author=request.user).select_related('project').prefetch_related('tags').order_by('-is_pinned', '-updated_at')[:20]
    selected_note = notes.first()
    activity_logs = ActivityLog.objects.filter(organization=current_org).select_related('actor', 'task', 'project')[:8]
    announcements = Announcement.objects.filter(organization=current_org).select_related('author')[:5]
    memberships = current_org.memberships.select_related('user', 'user__profile').all()
    pending_invitations = OrganizationInvitation.objects.filter(organization=current_org, accepted_at__isnull=True, expires_at__gt=timezone.now()).select_related('invited_by')[:6]
    due_tasks = Task.objects.filter(project__organization=current_org).select_related('project', 'assignee').exclude(due_date__isnull=True).order_by('due_date')[:6]
    critical_alerts = FinanceAlert.objects.filter(organization=current_org, status=FinanceAlert.Status.OPEN, severity=FinanceAlert.Severity.CRITICAL).select_related('project')[:5]
    active_members = memberships.order_by('-user__profile__last_seen_at')[:6]
    workspace_metrics = {
        'project_total': projects.count(),
        'project_active': projects.filter(status=Project.Status.ACTIVE).count(),
        'task_open': Task.objects.filter(project__organization=current_org).exclude(status__in=[Task.Status.COMPLETED, Task.Status.ARCHIVED]).count(),
        'member_active': memberships.exclude(user__profile__presence_status='offline').count(),
        'pending_requests': pending_invitations.count(),
        'critical_alerts': critical_alerts.count(),
    }
    context = {
        **get_workspace_shell_context(request=request, current_org=current_org),
        'projects': projects[:8],
        'active_projects': projects.filter(status=Project.Status.ACTIVE)[:6],
        'notes': notes,
        'selected_note': selected_note,
        'activity_logs': activity_logs,
        'announcements': announcements,
        'active_members': active_members,
        'pending_invitations': pending_invitations,
        'due_tasks': due_tasks,
        'critical_alerts': critical_alerts,
        'workspace_metrics': workspace_metrics,
        'available_projects': projects[:20],
        'available_tags': Tag.objects.filter(organization=current_org).order_by('name'),
    }
    return render(request, 'collab/dashboard_main.html', context)


@login_required
def notifications_page(request):
    current_org = get_current_organization(user=request.user, slug=request.GET.get('workspace'))
    notifications = Notification.objects.filter(recipient=request.user, organization=current_org).select_related('actor', 'task', 'comment')
    paginator = Paginator(notifications, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        **get_workspace_shell_context(request=request, current_org=current_org),
        'notifications_page_obj': page_obj,
    }
    return render(request, 'collab/notifications.html', context)


@login_required
def tasks_page(request):
    current_org = get_current_organization(user=request.user, slug=request.GET.get('workspace'))
    tasks = (
        Task.objects.filter(organization=current_org)
        .select_related('project', 'assignee', 'creator', 'assignee__profile', 'creator__profile')
        .prefetch_related('tags', 'subtasks__children', 'subtasks__assignee__profile')
        .annotate(comments_count=Count('comments'), attachments_count=Count('attachments'))
        .order_by('sort_order', '-updated_at')
    )
    status_columns = []
    for status, label in Task.Status.choices:
        status_columns.append({'value': status, 'label': label, 'items': [task for task in tasks if task.status == status]})
    task_stats = {
        'total': tasks.count(),
        'completed': tasks.filter(status=Task.Status.COMPLETED).count(),
        'in_progress': tasks.filter(status=Task.Status.IN_PROGRESS).count(),
        'due_soon': tasks.exclude(due_date__isnull=True).count(),
    }
    context = {
        **get_workspace_shell_context(request=request, current_org=current_org),
        'tasks': tasks[:50],
        'all_tasks': tasks,
        'status_columns': status_columns,
        'task_stats': task_stats,
        'projects': Project.objects.filter(organization=current_org).order_by('name'),
        'task_statuses': Task.Status.choices,
        'task_priorities': Task.Priority.choices,
        'available_tags': Tag.objects.filter(organization=current_org).order_by('name'),
    }
    return render(request, 'collab/tasks_page.html', context)


@login_required
def finance_page(request):
    current_org = get_current_organization(user=request.user, slug=request.GET.get('workspace'))
    alerts = FinanceAlert.objects.filter(organization=current_org).select_related('project', 'created_by').order_by('status', '-created_at')
    finance_totals = {
        'open_total': sum(alert.amount for alert in alerts.filter(status=FinanceAlert.Status.OPEN)),
        'critical_count': alerts.filter(severity=FinanceAlert.Severity.CRITICAL).count(),
        'resolved_count': alerts.filter(status=FinanceAlert.Status.RESOLVED).count(),
    }
    context = {
        **get_workspace_shell_context(request=request, current_org=current_org),
        'finance_alerts': alerts,
        'finance_totals': finance_totals,
        'projects': Project.objects.filter(organization=current_org).order_by('name'),
    }
    return render(request, 'collab/finance_page.html', context)


@login_required
def customers_page(request):
    current_org = get_current_organization(user=request.user, slug=request.GET.get('workspace'))
    customers = Customer.objects.filter(organization=current_org).select_related('owner').order_by('name')
    paginator = Paginator(customers, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        **get_workspace_shell_context(request=request, current_org=current_org),
        'customers_page_obj': page_obj,
    }
    return render(request, 'collab/customers_page.html', context)


@login_required
def project_detail_page(request, pk: int):
    current_org = get_current_organization(user=request.user, slug=request.GET.get('workspace'))
    project = get_object_or_404(
        Project.objects.filter(organization=current_org)
        .select_related('owner', 'team')
        .prefetch_related(Prefetch('project_memberships', queryset=ProjectMembership.objects.select_related('user', 'user__profile'))),
        pk=pk,
    )
    project_tasks = Task.objects.filter(project=project).select_related('assignee', 'creator').prefetch_related('subtasks__children', 'subtasks__assignee__profile', 'tags')
    calendar_events = CalendarEvent.objects.filter(project=project).select_related('created_by').prefetch_related('attendees__profile')
    project_notes = Note.objects.filter(project=project).select_related('author').prefetch_related('tags').order_by('-is_pinned', '-updated_at')
    project_task_columns = [
        {'value': status, 'label': label, 'items': [task for task in project_tasks if task.status == status]}
        for status, label in Task.Status.choices
    ]
    project_stats = {
        'task_total': project_tasks.count(),
        'task_completed': project_tasks.filter(status=Task.Status.COMPLETED).count(),
        'task_in_progress': project_tasks.filter(status=Task.Status.IN_PROGRESS).count(),
        'meeting_total': calendar_events.count(),
        'member_total': project.project_memberships.count(),
        'documentation_total': project_notes.filter(note_type=Note.NoteType.DOCUMENTATION).count(),
    }
    context = {
        **get_workspace_shell_context(request=request, current_org=current_org),
        'project': project,
        'project_tasks': project_tasks,
        'project_task_columns': project_task_columns,
        'calendar_events': calendar_events,
        'project_stats': project_stats,
        'plan_notes': project_notes.filter(note_type=Note.NoteType.PLAN),
        'documentation_notes': project_notes.filter(note_type=Note.NoteType.DOCUMENTATION),
        'general_notes': project_notes.filter(note_type=Note.NoteType.NOTE),
        'available_tags': Tag.objects.filter(organization=current_org).order_by('name'),
    }
    return render(request, 'collab/project_detail_page.html', context)
