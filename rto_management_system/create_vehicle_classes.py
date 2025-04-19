"""
Script to create vehicle classes for the RTO Management System
"""

import os
import django
import decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rto_management_system.settings')
django.setup()

from vehicle.models import VehicleClass

def create_vehicle_classes():
    """Create vehicle classes if they don't exist"""
    
    classes = [
        {
            'name': 'Motorcycle Without Gear',
            'code': 'MCWOG', 
            'description': 'Two-wheeler motorcycle without gear system',
            'fee': decimal.Decimal('500.00'),
            'validity_years': 15,
        },
        {
            'name': 'Motorcycle With Gear',
            'code': 'MCWG', 
            'description': 'Two-wheeler motorcycle with gear system',
            'fee': decimal.Decimal('800.00'),
            'validity_years': 15,
        },
        {
            'name': 'Light Motor Vehicle',
            'code': 'LMV', 
            'description': 'Four-wheeler light motor vehicle (e.g., car, jeep)',
            'fee': decimal.Decimal('1500.00'),
            'validity_years': 15,
        },
        {
            'name': 'Heavy Motor Vehicle',
            'code': 'HMV', 
            'description': 'Heavy motor vehicle (e.g., truck, lorry)',
            'fee': decimal.Decimal('3000.00'),
            'validity_years': 10,
        },
        {
            'name': 'Transport Vehicle',
            'code': 'TRANS', 
            'description': 'Public transport vehicle (e.g., bus, taxi)',
            'fee': decimal.Decimal('2500.00'),
            'validity_years': 8,
        },
        {
            'name': 'Motorcycle With Gear & Light Motor Vehicle',
            'code': 'MCWG+LMV', 
            'description': 'Combined license for motorcycle with gear and light motor vehicle',
            'fee': decimal.Decimal('2000.00'),
            'validity_years': 15,
        },
    ]
    
    count = 0
    for class_data in classes:
        # Check if class already exists
        if not VehicleClass.objects.filter(code=class_data['code']).exists():
            VehicleClass.objects.create(**class_data)
            count += 1
            print(f"Created vehicle class: {class_data['name']}")
    
    if count == 0:
        print("All vehicle classes already exist.")
    else:
        print(f"Created {count} vehicle classes.")

if __name__ == "__main__":
    create_vehicle_classes()