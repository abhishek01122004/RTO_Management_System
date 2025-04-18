"""
Temporary replacement for notifications.utils to fix import errors
This allows the license app to function while the proper notifications app is being set up
"""

import logging

logger = logging.getLogger(__name__)

def send_notification(user, title, message, notification_type='GENERAL'):
    """Send an in-app notification to a user"""
    logger.info(f"NOTIFICATION to {user.email}: {title} - {message}")
    print(f"NOTIFICATION to {user.email}: {title} - {message}")
    # In a real implementation, this would save to the database
    return True

def send_email(to_email, subject, message, html_message=None):
    """Send an email notification"""
    logger.info(f"EMAIL to {to_email}: {subject} - {message}")
    print(f"EMAIL to {to_email}: {subject} - {message}")
    # In a real implementation, this would use Django's send_mail
    return True

def send_sms(to_number, message):
    """Send an SMS notification"""
    logger.info(f"SMS to {to_number}: {message}")
    print(f"SMS to {to_number}: {message}")
    # In a real implementation, this would use a service like Twilio
    return True