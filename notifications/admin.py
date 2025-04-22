from django.contrib import admin
from .models import Notification, EmailLog, SMSLog

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    date_hierarchy = 'created_at'


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('to_email', 'subject', 'status', 'sent_at')
    list_filter = ('status', 'sent_at')
    search_fields = ('to_email', 'subject', 'message')
    date_hierarchy = 'sent_at'


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('to_number', 'status', 'sent_at')
    list_filter = ('status', 'sent_at')
    search_fields = ('to_number', 'message')
    date_hierarchy = 'sent_at'
