from django.contrib import admin
from .models import TrafficRule, ChallanType, Challan, ChallanPayment


@admin.register(TrafficRule)
class TrafficRuleAdmin(admin.ModelAdmin):
    list_display = ('rule_code', 'description', 'penalty_amount')
    search_fields = ('rule_code', 'description')
    list_filter = ('is_active',)


@admin.register(ChallanType)
class ChallanTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'default_penalty')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)


@admin.register(Challan)
class ChallanAdmin(admin.ModelAdmin):
    list_display = ('challan_number', 'violator', 'vehicle_number', 'status',
                   'issue_date', 'total_amount', 'payment_status')
    list_filter = ('status', 'payment_status', 'issue_date')
    search_fields = ('challan_number', 'vehicle_number', 'violator__email', 
                    'violator__first_name', 'violator__last_name')
    date_hierarchy = 'issue_date'
    readonly_fields = ('challan_number', 'issue_date', 'created_at')


@admin.register(ChallanPayment)
class ChallanPaymentAdmin(admin.ModelAdmin):
    list_display = ('challan', 'amount', 'payment_date', 'payment_method', 'transaction_id')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('challan__challan_number', 'transaction_id')
    date_hierarchy = 'payment_date'
    readonly_fields = ('created_at',)
