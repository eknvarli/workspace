from django.urls import path
from core.views import *

urlpatterns = [
    # Notes paths
    path('', note_index, name='index'),
    path('note/<int:pk>/', note_index, name='note_detail'),
    path('note/new/', note_create, name='note_create'),
    path('note/<int:pk>/save/', note_save, name='note_save'),
    path('note/<int:pk>/delete/', note_delete, name='note_delete'),
    
    # Auth paths
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('logout/', user_logout, name='logout'),
]