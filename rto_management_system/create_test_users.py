"""
Script to create test users for the RTO Management System
"""
import os
import django
import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rto_management_system.settings')
django.setup()

from django.utils import timezone
from accounts.models import User, CitizenProfile, OfficerProfile


def create_test_users():
    """Create test users with different roles"""
    print("Creating test users...")
    
    # Create Citizen User
    citizen_user, created = User.objects.get_or_create(
        email='citizen@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Citizen',
            'phone_number': '9876543210',
            'address': '123 Citizen Street, Test City',
            'user_type': 'CITIZEN',
            'aadhaar_number': '123456789012',
        }
    )
    
    if created:
        citizen_user.set_password('citizen123')
        citizen_user.save()
        print(f"Created citizen user: {citizen_user.email}")
        
        # Create citizen profile
        citizen_profile, _ = CitizenProfile.objects.get_or_create(
            user=citizen_user,
            defaults={
                'date_of_birth': datetime.date(1990, 1, 1),
                'blood_group': 'O+',
                'emergency_contact': '9876543211',
            }
        )
        print(f"Created citizen profile for: {citizen_user.email}")
    else:
        print(f"Citizen user already exists: {citizen_user.email}")
    
    # Create Officer User
    officer_user, created = User.objects.get_or_create(
        email='officer@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Officer',
            'phone_number': '8765432109',
            'address': '456 Officer Avenue, Test City',
            'user_type': 'OFFICER',
        }
    )
    
    if created:
        officer_user.set_password('officer123')
        officer_user.save()
        print(f"Created officer user: {officer_user.email}")
        
        # Create officer profile
        officer_profile, _ = OfficerProfile.objects.get_or_create(
            user=officer_user,
            defaults={
                'employee_id': 'OFF-12345',
                'designation': 'RTO Inspector',
                'department': 'Licenses Division',
                'joining_date': timezone.now().date(),
            }
        )
        print(f"Created officer profile for: {officer_user.email}")
    else:
        print(f"Officer user already exists: {officer_user.email}")
    
    # Create Admin User
    admin_user, created = User.objects.get_or_create(
        email='admin@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Admin',
            'phone_number': '7654321098',
            'address': '789 Admin Road, Test City',
            'user_type': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"Created admin user: {admin_user.email}")
    else:
        print(f"Admin user already exists: {admin_user.email}")
    
    print("Test users creation completed.")


if __name__ == '__main__':
    create_test_users()