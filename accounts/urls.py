from django.urls import path

from .views import login_page, logout_page, register_page, settings_page


urlpatterns = [
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('logout/', logout_page, name='logout'),
    path('settings/', settings_page, name='settings'),
]
