from __future__ import annotations

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify


class Project(models.Model):
    class Visibility(models.TextChoices):
        PRIVATE = 'private', 'Private'
        TEAM = 'team', 'Team'
        WORKSPACE = 'workspace', 'Workspace'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ON_HOLD = 'on_hold', 'On Hold'
        COMPLETED = 'completed', 'Completed'
        ARCHIVED = 'archived', 'Archived'

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='projects')
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, blank=True, null=True, related_name='projects')
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='#3B82F6')
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.WORKSPACE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_projects')
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMembership',
        through_fields=('project', 'user'),
        related_name='collaboration_projects',
    )
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('organization', 'slug')
        indexes = [models.Index(fields=['organization', 'status']), models.Index(fields=['organization', 'visibility'])]
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)[:160] or 'project'
            slug = base_slug
            counter = 1
            while Project.objects.exclude(pk=self.pk).filter(organization=self.organization, slug=slug).exists():
                counter += 1
                slug = f'{base_slug}-{counter}'
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class ProjectMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        CONTRIBUTOR = 'contributor', 'Contributor'
        VIEWER = 'viewer', 'Viewer'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CONTRIBUTOR)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='project_members_added')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')
        indexes = [models.Index(fields=['project', 'role'])]
        ordering = ['project__name', 'user__username']

    def __str__(self) -> str:
        return f'{self.user} on {self.project}'
