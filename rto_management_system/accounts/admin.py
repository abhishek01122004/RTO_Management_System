from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, CitizenProfile, OfficerProfile


class UserAdmin(BaseUserAdmin):
    """Define admin model for custom User model."""
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'aadhaar_number', 'address')}),
        (_('User type'), {'fields': ('user_type',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


class CitizenProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'blood_group')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


class OfficerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'designation', 'department')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'employee_id')


admin.site.register(User, UserAdmin)
admin.site.register(CitizenProfile, CitizenProfileAdmin)
admin.site.register(OfficerProfile, OfficerProfileAdmin)
