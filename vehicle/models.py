import random
import string
from django.db import models
from django.utils import timezone
from django.conf import settings

# Vehicle class constants
VEHICLE_CLASSES = (
    ('MCWOG', 'Motorcycle Without Gear'),
    ('MCWG', 'Motorcycle With Gear'),
    ('LMV', 'Light Motor Vehicle'),
    ('HMV', 'Heavy Motor Vehicle'),
    ('TRANS', 'Transport Vehicle'),
    ('MCWG+LMV', 'Motorcycle With Gear & Light Motor Vehicle'),
    ('OTHER', 'Other'),
)

# Fuel types
FUEL_TYPES = (
    ('PETROL', 'Petrol'),
    ('DIESEL', 'Diesel'),
    ('CNG', 'CNG'),
    ('LPG', 'LPG'),
    ('ELECTRIC', 'Electric'),
    ('HYBRID', 'Hybrid'),
    ('OTHER', 'Other'),
)

# Vehicle types
VEHICLE_TYPES = (
    ('2W', 'Two Wheeler'),
    ('3W', 'Three Wheeler'),
    ('4W', 'Four Wheeler'),
    ('CV', 'Commercial Vehicle'),
    ('OTHER', 'Other'),
)


def generate_registration_number():
    """Generate a unique vehicle registration number"""
    prefix = "MH"
    region_code = ''.join(random.choices(string.digits, k=2))
    alpha_part = ''.join(random.choices(string.ascii_uppercase, k=2))
    digit_part = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}-{region_code}-{alpha_part}-{digit_part}"


def generate_application_number():
    """Generate a unique application number for vehicle registration"""
    prefix = "VR"
    date_str = timezone.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{date_str}{random_str}"


class VehicleClass(models.Model):
    """Vehicle class model (e.g., LMV, HMV, etc.)"""
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    validity_years = models.IntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class VehicleMaker(models.Model):
    """Vehicle maker/manufacturer model"""
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='vehicle_makers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    """Vehicle model (e.g., Swift, City, etc.)"""
    maker = models.ForeignKey(VehicleMaker, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES)
    fuel_type = models.CharField(max_length=10, choices=FUEL_TYPES)
    engine_capacity = models.IntegerField(help_text="Engine capacity in CC")
    seating_capacity = models.IntegerField()
    year_of_manufacture = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.maker.name} {self.name} ({self.year_of_manufacture})"


class RegistrationApplication(models.Model):
    """Vehicle registration application model"""
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

    APPLICATION_TYPES = (
        ('NEW', 'New Registration'),
        ('RENEWAL', 'Registration Renewal'),
        ('TRANSFER', 'Ownership Transfer'),
        ('DUPLICATE', 'Duplicate Registration'),
    )

    application_number = models.CharField(max_length=20, unique=True, blank=True)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    application_type = models.CharField(max_length=10, choices=APPLICATION_TYPES)
    vehicle_class = models.ForeignKey(VehicleClass, on_delete=models.PROTECT)
    vehicle_maker = models.ForeignKey(VehicleMaker, on_delete=models.PROTECT)
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.PROTECT)
    engine_number = models.CharField(max_length=50)
    chassis_number = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=50)
    purchase_date = models.DateField()
    dealer_name = models.CharField(max_length=100)
    temporary_registration = models.CharField(max_length=50, blank=True, null=True)
    insurance_provider = models.CharField(max_length=100)
    insurance_number = models.CharField(max_length=50)
    insurance_validity = models.DateField()
    emission_test_number = models.CharField(max_length=50, blank=True, null=True)
    emission_test_validity = models.DateField(blank=True, null=True)
    
    # Document uploads
    invoice_copy = models.FileField(upload_to='vehicle_documents/invoices/')
    insurance_copy = models.FileField(upload_to='vehicle_documents/insurance/')
    emission_certificate = models.FileField(upload_to='vehicle_documents/emission/', blank=True, null=True)
    owner_id_proof = models.FileField(upload_to='vehicle_documents/id_proofs/')
    owner_address_proof = models.FileField(upload_to='vehicle_documents/address_proofs/')
    
    # Application processing fields
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING')
    remarks = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    inspection_date = models.DateTimeField(blank=True, null=True)
    inspection_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='vehicle_inspections'
    )
    inspection_remarks = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='vehicle_applications_reviewed'
    )
    
    # Payment fields
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    payment_date = models.DateTimeField(blank=True, null=True)
    payment_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application_number} - {self.get_application_type_display()}"
    
    def save(self, *args, **kwargs):
        # Generate application number if it doesn't exist
        if not self.application_number:
            self.application_number = generate_application_number()
        
        # Set fee based on vehicle class if not already set
        if not self.fee and self.vehicle_class:
            self.fee = self.vehicle_class.fee
            
        super().save(*args, **kwargs)


