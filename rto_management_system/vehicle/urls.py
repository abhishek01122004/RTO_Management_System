from django.urls import path
from . import views

urlpatterns = [
    # Citizen URLs
    path('register/', views.register_vehicle, name='register_vehicle'),
    path('registrations/', views.my_vehicle_registrations, name='my_vehicle_registrations'),
    path('registration/<str:reg_number>/', views.vehicle_registration_detail, name='vehicle_registration_detail'),
    path('vehicles/', views.my_vehicles, name='my_vehicles'),
    path('vehicle/<str:reg_number>/', views.vehicle_detail, name='vehicle_detail'),
    path('registration/<str:reg_number>/payment/', views.vehicle_registration_payment, name='vehicle_registration_payment'),
    path('registration/<str:reg_number>/payment/success/', views.vehicle_registration_payment_success, name='vehicle_registration_payment_success'),
    path('transfer/initiate/<str:reg_number>/', views.initiate_vehicle_transfer, name='initiate_vehicle_transfer'),
    path('transfers/', views.my_vehicle_transfers, name='my_vehicle_transfers'),
    
    # Officer URLs
    path('registrations/review/', views.review_vehicle_registrations, name='review_vehicle_registrations'),
    path('registration/<str:reg_number>/review/', views.review_vehicle_registration, name='review_vehicle_registration'),
    path('registration/<str:reg_number>/schedule-inspection/', views.schedule_inspection, name='schedule_inspection'),
    path('inspection/<int:inspection_id>/result/', views.record_inspection_result, name='record_inspection_result'),
    path('registration/<str:reg_number>/assign-number/', views.assign_registration_number, name='assign_registration_number'),
    path('transfers/review/', views.review_vehicle_transfers, name='review_vehicle_transfers'),
    path('transfer/<int:transfer_id>/review/', views.review_vehicle_transfer, name='review_vehicle_transfer'),
    
    # Admin URLs
    path('categories/', views.vehicle_categories, name='vehicle_categories'),
    path('category/add/', views.add_vehicle_category, name='add_vehicle_category'),
    path('category/<int:category_id>/edit/', views.edit_vehicle_category, name='edit_vehicle_category'),
    
    # Statistics
    path('statistics/', views.vehicle_statistics, name='vehicle_statistics'),
]
