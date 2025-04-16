from django.db import models
from accounts.models import User


class Notification(models.Model):
    """Model for in-app notifications"""
    NOTIFICATION_TYPES = (
        ('LICENSE_APPLICATION', 'License Application'),
        ('VEHICLE_REGISTRATION', 'Vehicle Registration'),
        ('CHALLAN_ISSUED', 'Challan Issued'),
        ('APPLICATION_STATUS', 'Application Status'),
        ('TEST_SCHEDULE', 'Test Schedule'),
        ('TEST_RESULT', 'Test Result'),
        ('INSPECTION_SCHEDULE', 'Inspection Schedule'),
        ('INSPECTION_RESULT', 'Inspection Result'),
        ('PAYMENT', 'Payment'),
        ('LICENSE_ISSUED', 'License Issued'),
        ('VEHICLE_REGISTERED', 'Vehicle Registered'),
        ('VEHICLE_TRANSFER', 'Vehicle Transfer'),
        ('TRANSFER_STATUS', 'Transfer Status'),
        ('CHALLAN_DISPUTE', 'Challan Dispute'),
        ('CHALLAN_STATUS', 'Challan Status'),
        ('GENERAL', 'General'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='GENERAL')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} for {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']


class EmailLog(models.Model):
    """Model for logging emails sent"""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    )
    
    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Email to {self.to_email}: {self.subject}"


class SMSLog(models.Model):
    """Model for logging SMS messages sent"""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    )
    
    to_number = models.CharField(max_length=15)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"SMS to {self.to_number}: {self.message[:30]}..."
