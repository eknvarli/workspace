from django.urls import path

from .views import customers_page, dashboard, finance_page, notifications_page, project_detail_page, tasks_page


urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('tasks/', tasks_page, name='tasks_page'),
    path('finance/', finance_page, name='finance_page'),
    path('customers/', customers_page, name='customers_page'),
    path('notifications/', notifications_page, name='notifications_page'),
    path('projects/<int:pk>/', project_detail_page, name='project_detail_page'),
]
