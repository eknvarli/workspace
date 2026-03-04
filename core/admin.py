from django.contrib import admin
from core.models import *

# Register your models here.

admin.site.register(Note)
admin.site.register(Tag)
admin.site.register(Project)
admin.site.register(UserPresence)
admin.site.register(Customer)
admin.site.register(CustomerQuote)