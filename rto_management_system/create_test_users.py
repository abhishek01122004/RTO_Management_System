import os
import django
import datetime

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rto_management_system.settings')
django.setup()

from django.utils import timezone
from accounts.models import User, CitizenProfile, OfficerProfile


def create_test_users():
    """Create test users with different roles"""
    
    # Create admin user
    admin_user, admin_created = User.objects.get_or_create(
        email='admin@test.com',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'user_type': 'ADMIN',
            'phone_number': '+1234567890',
            'address': '123 Admin Street, Admin City, 12345',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    
    if admin_created:
        admin_user.set_password('Admin@123')
        admin_user.save()
        print(f"Admin user created with email: {admin_user.email} and password: Admin@123")
    else:
        print(f"Admin user already exists with email: {admin_user.email}")
    
    # Create officer user
    officer_user, officer_created = User.objects.get_or_create(
        email='officer@test.com',
        defaults={
            'first_name': 'Officer',
            'last_name': 'User',
            'user_type': 'OFFICER',
            'phone_number': '+1987654321',
            'address': '456 Officer Street, Officer City, 67890',
        }
    )
    
    if officer_created:
        officer_user.set_password('Officer@123')
        officer_user.save()
        
        # Create officer profile
        OfficerProfile.objects.create(
            user=officer_user,
            employee_id='EMP001',
            designation='RTO Officer',
            department='License Department',
            joining_date=timezone.now().date()
        )
        
        print(f"Officer user created with email: {officer_user.email} and password: Officer@123")
    else:
        print(f"Officer user already exists with email: {officer_user.email}")
    
    # Create citizen user
    citizen_user, citizen_created = User.objects.get_or_create(
        email='citizen@test.com',
        defaults={
            'first_name': 'Citizen',
            'last_name': 'User',
            'user_type': 'CITIZEN',
            'phone_number': '+1122334455',
            'address': '789 Citizen Street, Citizen City, 10111',
            'aadhaar_number': '1234 5678 9012',
        }
    )
    
    if citizen_created:
        citizen_user.set_password('Citizen@123')
        citizen_user.save()
        
        # Create citizen profile
        CitizenProfile.objects.create(
            user=citizen_user,
            date_of_birth=datetime.date(1990, 1, 1),
            blood_group='O+',
            emergency_contact='+1567891234'
        )
        
        print(f"Citizen user created with email: {citizen_user.email} and password: Citizen@123")
    else:
        print(f"Citizen user already exists with email: {citizen_user.email}")
    
    return {
        'admin': {'email': 'admin@test.com', 'password': 'Admin@123'},
        'officer': {'email': 'officer@test.com', 'password': 'Officer@123'},
        'citizen': {'email': 'citizen@test.com', 'password': 'Citizen@123'}
    }


if __name__ == "__main__":
    create_test_users()