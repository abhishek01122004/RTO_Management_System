from django.core.mail import send_mail
from django.conf import settings
import logging
from .models import Notification, EmailLog, SMSLog

logger = logging.getLogger(__name__)


def send_notification(user, title, message, notification_type='GENERAL'):
    """Send an in-app notification to a user"""
    try:
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type
        )
        return notification
    except Exception as e:
        logger.error(f"Failed to create notification: {str(e)}")
        return None


def send_email(to_email, subject, message, html_message=None):
    """Send an email and log it"""
    try:
        # Log the email first
        email_log = EmailLog.objects.create(
            to_email=to_email,
            subject=subject,
            message=message
        )
        
        # Send the email
        sent = send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False
        )
        
        # Update log status
        if sent:
            email_log.status = 'SENT'
        else:
            email_log.status = 'FAILED'
            email_log.error_message = "Email not sent (unknown error)"
        
        email_log.save()
        return sent
    
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        
        # Update log if it was created
        try:
            if 'email_log' in locals():
                email_log.status = 'FAILED'
                email_log.error_message = str(e)
                email_log.save()
        except Exception:
            pass
        
        return False


def send_sms(to_number, message):
    """
    Send an SMS and log it
    Note: This is a placeholder. In a real implementation, you would integrate with an SMS service.
    """
    try:
        # Log the SMS first
        sms_log = SMSLog.objects.create(
            to_number=to_number,
            message=message
        )
        
        # In a real implementation, you would call an SMS API service here
        # For now, we'll just log it as sent
        
        # Simulating successful SMS sending
        sms_sent = True
        
        # Update log status
        if sms_sent:
            sms_log.status = 'SENT'
        else:
            sms_log.status = 'FAILED'
            sms_log.error_message = "SMS not sent (unknown error)"
        
        sms_log.save()
        return sms_sent
    
    except Exception as e:
        logger.error(f"Failed to send SMS: {str(e)}")
        
        # Update log if it was created
        try:
            if 'sms_log' in locals():
                sms_log.status = 'FAILED'
                sms_log.error_message = str(e)
                sms_log.save()
        except Exception:
            pass
        
        return False
