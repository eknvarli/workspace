from django.urls import path

from .views import dashboard, notifications_page


urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('notifications/', notifications_page, name='notifications_page'),
]
