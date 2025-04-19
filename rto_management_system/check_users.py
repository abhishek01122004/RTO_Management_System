"""
Script to check users in the RTO Management System
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rto_management_system.settings')
django.setup()

from accounts.models import User, CitizenProfile, OfficerProfile

def check_users():
    """List all users in the system with details"""
    print("\nUsers in the system:")
    print("====================")
    
    for user in User.objects.all():
        print(f"Email: {user.email}")
        print(f"Name: {user.first_name} {user.last_name}")
        print(f"User Type: {user.user_type}")
        print(f"Phone: {user.phone_number}")
        print("-------------------------------------------")
    
    print("\nCitizen profiles:")
    print("================")
    for profile in CitizenProfile.objects.all():
        print(f"User: {profile.user.email}")
        print(f"DOB: {profile.date_of_birth}")
        print(f"Blood Group: {profile.blood_group}")
        print("-------------------------------------------")
    
    print("\nOfficer profiles:")
    print("================")
    for profile in OfficerProfile.objects.all():
        print(f"User: {profile.user.email}")
        print(f"Employee ID: {profile.employee_id}")
        print(f"Designation: {profile.designation}")
        print(f"Department: {profile.department}")
        print("-------------------------------------------")

if __name__ == '__main__':
    check_users()