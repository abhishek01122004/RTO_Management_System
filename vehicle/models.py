from django.db import models
from django.conf import settings
from django.utils import timezone

class VehicleCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class VehicleMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class VehicleModel(models.Model):
    make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.make.name} {self.name}"

class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('TRANSFERRED', 'Transferred'),
    ]
    
    CATEGORY_CHOICES = [
        ('LMV', 'Light Motor Vehicle'),
        ('MCWG', 'Motor Cycle With Gear'),
        ('MCWOG', 'Motor Cycle Without Gear'),
        ('HMV', 'Heavy Motor Vehicle'),
    ]
    
    FUEL_TYPE_CHOICES = [
        ('PETROL', 'Petrol'),
        ('DIESEL', 'Diesel'),
        ('ELECTRIC', 'Electric'),
        ('HYBRID', 'Hybrid'),
    ]
    
    registration_number = models.CharField(max_length=20, unique=True)
    make = models.ForeignKey(VehicleMake, on_delete=models.PROTECT)
    model = models.ForeignKey(VehicleModel, on_delete=models.PROTECT)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    fuel_type = models.CharField(max_length=10, choices=FUEL_TYPE_CHOICES)
    engine_number = models.CharField(max_length=50, unique=True)
    chassis_number = models.CharField(max_length=50, unique=True)
    manufacturing_year = models.IntegerField()
    color = models.CharField(max_length=50)
    seating_capacity = models.IntegerField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    registration_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address_proof = models.FileField(upload_to='vehicle_documents/address_proof/', blank=True, null=True)
    invoice_copy = models.FileField(upload_to='vehicle_documents/invoice/', blank=True, null=True)
    vehicle_photograph = models.ImageField(upload_to='vehicle_documents/photographs/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.registration_number} - {self.make.name} {self.model.name}"

class RegistrationApplication(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    application_number = models.CharField(max_length=20, unique=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.application_number} - {self.vehicle.registration_number}"

class VehicleDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('RC', 'Registration Certificate'),
        ('INSURANCE', 'Insurance Certificate'),
        ('PUC', 'Pollution Under Control Certificate'),
        ('INVOICE', 'Invoice'),
        ('OTHER', 'Other'),
    ]
    
    application = models.ForeignKey(RegistrationApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='vehicle_documents/')
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.application.application_number} - {self.get_document_type_display()}"

class VehicleTransfer(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sold_vehicles')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bought_vehicles')
    transfer_number = models.CharField(max_length=20, unique=True)
    transfer_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_transfers')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.transfer_number} - {self.vehicle.registration_number}" 