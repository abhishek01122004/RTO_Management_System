import random
import string
from django.db import models
from django.utils import timezone
from accounts.models import User


class TrafficRule(models.Model):
    """Model for traffic rules and corresponding penalties"""
    rule_code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.rule_code} - {self.description[:50]}"


class ChallanType(models.Model):
    """Model for types of challans (e.g., Speeding, Parking, No Helmet)"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    default_penalty = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Challan(models.Model):
    """Model for e-challans issued to violators"""
    STATUS_CHOICES = (
        ('ISSUED', 'Issued'),
        ('UNDER_REVIEW', 'Under Review'),
        ('CONFIRMED', 'Confirmed'),
        ('DISPUTED', 'Disputed'),
        ('PAID', 'Paid'),
        ('CANCELED', 'Canceled'),
    )
    
    challan_number = models.CharField(max_length=20, unique=True)
    violator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='challans')
    vehicle_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=20, blank=True, null=True)
    violation_rules = models.ManyToManyField(TrafficRule, related_name='challans')
    violation_place = models.CharField(max_length=255)
    violation_description = models.TextField()
    evidence_image = models.FileField(upload_to='challan_evidence/', blank=True, null=True)
    issue_date = models.DateField(auto_now_add=True)
    issue_time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ISSUED')
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_challans')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Challan #{self.challan_number} - {self.vehicle_number}"
    
    def save(self, *args, **kwargs):
        if not self.challan_number:
            # Generate a unique challan number
            prefix = "CH"
            date_str = timezone.now().strftime("%y%m%d")
            random_str = ''.join(random.choices(string.digits, k=4))
            self.challan_number = f"{prefix}{date_str}{random_str}"
            
        if not self.due_date:
            # Set due date to 30 days from issue date
            self.due_date = (timezone.now() + timezone.timedelta(days=30)).date()
            
        super().save(*args, **kwargs)


class ChallanPayment(models.Model):
    """Model for challan payments"""
    PAYMENT_METHOD_CHOICES = (
        ('ONLINE', 'Online Payment'),
        ('CASH', 'Cash Payment'),
        ('CARD', 'Card Payment'),
        ('UPI', 'UPI Payment'),
    )
    
    challan = models.OneToOneField(Challan, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_gateway_response = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment for {self.challan.challan_number} - ₹{self.amount}"
    
    def save(self, *args, **kwargs):
        # Update challan payment status
        self.challan.payment_status = True
        self.challan.status = 'PAID'
        self.challan.save()
        
        super().save(*args, **kwargs)
