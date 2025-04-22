from django.db import models
from accounts.models import User


class LicenseType(models.Model):
    """Define different types of licenses available"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    age_requirement = models.PositiveIntegerField(default=18)
    validity_years = models.PositiveIntegerField(default=10)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class LicenseApplication(models.Model):
    """Model for license applications"""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('DOCUMENT_VERIFICATION', 'Document Verification'),
        ('SCHEDULED_FOR_TEST', 'Scheduled for Test'),
        ('TEST_PASSED', 'Test Passed'),
        ('TEST_FAILED', 'Test Failed'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('ISSUED', 'Issued'),
    )
    
    APPLICATION_TYPE_CHOICES = (
        ('NEW', 'New License'),
        ('RENEWAL', 'License Renewal'),
        ('DUPLICATE', 'Duplicate License'),
    )
    
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='license_applications')
    license_type = models.ForeignKey(LicenseType, on_delete=models.CASCADE)
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPE_CHOICES, default='NEW')
    application_number = models.CharField(max_length=20, unique=True)
    application_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    photo = models.ImageField(upload_to='license_photos/')
    signature = models.ImageField(upload_to='license_signatures/')
    id_proof = models.FileField(upload_to='license_id_proofs/')
    address_proof = models.FileField(upload_to='license_address_proofs/')
    test_date = models.DateTimeField(null=True, blank=True)
    test_result = models.BooleanField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    payment_status = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='reviewed_license_applications')
    issued_date = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"License Application #{self.application_number} - {self.applicant.email}"
    
    def get_absolute_url(self):
        return f"/license/application/{self.application_number}/"


class DrivingLicense(models.Model):
    """Model for issued driving licenses"""
    license_number = models.CharField(max_length=20, unique=True)
    application = models.OneToOneField(LicenseApplication, on_delete=models.CASCADE, related_name='issued_license')
    holder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='driving_licenses')
    license_type = models.ForeignKey(LicenseType, on_delete=models.CASCADE)
    issued_date = models.DateField()
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)
    qr_code = models.ImageField(upload_to='license_qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"License #{self.license_number} - {self.holder.get_full_name()}"


class TestSchedule(models.Model):
    """Model for license test scheduling"""
    TEST_TYPES = (
        ('WRITTEN', 'Written Test'),
        ('DRIVING', 'Driving Test'),
    )
    
    application = models.ForeignKey(LicenseApplication, on_delete=models.CASCADE, related_name='test_schedules')
    test_type = models.CharField(max_length=10, choices=TEST_TYPES)
    scheduled_date = models.DateTimeField()
    venue = models.CharField(max_length=255)
    instructions = models.TextField()
    is_completed = models.BooleanField(default=False)
    passed = models.BooleanField(null=True, blank=True)
    examiner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='conducted_tests')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.test_type} Test for {self.application.application_number}"