class VehicleRegistration(models.Model):
    """Vehicle registration model"""
    # Status choices
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REGISTERED', 'Registered'),
    )
    
    # Basic vehicle information
    registration_number = models.CharField(max_length=20, unique=True, blank=True)
    application = models.OneToOneField(RegistrationApplication, on_delete=models.CASCADE, related_name='registration')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_vehicles')
    
    # Status fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Vehicle details
    make = models.CharField(max_length=100, blank=True, null=True)  # Vehicle manufacturer
    model = models.CharField(max_length=100, blank=True, null=True)  # Vehicle model
    year = models.IntegerField(blank=True, null=True)  # Manufacturing year
    vehicle_category = models.CharField(max_length=50, blank=True, null=True)  # Vehicle category/class
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES, default='PETROL', blank=True, null=True)
    seating_capacity = models.IntegerField(blank=True, null=True)
    engine_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    chassis_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    registration_type = models.CharField(max_length=50, blank=True, null=True)  # New, Renewal, Transfer, etc.
    
    # Document dates
    purchase_date = models.DateField(blank=True, null=True)
    registered_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(blank=True, null=True)
    
    # Insurance details
    insurance_provider = models.CharField(max_length=100, blank=True, null=True)
    insurance_number = models.CharField(max_length=50, blank=True, null=True)
    insurance_validity = models.DateField(blank=True, null=True)
    insurance_document = models.FileField(upload_to='vehicle_documents/insurance/', blank=True, null=True)
    
    # Document uploads
    vehicle_photo_front = models.ImageField(upload_to='vehicle_photos/front/', blank=True, null=True)
    vehicle_photo_side = models.ImageField(upload_to='vehicle_photos/side/', blank=True, null=True)
    purchase_invoice = models.FileField(upload_to='vehicle_documents/invoices/', blank=True, null=True)
    address_proof = models.FileField(upload_to='vehicle_documents/address_proofs/', blank=True, null=True)
    pollution_certificate = models.FileField(upload_to='vehicle_documents/pollution/', blank=True, null=True)
    road_tax_receipt = models.FileField(upload_to='vehicle_documents/tax/', blank=True, null=True)
    
    # Additional registration details
    fitness_certificate_expiry = models.DateField(blank=True, null=True)
    tax_paid_upto = models.DateField(blank=True, null=True)
    emission_test_validity = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # RC smart card data
    rc_card_number = models.CharField(max_length=50, blank=True, null=True)
    rc_card_issued_date = models.DateField(blank=True, null=True)
    
    # Inspection and verification data
    last_inspection_date = models.DateField(blank=True, null=True)
    next_inspection_due = models.DateField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.registration_number
    
    def save(self, *args, **kwargs):
        # Generate registration number if it doesn't exist
        if not self.registration_number:
            self.registration_number = generate_registration_number()
            
        # Set expiry date based on vehicle class if not already set
        if not self.expiry_date and self.application and self.application.vehicle_class:
            validity_years = self.application.vehicle_class.validity_years
            self.expiry_date = timezone.now().date() + timezone.timedelta(days=validity_years * 365)
            
        super().save(*args, **kwargs)


class VehicleTransfer(models.Model):
    """Vehicle ownership transfer model"""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    )
    
    vehicle = models.ForeignKey(VehicleRegistration, on_delete=models.CASCADE, related_name='transfers')
    current_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='vehicle_transfers_as_seller'
    )
    new_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='vehicle_transfers_as_buyer'
    )
    sale_date = models.DateField()
    sale_amount = models.DecimalField(max_digits=12, decimal_places=2)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    remarks = models.TextField(blank=True)
    
    # Document uploads
    sale_agreement = models.FileField(upload_to='vehicle_transfers/agreements/')
    seller_id_proof = models.FileField(upload_to='vehicle_transfers/id_proofs/')
    buyer_id_proof = models.FileField(upload_to='vehicle_transfers/id_proofs/')
    seller_address_proof = models.FileField(upload_to='vehicle_transfers/address_proofs/')
    buyer_address_proof = models.FileField(upload_to='vehicle_transfers/address_proofs/')
    
    # Processing fields
    transfer_fee = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    payment_date = models.DateTimeField(blank=True, null=True)
    payment_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='vehicle_transfers_processed'
    )
    processed_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Transfer of {self.vehicle.registration_number} from {self.current_owner} to {self.new_owner}"


class VehicleInspection(models.Model):
    """Vehicle inspection model"""
    vehicle = models.ForeignKey(VehicleRegistration, on_delete=models.CASCADE)
    scheduled_date = models.DateTimeField()
    venue = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    passed = models.BooleanField(null=True, blank=True)
    notes = models.TextField(blank=True)
    inspection_report = models.FileField(upload_to='inspection_reports/', blank=True, null=True)
    inspected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inspection for {self.vehicle.registration_number} on {self.scheduled_date}"
