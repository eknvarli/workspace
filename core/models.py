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
    tags = models.ManyToManyField(Tag, blank=True, related_name='notes')
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_notes')
    assigned_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-updated_at']
