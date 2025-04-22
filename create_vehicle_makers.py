"""
Script to create vehicle makers and models for the RTO Management System
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rto_management_system.settings')
django.setup()

from vehicle.models import VehicleMaker, VehicleModel

def create_vehicle_makers_and_models():
    """Create vehicle makers and models if they don't exist"""
    
    # Define makers and models
    makers_data = [
        {
            'name': 'Maruti Suzuki',
            'country': 'India',
            'website': 'https://www.marutisuzuki.com/',
            'models': [
                {
                    'name': 'Swift',
                    'vehicle_type': '4W',
                    'fuel_type': 'PETROL',
                    'engine_capacity': 1197,
                    'seating_capacity': 5,
                    'year_of_manufacture': 2023,
                },
                {
                    'name': 'Baleno',
                    'vehicle_type': '4W',
                    'fuel_type': 'PETROL',
                    'engine_capacity': 1197,
                    'seating_capacity': 5,
                    'year_of_manufacture': 2023,
                },
                {
                    'name': 'Brezza',
                    'vehicle_type': '4W',
                    'fuel_type': 'PETROL',
                    'engine_capacity': 1462,
                    'seating_capacity': 5,
                    'year_of_manufacture': 2023,
                },
            ]
        },
        {
            'name': 'Hyundai',
            'country': 'South Korea',
            'website': 'https://www.hyundai.com/',
            'models': [
                {
                    'name': 'i20',
                    'vehicle_type': '4W',
                    'fuel_type': 'PETROL',
                    'engine_capacity': 1197,
                    'seating_capacity': 5,
                    'year_of_manufacture': 2023,
                },
                {
                    'name': 'Creta',
                    'vehicle_type': '4W',
                    'fuel_type': 'DIESEL',
                    'engine_capacity': 1493,
                    'seating_capacity': 5,
                    'year_of_manufacture': 2023,
                },
            ]
        },
        {
            'name': 'Honda',
            'country': 'Japan',
            'website': 'https://www.honda.com/',
            'models': [
                {
                    'name': 'City',
                    'vehicle_type': '4W',
                    'fuel_type': 'PETROL',
                    'engine_capacity': 1498,
                    'seating_capacity': 5,
                    'year_of_manufacture': 2023,
                },
                {
                    'name': 'Amaze',
                    'vehicle_type': '4W',
                    'fuel_type': 'PETROL',
                    'engine_capacity': 1199,
                    'seating_capacity': 5,
                    'year_of_manufacture': 2023,
                },
            ]
        },
        {
            'name': 'Hero',
            'country': 'India',
            'website': 'https://www.heromotocorp.com/',
            'models': [
                {
                    'name': 'Splendor',
                    'vehicle_type': '2W',
                    'fuel_type': 'PETROL',
                    'engine_capacity': 97,
                    'seating_capacity': 2,
                    'year_of_manufacture': 2023,
                },
                {
                    'name': 'Passion',
                    'vehicle_type': '2W',
                    'fuel_type': 'PETROL',
                    'engine_capacity': 113,
                    'seating_capacity': 2,
                    'year_of_manufacture': 2023,
                },
            ]
        },
        {
            'name': 'Bajaj',
            'country': 'India',
            'website': 'https://www.bajajauto.com/',
            'models': [
                {
                    'name': 'Pulsar',
                    'vehicle_type': '2W',
                    'fuel_type': 'PETROL',
                    'engine_capacity': 150,
                    'seating_capacity': 2,
                    'year_of_manufacture': 2023,
                },
                {
                    'name': 'Avenger',
                    'vehicle_type': '2W',
                    'fuel_type': 'PETROL',
                    'engine_capacity': 220,
                    'seating_capacity': 2,
                    'year_of_manufacture': 2023,
                },
            ]
        },
    ]
    
    makers_count = 0
    models_count = 0
    
    # Create makers and models
    for maker_data in makers_data:
        models_list = maker_data.pop('models')
        
        # Check if maker already exists
        maker, created = VehicleMaker.objects.get_or_create(
            name=maker_data['name'],
            defaults=maker_data
        )
        
        if created:
            makers_count += 1
            print(f"Created vehicle maker: {maker.name}")
        
        # Create models for this maker
        for model_data in models_list:
            if not VehicleModel.objects.filter(
                maker=maker, 
                name=model_data['name'],
                year_of_manufacture=model_data['year_of_manufacture']
            ).exists():
                VehicleModel.objects.create(maker=maker, **model_data)
                models_count += 1
                print(f"Created vehicle model: {maker.name} {model_data['name']}")
    
    if makers_count == 0 and models_count == 0:
        print("All vehicle makers and models already exist.")
    else:
        print(f"Created {makers_count} vehicle makers and {models_count} vehicle models.")

if __name__ == "__main__":
    create_vehicle_makers_and_models()