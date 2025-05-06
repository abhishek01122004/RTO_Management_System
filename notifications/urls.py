from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('api/unread/', views.get_unread_notifications, name='api_unread_notifications'),
    path('', views.notification_list, name='notification_list'),
    path('test-email/', views.test_email, name='test_email'),
] 