from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='blue-500')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags')
    
    def __str__(self):
        return self.name

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
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-updated_at']
