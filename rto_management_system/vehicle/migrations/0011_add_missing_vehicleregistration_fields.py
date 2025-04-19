from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0010_add_missing_db_columns'),
    ]

    operations = [
        # Add missing fields to VehicleRegistration
        migrations.AddField(
            model_name='vehicleregistration',
            name='fitness_certificate_expiry',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehicleregistration',
            name='tax_paid_upto',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehicleregistration',
            name='emission_test_validity',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehicleregistration',
            name='insurance_validity',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vehicleregistration',
            name='rc_card_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='vehicleregistration',
            name='rc_card_issued_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehicleregistration',
            name='last_inspection_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehicleregistration',
            name='next_inspection_due',
            field=models.DateField(blank=True, null=True),
        ),
    ]