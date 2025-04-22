from django.urls import path
from . import views

urlpatterns = [
    # Citizen URLs
    path('search/', views.search_challan, name='search_challan'),
    path('my-challans/', views.my_challans, name='my_challans'),
    path('view/<str:challan_number>/', views.view_challan, name='view_challan'),
    path('pay/<str:challan_number>/', views.pay_challan, name='pay_challan'),
    path('payment-success/<str:challan_number>/', views.challan_payment_success, name='challan_payment_success'),
    path('dispute/<str:challan_number>/', views.dispute_challan, name='dispute_challan'),
    
    # Officer URLs
    path('generate/', views.generate_challan, name='generate_challan'),
    path('manage/', views.manage_challans, name='manage_challans'),
    path('update/<str:challan_number>/', views.update_challan, name='update_challan'),
    path('record-payment/<str:challan_number>/', views.record_offline_payment, name='record_offline_payment'),
    
    # Admin URLs
    path('rules/', views.traffic_rules, name='traffic_rules'),
    path('rule/add/', views.add_traffic_rule, name='add_traffic_rule'),
    path('rule/<int:rule_id>/edit/', views.edit_traffic_rule, name='edit_traffic_rule'),
    path('types/', views.challan_types, name='challan_types'),
    path('type/add/', views.add_challan_type, name='add_challan_type'),
    path('type/<int:type_id>/edit/', views.edit_challan_type, name='edit_challan_type'),
    
    # Statistics
    path('statistics/', views.challan_statistics, name='challan_statistics'),
]
