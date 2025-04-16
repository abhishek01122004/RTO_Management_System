from django.db import models
from accounts.models import User


class VehicleCategory(models.Model):
    """Model for vehicle categories (car, motorcycle, etc.)"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name


class VehicleRegistration(models.Model):
    """Model for vehicle registration applications"""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('DOCUMENT_VERIFICATION', 'Document Verification'),
        ('INSPECTION_SCHEDULED', 'Inspection Scheduled'),
        ('INSPECTION_PASSED', 'Inspection Passed'),
        ('INSPECTION_FAILED', 'Inspection Failed'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REGISTERED', 'Registered'),
    )
    
    REGISTRATION_TYPE_CHOICES = (
        ('NEW', 'New Registration'),
        ('RENEWAL', 'Registration Renewal'),
        ('TRANSFER', 'Ownership Transfer'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicle_registrations')
    registration_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    temporary_number = models.CharField(max_length=20, unique=True)
    registration_type = models.CharField(max_length=20, choices=REGISTRATION_TYPE_CHOICES, default='NEW')
    vehicle_category = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    chassis_number = models.CharField(max_length=100, unique=True)
    engine_number = models.CharField(max_length=100, unique=True)
    fuel_type = models.CharField(max_length=50)
    seating_capacity = models.PositiveIntegerField()
    color = models.CharField(max_length=50)
    purchase_date = models.DateField()
    purchase_invoice = models.FileField(upload_to='vehicle_invoices/')
    insurance_provider = models.CharField(max_length=100)
    insurance_number = models.CharField(max_length=100)
    insurance_validity = models.DateField()
    insurance_document = models.FileField(upload_to='vehicle_insurance/')
    pollution_certificate = models.FileField(upload_to='vehicle_pollution/', blank=True, null=True)
    road_tax_receipt = models.FileField(upload_to='vehicle_tax/', blank=True, null=True)
    vehicle_photo_front = models.FileField(upload_to='vehicle_photos/')
    vehicle_photo_side = models.FileField(upload_to='vehicle_photos/')
    address_proof = models.FileField(upload_to='vehicle_address_proof/')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    application_date = models.DateField(auto_now_add=True)
    rejection_reason = models.TextField(blank=True, null=True)
    payment_status = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    inspection_date = models.DateTimeField(null=True, blank=True)
    inspection_result = models.BooleanField(null=True, blank=True)
    inspection_notes = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='reviewed_vehicle_registrations')
    registration_date = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        reg_no = self.registration_number or self.temporary_number
        return f"{reg_no} - {self.make} {self.model} ({self.owner.email})"


class VehicleInspection(models.Model):
    """Model for vehicle inspection scheduling and results"""
    registration = models.ForeignKey(VehicleRegistration, on_delete=models.CASCADE, related_name='inspections')
    scheduled_date = models.DateTimeField()
    venue = models.CharField(max_length=255)
    instructions = models.TextField()
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='conducted_inspections')
    is_completed = models.BooleanField(default=False)
    passed = models.BooleanField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    inspection_report = models.FileField(upload_to='inspection_reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Inspection for {self.registration.temporary_number} on {self.scheduled_date}"


class RegisteredVehicle(models.Model):
    """Model for registered vehicles with complete information"""
    registration = models.OneToOneField(VehicleRegistration, on_delete=models.CASCADE, related_name='registered_vehicle')
    registration_certificate = models.FileField(upload_to='registration_certificates/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='vehicle_qr_codes/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Registered Vehicle: {self.registration.registration_number}"


class VehicleTransfer(models.Model):
    """Model for vehicle ownership transfers"""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    )
    
    vehicle = models.ForeignKey(RegisteredVehicle, on_delete=models.CASCADE, related_name='transfers')
    current_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicle_transfers_as_owner')
    new_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicle_transfers_as_buyer')
    application_date = models.DateField(auto_now_add=True)
    transfer_document = models.FileField(upload_to='transfer_documents/')
    sale_amount = models.DecimalField(max_digits=12, decimal_places=2)
    sale_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='reviewed_vehicle_transfers')
    completion_date = models.DateField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Transfer of {self.vehicle.registration.registration_number} from {self.current_owner.email} to {self.new_owner.email}"
