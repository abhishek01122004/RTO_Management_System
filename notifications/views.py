from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from django.contrib import messages
from .utils import send_email

@login_required
def get_unread_notifications(request):
    # Get notifications from the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    notifications = Notification.objects.filter(
        user=request.user,
        created_at__gte=thirty_days_ago
    ).order_by('-created_at')[:10]  # Limit to 10 most recent notifications
    
    notifications_data = []
    for notification in notifications:
        # Determine the appropriate link based on notification type
        link = '#'
        if notification.notification_type == 'LICENSE_APPLICATION':
            link = f'/license/my_license_applications/'
        elif notification.notification_type == 'VEHICLE_REGISTRATION':
            link = f'/vehicle/vehicle_dashboard/'
        elif notification.notification_type == 'CHALLAN_ISSUED':
            link = f'/challan/my_challans/'
        elif notification.notification_type == 'TEST_RESULT':
            link = f'/license/my_licenses/'
        elif notification.notification_type == 'LICENSE_ISSUED':
            link = f'/license/my_licenses/'
        elif notification.notification_type == 'VEHICLE_REGISTERED':
            link = f'/vehicle/my_vehicles/'
        elif notification.notification_type == 'CHALLAN_STATUS':
            link = f'/challan/my_challans/'
        
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'link': link,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_read': notification.is_read
        })
    
    return JsonResponse({
        'notifications': notifications_data
    })

@login_required
def test_email(request):
    """View to test email configuration"""
    if request.method == 'POST':
        try:
            sent = send_email(
                to_email=request.user.email,
                subject="Test Email from RTO Management System",
                message="This is a test email to verify the email configuration is working correctly.",
                html_message="<h1>Test Email</h1><p>This is a test email to verify the email configuration is working correctly.</p>"
            )
            if sent:
                messages.success(request, "Test email sent successfully!")
            else:
                messages.error(request, "Failed to send test email.")
        except Exception as e:
            messages.error(request, f"Error sending test email: {str(e)}")
    
    return render(request, 'notifications/test_email.html')

@login_required
def notification_list(request):
    """View to display all notifications for the user"""
    # Get notifications from the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    notifications = Notification.objects.filter(
        user=request.user,
        created_at__gte=thirty_days_ago
    ).order_by('-created_at')
    
    # Mark notifications as read
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
    
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications
    }) 