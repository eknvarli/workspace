from __future__ import annotations

from django.conf import settings
from django.db import models


class CalendarEvent(models.Model):
    class EventType(models.TextChoices):
        APPOINTMENT = 'appointment', 'Appointment'
        MEETING = 'meeting', 'Meeting'
        DEADLINE = 'deadline', 'Deadline'
        REMINDER = 'reminder', 'Reminder'

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='calendar_events')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, blank=True, null=True, related_name='calendar_events')
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EventType.choices, default=EventType.MEETING)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    location = models.CharField(max_length=180, blank=True)
    meeting_url = models.URLField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calendar_events_created')
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='calendar_events')
    attendee_roles = models.JSONField(default=list, blank=True)
    reminder_minutes_before = models.PositiveIntegerField(default=30)
    reminders_sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_at', 'title']
        indexes = [models.Index(fields=['organization', 'start_at']), models.Index(fields=['event_type'])]

    def __str__(self) -> str:
        return self.title