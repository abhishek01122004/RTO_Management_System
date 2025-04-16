from django.contrib import admin
from .models import (VehicleCategory, VehicleRegistration, VehicleInspection, 
                    RegisteredVehicle, VehicleTransfer)


@admin.register(VehicleCategory)
class VehicleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_fee')
    search_fields = ('name',)


@admin.register(VehicleRegistration)
class VehicleRegistrationAdmin(admin.ModelAdmin):
    list_display = ('temporary_number', 'registration_number', 'owner', 'make', 'model', 
                   'registration_type', 'status', 'application_date')
    list_filter = ('status', 'registration_type', 'vehicle_category', 'application_date')
    search_fields = ('temporary_number', 'registration_number', 'owner__email', 
                     'chassis_number', 'engine_number', 'make', 'model')
    date_hierarchy = 'application_date'
    readonly_fields = ('temporary_number', 'application_date', 'created_at', 'updated_at')


@admin.register(VehicleInspection)
class VehicleInspectionAdmin(admin.ModelAdmin):
    list_display = ('registration', 'scheduled_date', 'venue', 'is_completed', 'passed')
    list_filter = ('is_completed', 'passed', 'scheduled_date')
    search_fields = ('registration__temporary_number', 'registration__registration_number')
    date_hierarchy = 'scheduled_date'


@admin.register(RegisteredVehicle)
class RegisteredVehicleAdmin(admin.ModelAdmin):
    list_display = ('registration', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('registration__registration_number', 'registration__owner__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VehicleTransfer)
class VehicleTransferAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'current_owner', 'new_owner', 
                   'sale_date', 'status', 'application_date')
    list_filter = ('status', 'application_date')
    search_fields = ('vehicle__registration__registration_number', 
                    'current_owner__email', 'new_owner__email')
    date_hierarchy = 'application_date'
    readonly_fields = ('application_date',)
