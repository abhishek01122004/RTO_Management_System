from django.urls import path
from . import views

app_name = 'vehicle'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.vehicle_dashboard, name='vehicle_dashboard'),
    
    # Vehicle Registration
    path('register/', views.register_vehicle, name='register_vehicle'),
    path('application/<int:application_id>/', views.vehicle_application_detail, name='vehicle_application_detail'),
    path('application/<int:application_id>/submit/', views.submit_application, name='submit_application'),
    path('application/<int:application_id>/review/', views.review_application, name='review_application'),
    path('applications/review/', views.review_registration_applications, name='review_registration_applications'),
    
    # Vehicle Management
    path('my/', views.my_vehicles, name='my_vehicles'),
    path('detail/<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    path('transfer/<int:vehicle_id>/', views.transfer_vehicle, name='transfer_vehicle'),
    path('transfer/<int:transfer_id>/review/', views.review_transfer, name='review_transfer'),
    path('transfers/', views.vehicle_transfers, name='vehicle_transfers'),
    path('get-models/', views.get_models, name='get_models'),
    
    # Statistics
    path('statistics/', views.vehicle_statistics, name='vehicle_statistics'),
    
    # Vehicle Categories
    path('classes/', views.vehicle_classes, name='vehicle_classes'),
    path('makes/', views.vehicle_makes, name='vehicle_makes'),
    path('models/', views.vehicle_models, name='vehicle_models'),
] 