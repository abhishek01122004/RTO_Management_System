from django.contrib import admin
from .models import (VehicleClass, VehicleMaker, VehicleModel, 
                   RegistrationApplication, VehicleRegistration, VehicleTransfer)


@admin.register(VehicleClass)
class VehicleClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'fee', 'validity_years', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('is_active',)


@admin.register(VehicleMaker)
class VehicleMakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'is_active')
    search_fields = ('name', 'country')
    list_filter = ('is_active',)


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'maker', 'vehicle_type', 'fuel_type', 'year_of_manufacture', 'is_active')
    search_fields = ('name', 'maker__name')
    list_filter = ('vehicle_type', 'fuel_type', 'is_active', 'maker')


@admin.register(RegistrationApplication)
class RegistrationApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_number', 'applicant', 'application_type', 'status', 
                   'vehicle_maker', 'vehicle_model', 'application_date')
    search_fields = ('application_number', 'applicant__email', 'engine_number', 'chassis_number')
    list_filter = ('status', 'application_type', 'payment_status', 'application_date')
    date_hierarchy = 'application_date'
    readonly_fields = ('application_number', 'application_date', 'created_at', 'updated_at')
    fieldsets = (
        ('Application Details', {
            'fields': ('application_number', 'applicant', 'application_type', 'status', 'remarks')
        }),
        ('Vehicle Details', {
            'fields': ('vehicle_class', 'vehicle_maker', 'vehicle_model', 'engine_number', 
                      'chassis_number', 'color', 'purchase_date', 'dealer_name', 'temporary_registration')
        }),
        ('Insurance & Emission', {
            'fields': ('insurance_provider', 'insurance_number', 'insurance_validity',
                      'emission_test_number', 'emission_test_validity')
        }),
        ('Documents', {
            'fields': ('invoice_copy', 'insurance_copy', 'emission_certificate', 
                      'owner_id_proof', 'owner_address_proof')
        }),
        ('Processing', {
            'fields': ('inspection_date', 'inspection_officer', 'inspection_remarks', 
                       'rejection_reason', 'reviewed_by')
        }),
        ('Payment', {
            'fields': ('fee', 'payment_status', 'payment_date', 'payment_transaction_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(VehicleRegistration)
class VehicleRegistrationAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'owner', 'registered_date', 'expiry_date', 'is_active')
    search_fields = ('registration_number', 'owner__email', 'application__engine_number', 'application__chassis_number')
    list_filter = ('is_active', 'registered_date')
    date_hierarchy = 'registered_date'
    readonly_fields = ('registration_number', 'registered_date', 'created_at', 'updated_at')
    fieldsets = (
        ('Registration Details', {
            'fields': ('registration_number', 'application', 'owner', 'registered_date', 'expiry_date', 'is_active')
        }),
        ('RC Card Details', {
            'fields': ('rc_card_number', 'rc_card_issued_date')
        }),
        ('Validity Details', {
            'fields': ('fitness_certificate_expiry', 'tax_paid_upto', 'emission_test_validity', 'insurance_validity')
        }),
        ('Inspection Details', {
            'fields': ('last_inspection_date', 'next_inspection_due')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(VehicleTransfer)
class VehicleTransferAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'current_owner', 'new_owner', 'status', 'sale_date', 'application_date')
    search_fields = ('vehicle__registration_number', 'current_owner__email', 'new_owner__email')
    list_filter = ('status', 'payment_status', 'application_date')
    date_hierarchy = 'application_date'
    fieldsets = (
        ('Transfer Details', {
            'fields': ('vehicle', 'current_owner', 'new_owner', 'status', 'remarks')
        }),
        ('Sale Details', {
            'fields': ('sale_date', 'sale_amount')
        }),
        ('Documents', {
            'fields': ('sale_agreement', 'seller_id_proof', 'buyer_id_proof', 
                      'seller_address_proof', 'buyer_address_proof')
        }),
        ('Payment', {
            'fields': ('transfer_fee', 'payment_status', 'payment_date', 'payment_transaction_id')
        }),
        ('Processing', {
            'fields': ('processed_by', 'processed_date')
        }),
    )