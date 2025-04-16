from django.contrib import admin
from .models import DashboardStatistic

@admin.register(DashboardStatistic)
class DashboardStatisticAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
