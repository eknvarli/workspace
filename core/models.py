from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='blue-500')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags')
    
    def __str__(self):
        return self.name


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=120)
    color = models.CharField(max_length=20, default='blue-500')
    representative = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='represented_projects'
    )
    participants = models.ManyToManyField(User, blank=True, related_name='project_participations')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-updated_at']


class UserPresence(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='presence')
    last_active_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.last_active_at}"

    class Meta:
        verbose_name = 'User Presence'
        verbose_name_plural = 'User Presences'


class UserSettings(models.Model):
    THEME_CHOICES = [
        ('dark', 'Koyu Tema'),
        ('light', 'Açık Tema'),
        ('system', 'Sistem Teması'),
    ]

    LANGUAGE_CHOICES = [
        ('tr', 'Türkçe'),
        ('en', 'English'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings_profile')
    auto_save = models.BooleanField(default=False)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='dark')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='tr')
    profile_photo = models.FileField(upload_to='profiles/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} settings"

    class Meta:
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'

class Note(models.Model):
    CATEGORY_CHOICES = [
        ('note', 'Tüm Notlar'),
        ('project', 'Projeler'),
        ('task', 'Görevler'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255, default='Yeni Not')
    content = models.TextField(blank=True, null=True)
    is_favorite = models.BooleanField(default=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='note')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='notes')
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_notes')
    assigned_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    parent_note = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_tasks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-updated_at']
