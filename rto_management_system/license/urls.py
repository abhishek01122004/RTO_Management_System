from django.urls import path
from . import views

urlpatterns = [
    # Citizen URLs
    path('apply/', views.apply_for_license, name='apply_for_license'),
    path('application/<str:application_number>/', views.license_application_detail, name='license_application_detail'),
    path('applications/', views.my_license_applications, name='my_license_applications'),
    path('licenses/', views.my_licenses, name='my_licenses'),
    path('license/<str:license_number>/', views.license_detail, name='license_detail'),
    path('application/<str:application_number>/payment/', views.license_payment, name='license_payment'),
    path('application/<str:application_number>/payment/success/', views.license_payment_success, name='license_payment_success'),
    
    # Officer URLs
    path('applications/review/', views.review_license_applications, name='review_license_applications'),
    path('application/<str:application_number>/review/', views.review_license_application, name='review_license_application'),
    path('application/<str:application_number>/schedule-test/', views.schedule_test, name='schedule_test'),
    path('test/<int:test_id>/result/', views.record_test_result, name='record_test_result'),
    path('application/<str:application_number>/issue-license/', views.issue_license, name='issue_license'),
    
    # Admin URLs
    path('types/', views.license_types, name='license_types'),
    path('type/add/', views.add_license_type, name='add_license_type'),
    path('type/<int:type_id>/edit/', views.edit_license_type, name='edit_license_type'),
    
    # Statistics
    path('statistics/', views.license_statistics, name='license_statistics'),
]
