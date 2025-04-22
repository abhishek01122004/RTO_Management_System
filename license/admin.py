from django.contrib import admin
from .models import LicenseType, LicenseApplication, DrivingLicense, TestSchedule


@admin.register(LicenseType)
class LicenseTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'age_requirement', 'validity_years', 'fee')
    search_fields = ('name', 'code')


@admin.register(LicenseApplication)
class LicenseApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_number', 'applicant', 'license_type', 'application_type', 
                   'status', 'application_date', 'payment_status')
    list_filter = ('status', 'application_type', 'payment_status', 'application_date')
    search_fields = ('application_number', 'applicant__email', 'applicant__first_name', 
                    'applicant__last_name')
    date_hierarchy = 'application_date'
    readonly_fields = ('application_number', 'application_date', 'created_at', 'updated_at')


@admin.register(DrivingLicense)
class DrivingLicenseAdmin(admin.ModelAdmin):
    list_display = ('license_number', 'holder', 'license_type', 'issued_date', 'valid_until', 'is_active')
    list_filter = ('is_active', 'license_type', 'issued_date')
    search_fields = ('license_number', 'holder__email', 'holder__first_name', 'holder__last_name')
    date_hierarchy = 'issued_date'
    readonly_fields = ('license_number', 'created_at', 'updated_at')


@admin.register(TestSchedule)
class TestScheduleAdmin(admin.ModelAdmin):
    list_display = ('application', 'test_type', 'scheduled_date', 'venue', 'is_completed', 'passed')
    list_filter = ('test_type', 'is_completed', 'passed', 'scheduled_date')
    search_fields = ('application__application_number', 'application__applicant__email')
    date_hierarchy = 'scheduled_date'
