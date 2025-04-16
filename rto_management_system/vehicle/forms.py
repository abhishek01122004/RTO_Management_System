from django import forms
from .models import VehicleRegistration, VehicleInspection, VehicleTransfer
import datetime


class VehicleRegistrationForm(forms.ModelForm):
    """Form for vehicle registration"""
    
    # Additional confirmation field
    confirm_chassis_number = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Chassis Number'})
    )
    
    class Meta:
        model = VehicleRegistration
        fields = [
            'registration_type', 'vehicle_category', 'make', 'model', 'year',
            'chassis_number', 'engine_number', 'fuel_type', 'seating_capacity',
            'color', 'purchase_date', 'purchase_invoice', 'insurance_provider',
            'insurance_number', 'insurance_validity', 'insurance_document',
            'pollution_certificate', 'road_tax_receipt', 'vehicle_photo_front',
            'vehicle_photo_side', 'address_proof'
        ]
        widgets = {
            'registration_type': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_category': forms.Select(attrs={'class': 'form-control'}),
            'make': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vehicle Make'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vehicle Model'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Manufacturing Year', 'min': 1900, 'max': datetime.datetime.now().year}),
            'chassis_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chassis Number'}),
            'engine_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Engine Number'}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select Fuel Type'),
                ('PETROL', 'Petrol'),
                ('DIESEL', 'Diesel'),
                ('CNG', 'CNG'),
                ('LPG', 'LPG'),
                ('ELECTRIC', 'Electric'),
                ('HYBRID', 'Hybrid'),
            ]),
            'seating_capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Seating Capacity', 'min': 1}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vehicle Color'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_invoice': forms.FileInput(attrs={'class': 'form-control'}),
            'insurance_provider': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insurance Provider'}),
            'insurance_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insurance Policy Number'}),
            'insurance_validity': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'insurance_document': forms.FileInput(attrs={'class': 'form-control'}),
            'pollution_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'road_tax_receipt': forms.FileInput(attrs={'class': 'form-control'}),
            'vehicle_photo_front': forms.FileInput(attrs={'class': 'form-control'}),
            'vehicle_photo_side': forms.FileInput(attrs={'class': 'form-control'}),
            'address_proof': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        chassis_number = cleaned_data.get('chassis_number')
        confirm_chassis_number = cleaned_data.get('confirm_chassis_number')
        
        if chassis_number != confirm_chassis_number:
            raise forms.ValidationError("Chassis numbers don't match. Please check and try again.")
        
        purchase_date = cleaned_data.get('purchase_date')
        insurance_validity = cleaned_data.get('insurance_validity')
        
        if purchase_date and insurance_validity and purchase_date > insurance_validity:
            raise forms.ValidationError("Insurance validity date cannot be before the purchase date.")
        
        return cleaned_data


class VehicleRegistrationReviewForm(forms.ModelForm):
    """Form for RTO officers to review vehicle registrations"""
    
    class Meta:
        model = VehicleRegistration
        fields = ['status', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class VehicleInspectionForm(forms.ModelForm):
    """Form for scheduling vehicle inspections"""
    
    class Meta:
        model = VehicleInspection
        fields = ['scheduled_date', 'venue', 'instructions']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Inspection Venue/Address'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class InspectionResultForm(forms.ModelForm):
    """Form for recording vehicle inspection results"""
    
    class Meta:
        model = VehicleInspection
        fields = ['passed', 'notes', 'inspection_report']
        widgets = {
            'passed': forms.Select(attrs={'class': 'form-control'}, 
                                 choices=[(True, 'Pass'), (False, 'Fail')]),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'inspection_report': forms.FileInput(attrs={'class': 'form-control'}),
        }


class VehicleTransferForm(forms.ModelForm):
    """Form for vehicle ownership transfer"""
    
    new_owner_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'New Owner Email'})
    )
    
    class Meta:
        model = VehicleTransfer
        fields = ['sale_amount', 'sale_date', 'transfer_document']
        widgets = {
            'sale_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Sale Amount', 'min': 1}),
            'sale_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'transfer_document': forms.FileInput(attrs={'class': 'form-control'}),
        }
