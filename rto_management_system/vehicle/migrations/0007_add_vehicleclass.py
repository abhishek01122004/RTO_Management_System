# Generated manually on 2025-04-19

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0006_auto_20250419_1127'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('description', models.TextField(blank=True)),
                ('fee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('validity_years', models.IntegerField(default=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='VehicleMaker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('country', models.CharField(blank=True, max_length=50)),
                ('website', models.URLField(blank=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='vehicle_makers/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='VehicleModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('vehicle_type', models.CharField(choices=[('2W', 'Two Wheeler'), ('3W', 'Three Wheeler'), ('4W', 'Four Wheeler'), ('CV', 'Commercial Vehicle'), ('OTHER', 'Other')], max_length=10)),
                ('fuel_type', models.CharField(choices=[('PETROL', 'Petrol'), ('DIESEL', 'Diesel'), ('CNG', 'CNG'), ('LPG', 'LPG'), ('ELECTRIC', 'Electric'), ('HYBRID', 'Hybrid'), ('OTHER', 'Other')], max_length=10)),
                ('engine_capacity', models.IntegerField(help_text='Engine capacity in CC')),
                ('seating_capacity', models.IntegerField()),
                ('year_of_manufacture', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('maker', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='models', to='vehicle.vehiclemaker')),
            ],
        ),
        migrations.CreateModel(
            name='RegistrationApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_number', models.CharField(blank=True, max_length=20, unique=True)),
                ('application_type', models.CharField(choices=[('NEW', 'New Registration'), ('RENEWAL', 'Registration Renewal'), ('TRANSFER', 'Ownership Transfer'), ('DUPLICATE', 'Duplicate Registration')], max_length=10)),
                ('engine_number', models.CharField(max_length=50)),
                ('chassis_number', models.CharField(max_length=50, unique=True)),
                ('color', models.CharField(max_length=50)),
                ('purchase_date', models.DateField()),
                ('dealer_name', models.CharField(max_length=100)),
                ('temporary_registration', models.CharField(blank=True, max_length=50, null=True)),
                ('insurance_provider', models.CharField(max_length=100)),
                ('insurance_number', models.CharField(max_length=50)),
                ('insurance_validity', models.DateField()),
                ('emission_test_number', models.CharField(blank=True, max_length=50, null=True)),
                ('emission_test_validity', models.DateField(blank=True, null=True)),
                ('invoice_copy', models.FileField(upload_to='vehicle_documents/invoices/')),
                ('insurance_copy', models.FileField(upload_to='vehicle_documents/insurance/')),
                ('emission_certificate', models.FileField(blank=True, null=True, upload_to='vehicle_documents/emission/')),
                ('owner_id_proof', models.FileField(upload_to='vehicle_documents/id_proofs/')),
                ('owner_address_proof', models.FileField(upload_to='vehicle_documents/address_proofs/')),
                ('application_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('DOCUMENT_VERIFICATION', 'Document Verification'), ('INSPECTION_SCHEDULED', 'Inspection Scheduled'), ('INSPECTION_PASSED', 'Inspection Passed'), ('INSPECTION_FAILED', 'Inspection Failed'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('REGISTERED', 'Registered')], default='PENDING', max_length=25)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('rejection_reason', models.TextField(blank=True, null=True)),
                ('inspection_date', models.DateTimeField(blank=True, null=True)),
                ('inspection_remarks', models.TextField(blank=True, null=True)),
                ('fee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.BooleanField(default=False)),
                ('payment_date', models.DateTimeField(blank=True, null=True)),
                ('payment_transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('inspection_officer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicle_inspections', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicle_applications_reviewed', to=settings.AUTH_USER_MODEL)),
                ('vehicle_class', models.ForeignKey(on_delete=models.deletion.PROTECT, to='vehicle.vehicleclass')),
                ('vehicle_maker', models.ForeignKey(on_delete=models.deletion.PROTECT, to='vehicle.vehiclemaker')),
                ('vehicle_model', models.ForeignKey(on_delete=models.deletion.PROTECT, to='vehicle.vehiclemodel')),
            ],
        ),
    ]