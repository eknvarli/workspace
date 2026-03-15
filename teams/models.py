from __future__ import annotations

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify


class Team(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='#6366F1')
    lead = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='leading_teams')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='TeamMembership', related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('organization', 'slug')
        indexes = [models.Index(fields=['organization', 'name'])]
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)[:160] or 'team'
            slug = base_slug
            counter = 1
            while Team.objects.exclude(pk=self.pk).filter(organization=self.organization, slug=slug).exists():
                counter += 1
                slug = f'{base_slug}-{counter}'
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class TeamMembership(models.Model):
    class Role(models.TextChoices):
        LEAD = 'lead', 'Lead'
        MEMBER = 'member', 'Member'

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'user')
        ordering = ['team__name', 'user__username']

    def __str__(self) -> str:
        return f'{self.user} in {self.team}'
