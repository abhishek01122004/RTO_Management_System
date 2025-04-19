from django.urls import path
from . import views

urlpatterns = [
    # Citizen URLs
    path('dashboard/', views.vehicle_dashboard, name='vehicle_dashboard'),
    path('register/', views.apply_for_registration, name='register_vehicle'),  # Fixed URL name for template compatibility
    path('register/', views.apply_for_registration, name='apply_for_registration'),  # Keep original name for backward compatibility
    path('application/<str:application_number>/', views.registration_application_detail, name='registration_application_detail'),
    path('applications/', views.my_registration_applications, name='my_registration_applications'),
    path('my-vehicles/', views.my_vehicles, name='my_vehicles'),
    path('vehicle/<str:registration_number>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicle/<str:registration_number>/transfer/', views.transfer_vehicle, name='transfer_vehicle'),
    path('transfers/', views.vehicle_transfers, name='vehicle_transfers'),
    
    # Officer URLs
    path('applications/review/', views.review_registration_applications, name='review_registration_applications'),
    path('application/<str:application_number>/review/', views.review_registration_application, name='review_registration_application'),
    path('application/<str:application_number>/inspection/', views.schedule_inspection, name='schedule_inspection'),
    path('application/<str:application_number>/inspection/result/', views.record_inspection_result, name='record_inspection_result'),
    path('application/<str:application_number>/issue/', views.issue_registration, name='issue_registration'),
    path('transfers/review/', views.review_transfer_applications, name='review_transfer_applications'),
    path('transfer/<int:transfer_id>/review/', views.review_transfer, name='review_transfer'),
    
    # Admin URLs
    path('classes/', views.vehicle_classes, name='vehicle_classes'),
    path('class/add/', views.add_vehicle_class, name='add_vehicle_class'),
    path('class/<int:class_id>/edit/', views.edit_vehicle_class, name='edit_vehicle_class'),
    path('makers/', views.vehicle_makers, name='vehicle_makers'),
    path('maker/add/', views.add_vehicle_maker, name='add_vehicle_maker'),
    path('maker/<int:maker_id>/edit/', views.edit_vehicle_maker, name='edit_vehicle_maker'),
    path('models/', views.vehicle_models, name='vehicle_models'),
    path('model/add/', views.add_vehicle_model, name='add_vehicle_model'),
    path('model/<int:model_id>/edit/', views.edit_vehicle_model, name='edit_vehicle_model'),
    
    # Statistics
    path('statistics/', views.vehicle_statistics, name='vehicle_statistics'),
]