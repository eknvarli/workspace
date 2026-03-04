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


class Customer(models.Model):
    STATUS_CHOICES = [
        ('lead', 'Potansiyel'),
        ('active', 'Aktif'),
        ('inactive', 'Pasif'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=200, blank=True)
    sector = models.CharField(max_length=120, blank=True)
    title = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    alternate_phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)
    address = models.TextField(blank=True)
    tax_office = models.CharField(max_length=120, blank=True)
    tax_number = models.CharField(max_length=50, blank=True)
    preferred_contact_channel = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lead')
    source = models.CharField(max_length=120, blank=True)
    budget_expectation = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.company_name:
            return f"{self.name} - {self.company_name}"
        return self.name

    class Meta:
        ordering = ['-updated_at']


class CustomerQuote(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('sent', 'Gönderildi'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
        ('revision', 'Revizyon Bekliyor'),
    ]

    CURRENCY_CHOICES = [
        ('TRY', 'TRY'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_quotes')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='quotes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    reference_code = models.CharField(max_length=80, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='TRY')
    quote_date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.name} - {self.title}"

    class Meta:
        ordering = ['-quote_date', '-updated_at']


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
