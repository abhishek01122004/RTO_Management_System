from django.core.management.base import BaseCommand
from vehicle.models import Vehicle, VehicleTransfer

class Command(BaseCommand):
    help = 'Updates the status of vehicles with approved transfers to TRANSFERRED'

    def handle(self, *args, **options):
        # Get all vehicles that have approved transfers
        approved_transfers = VehicleTransfer.objects.filter(status='APPROVED')
        
        for transfer in approved_transfers:
            vehicle = transfer.vehicle
            if vehicle.status != 'TRANSFERRED':
                vehicle.status = 'TRANSFERRED'
                vehicle.owner = transfer.buyer
                vehicle.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Updated vehicle {vehicle.registration_number} to TRANSFERRED')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully updated all vehicles with approved transfers')
        ) 