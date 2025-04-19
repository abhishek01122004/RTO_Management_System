from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0009_add_remarks_to_vehicletransfer'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicleregistration',
            name='registered_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]