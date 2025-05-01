from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Vehicle, RegistrationApplication, VehicleDocument, VehicleTransfer, VehicleMake, VehicleModel
from django.core.validators import MinValueValidator, MaxValueValidator

class VehicleRegistrationForm(forms.ModelForm):
    confirm_chassis_number = forms.CharField(max_length=50, required=True)
    confirm_engine_number = forms.CharField(max_length=50, required=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'make', 'model', 'category', 'fuel_type',
            'engine_number', 'chassis_number', 'confirm_chassis_number',
            'confirm_engine_number', 'manufacturing_year', 'color',
            'seating_capacity'
        ]
        widgets = {
            'manufacturing_year': forms.NumberInput(attrs={'min': 1900, 'max': timezone.now().year}),
            'seating_capacity': forms.NumberInput(attrs={'min': 1}),
        }

    def clean(self):
        cleaned_data = super().clean()
        chassis_number = cleaned_data.get('chassis_number')
        confirm_chassis_number = cleaned_data.get('confirm_chassis_number')
        engine_number = cleaned_data.get('engine_number')
        confirm_engine_number = cleaned_data.get('confirm_engine_number')
        
        if chassis_number and confirm_chassis_number and chassis_number != confirm_chassis_number:
            raise ValidationError("Chassis numbers do not match.")
            
        if engine_number and confirm_engine_number and engine_number != confirm_engine_number:
            raise ValidationError("Engine numbers do not match.")
            
        return cleaned_data

class VehicleDocumentForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument
        fields = ['document_type', 'file', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class VehicleTransferForm(forms.ModelForm):
    class Meta:
        model = VehicleTransfer
        fields = ['buyer', 'transfer_date']
        widgets = {
            'transfer_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_transfer_date(self):
        transfer_date = self.cleaned_data.get('transfer_date')
        if transfer_date and transfer_date > timezone.now().date():
            raise ValidationError("Transfer date cannot be in the future.")
        return transfer_date

class VehicleReviewForm(forms.ModelForm):
    class Meta:
        model = RegistrationApplication
        fields = ['status', 'review_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'review_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow APPROVED or REJECTED status for review
        self.fields['status'].choices = [
            ('APPROVED', 'Approve'),
            ('REJECTED', 'Reject'),
        ]

class TransferReviewForm(forms.ModelForm):
    class Meta:
        model = VehicleTransfer
        fields = ['status', 'review_notes']
        widgets = {
            'review_notes': forms.Textarea(attrs={'rows': 4}),
        }

class VehicleForm(forms.ModelForm):
    make = forms.ModelChoiceField(
        queryset=VehicleMake.objects.all(),
        empty_label="Select Make",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    model = forms.ModelChoiceField(
        queryset=VehicleModel.objects.none(),
        empty_label="Select Model",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    class Meta:
        model = Vehicle
        fields = [
            'registration_number', 'make', 'model', 'category', 'fuel_type',
            'engine_number', 'chassis_number', 'manufacturing_year', 'color',
            'seating_capacity', 'registration_date', 'expiry_date',
            'address_proof', 'invoice_copy', 'vehicle_photograph'
        ]
        widgets = {
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'category': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'engine_number': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'chassis_number': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'manufacturing_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'min': 1900,
                'max': timezone.now().year
            }),
            'color': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'seating_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'min': 1
            }),
            'registration_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'expiry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'address_proof': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
                'required': 'required'
            }),
            'invoice_copy': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
                'required': 'required'
            }),
            'vehicle_photograph': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.jpg,.jpeg,.png',
                'required': 'required'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'make' in self.data:
            try:
                make_id = int(self.data.get('make'))
                self.fields['model'].queryset = VehicleModel.objects.filter(make_id=make_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.make:
            self.fields['model'].queryset = self.instance.make.vehiclemodel_set.all()

    def clean(self):
        cleaned_data = super().clean()
        registration_date = cleaned_data.get('registration_date')
        expiry_date = cleaned_data.get('expiry_date')
        manufacturing_year = cleaned_data.get('manufacturing_year')

        if registration_date and expiry_date and registration_date >= expiry_date:
            raise ValidationError("Expiry date must be after registration date.")

        if manufacturing_year and manufacturing_year > timezone.now().year:
            raise ValidationError("Manufacturing year cannot be in the future.")

        return cleaned_data 