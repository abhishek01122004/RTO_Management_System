from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('license/', views.license_service, name='license_service'),
    path('vehicle/', views.vehicle_service, name='vehicle_service'),
    path('challan/', views.challan_service, name='challan_service'),
] 