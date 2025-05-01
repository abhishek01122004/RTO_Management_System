from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_redirect, name='dashboard'),
    path('citizen/', views.citizen_dashboard, name='citizen_dashboard'),
    path('officer/', views.officer_dashboard, name='officer_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('officers/', views.manage_officers, name='manage_officers'),
    path('status/<str:application_type>/<str:application_number>/', views.check_application_status, name='check_application_status'),
    path('status/license/', views.track_license_status, name='track_license_status'),
    path('applications/review/', views.review_applications, name='review_applications'),
]
