from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0009_add_remarks_to_vehicletransfer'),
    ]

    operations = [
        # Add missing fields to VehicleRegistration
        migrations.AddField(
            model_name='vehicleregistration',
            name='registered_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vehicleregistration',
            name='expiry_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        
        # Add sale_agreement field to VehicleTransfer if not already there
        migrations.AddField(
            model_name='vehicletransfer',
            name='sale_agreement',
            field=models.FileField(default='', upload_to='vehicle_transfers/agreements/'),
            preserve_default=False,
        ),
    ]