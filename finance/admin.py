from django.contrib import admin

from .models import FinanceAlert


@admin.register(FinanceAlert)
class FinanceAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'status', 'severity', 'amount', 'currency')
    list_filter = ('organization', 'status', 'severity')
    search_fields = ('title', 'notes')