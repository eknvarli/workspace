from django.urls import path
from core.views import *

urlpatterns = [
    # Notes paths
    path('', note_index, name='index'),
    path('projects/', project_index, name='projects'),
    path('tasks/', task_index, name='tasks'),
    path('projects/<int:pk>/', project_detail, name='project_detail'),
    path('users/<int:pk>/summary/', user_summary, name='user_summary'),
    path('note/<int:pk>/', note_index, name='note_detail'),
    path('note/new/', note_create, name='note_create'),
    path('note/<int:pk>/save/', note_save, name='note_save'),
    path('note/<int:pk>/favorite/', note_toggle_favorite, name='note_toggle_favorite'),
    path('note/<int:pk>/assign/', note_assign, name='note_assign'),
    path('note/<int:pk>/delete/', note_delete, name='note_delete'),
    path('tasks/<int:pk>/toggle-complete/', task_toggle_complete, name='task_toggle_complete'),
    path('projects/new/', project_create, name='project_create'),
    path('settings/', settings_page, name='settings'),
    
    # Auth paths
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('logout/', user_logout, name='logout'),
]