from django.core.management.base import BaseCommand
from vehicle.models import VehicleMake, VehicleModel

class Command(BaseCommand):
    help = 'Populates the database with sample vehicle makes and models'

    def handle(self, *args, **kwargs):
        # Create vehicle makes
        makes = {
            'Maruti Suzuki': ['Swift', 'Baleno', 'Dzire', 'Wagon R', 'Alto'],
            'Hyundai': ['i20', 'Verna', 'Creta', 'Venue', 'Santro'],
            'Honda': ['City', 'Amaze', 'Jazz', 'WR-V', 'Brio'],
            'Toyota': ['Innova', 'Fortuner', 'Glanza', 'Urban Cruiser', 'Camry'],
            'Tata': ['Nexon', 'Harrier', 'Safari', 'Tiago', 'Altroz'],
            'Mahindra': ['Thar', 'Scorpio', 'XUV700', 'Bolero', 'XUV300'],
            'Kia': ['Seltos', 'Sonet', 'Carnival', 'EV6', 'Carens'],
            'Renault': ['Kwid', 'Triber', 'Duster', 'Kiger', 'Captur'],
            'Volkswagen': ['Polo', 'Vento', 'Taigun', 'Virtus', 'Tiguan'],
            'Skoda': ['Rapid', 'Kushaq', 'Slavia', 'Octavia', 'Superb']
        }

        # Clear existing data
        VehicleModel.objects.all().delete()
        VehicleMake.objects.all().delete()

        # Create makes and models
        for make_name, models in makes.items():
            make = VehicleMake.objects.create(name=make_name)
            for model_name in models:
                VehicleModel.objects.create(make=make, name=model_name)

        self.stdout.write(self.style.SUCCESS('Successfully populated vehicle makes and models')) 