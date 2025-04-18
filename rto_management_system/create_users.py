import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rto_management_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import OfficerProfile, CitizenProfile
from datetime import date, timedelta
import random

User = get_user_model()

def create_admin_user():
    """Create an admin user if it doesn't exist"""
    if not User.objects.filter(email='admin@rto.gov.in').exists():
        admin_user = User.objects.create_superuser(
            email='admin@rto.gov.in',
            password='Admin@123',
            first_name='Admin',
            last_name='User',
            phone_number='9876543210',
            user_type='ADMIN'
        )
        print(f"Created admin user: {admin_user.email}")
        return admin_user
    else:
        print("Admin user already exists")
        return User.objects.get(email='admin@rto.gov.in')

def create_officer_user():
    """Create an RTO officer user if it doesn't exist"""
    if not User.objects.filter(email='officer@rto.gov.in').exists():
        officer_user = User.objects.create_user(
            email='officer@rto.gov.in',
            password='Officer@123',
            first_name='Officer',
            last_name='User',
            phone_number='9876543211',
            user_type='OFFICER'
        )
        
        # Create officer profile
        OfficerProfile.objects.create(
            user=officer_user,
            employee_id='RTO-' + ''.join(random.choices('0123456789', k=6)),
            designation='Transport Officer',
            department='License & Registration',
            joining_date=date.today() - timedelta(days=random.randint(30, 365))
        )
        
        print(f"Created officer user: {officer_user.email}")
        return officer_user
    else:
        print("Officer user already exists")
        return User.objects.get(email='officer@rto.gov.in')

def create_citizen_user():
    """Create a sample citizen user if it doesn't exist"""
    if not User.objects.filter(email='citizen@example.com').exists():
        citizen_user = User.objects.create_user(
            email='citizen@example.com',
            password='Citizen@123',
            first_name='Sample',
            last_name='Citizen',
            phone_number='9876543212',
            aadhaar_number='123456789012',
            address='123 Main St, Example City, State - 123456',
            user_type='CITIZEN'
        )
        
        # Create citizen profile
        CitizenProfile.objects.create(
            user=citizen_user,
            date_of_birth=date.today() - timedelta(days=random.randint(7300, 14600)),  # 20-40 years old
            blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
            emergency_contact='9876543213'
        )
        
        print(f"Created citizen user: {citizen_user.email}")
        return citizen_user
    else:
        print("Citizen user already exists")
        return User.objects.get(email='citizen@example.com')

if __name__ == '__main__':
    print("Creating user accounts...")
    admin = create_admin_user()
    officer = create_officer_user()
    citizen = create_citizen_user()
    print("\nUser accounts created successfully!")
    print("\nLogin credentials:")
    print(f"Admin: {admin.email} / Admin@123")
    print(f"Officer: {officer.email} / Officer@123")
    print(f"Citizen: {citizen.email} / Citizen@123")