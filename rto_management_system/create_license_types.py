import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rto_management_system.settings')
django.setup()

from license.models import LicenseType

def create_license_types():
    # Define common license types
    license_types = [
        {
            'name': 'Learner\'s License',
            'code': 'LL',
            'description': 'A temporary license issued to a person so that the person can practice driving under supervision.',
            'age_requirement': 18,
            'validity_years': 1,
            'fee': 200.00,
        },
        {
            'name': 'Non-Commercial Driving License (Two Wheeler)',
            'code': 'NCDL-2W',
            'description': 'License to drive two-wheelers like motorcycles and scooters for non-commercial purposes.',
            'age_requirement': 18,
            'validity_years': 20,
            'fee': 500.00,
        },
        {
            'name': 'Non-Commercial Driving License (Light Motor Vehicle)',
            'code': 'NCDL-LMV',
            'description': 'License to drive cars and other light motor vehicles for non-commercial purposes.',
            'age_requirement': 18,
            'validity_years': 20,
            'fee': 750.00,
        },
        {
            'name': 'Commercial Driving License (Light Motor Vehicle)',
            'code': 'CDL-LMV',
            'description': 'License to drive taxis, small commercial vehicles for business or commercial purposes.',
            'age_requirement': 20,
            'validity_years': 3,
            'fee': 1000.00,
        },
        {
            'name': 'Commercial Driving License (Heavy Motor Vehicle)',
            'code': 'CDL-HMV',
            'description': 'License to drive trucks, buses and other heavy motor vehicles for commercial purposes.',
            'age_requirement': 22,
            'validity_years': 3,
            'fee': 1500.00,
        },
        {
            'name': 'International Driving Permit',
            'code': 'IDP',
            'description': 'License that allows the holder to drive a private motor vehicle in any country or jurisdiction which recognizes IDP.',
            'age_requirement': 18,
            'validity_years': 1,
            'fee': 2000.00,
        },
    ]
    
    # Create license types if they don't exist already
    created_count = 0
    for license_type_data in license_types:
        license_type, created = LicenseType.objects.get_or_create(
            code=license_type_data['code'],
            defaults=license_type_data
        )
        if created:
            created_count += 1
            print(f"Created license type: {license_type.name}")
        else:
            print(f"License type already exists: {license_type.name}")
            
    print(f"Successfully created {created_count} license types")

if __name__ == "__main__":
    create_license_types()