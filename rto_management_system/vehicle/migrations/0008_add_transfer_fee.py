from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0007_add_vehicleclass'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicletransfer',
            name='transfer_fee',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=500),
            preserve_default=False,
        ),
    ]