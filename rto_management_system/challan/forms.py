from django import forms
from django.core.validators import RegexValidator
from .models import Challan, TrafficRule, ChallanPayment, ChallanType
from accounts.models import User
from vehicle.models import VehicleRegistration


class TrafficRuleForm(forms.ModelForm):
    """Form for creating and editing traffic rules"""
    class Meta:
        model = TrafficRule
        fields = ['rule_code', 'description', 'penalty_amount', 'is_active']
        widgets = {
            'rule_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rule Code (e.g., TR001)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detailed description of the traffic rule violation'}),
            'penalty_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def clean_rule_code(self):
        """Ensure rule code is unique"""
        rule_code = self.cleaned_data.get('rule_code')
        
        # If editing an existing instance, exclude the current instance from uniqueness check
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            if TrafficRule.objects.filter(rule_code=rule_code).exclude(pk=instance.pk).exists():
                raise forms.ValidationError("This rule code already exists. Please choose a different one.")
        else:  # New instance
            if TrafficRule.objects.filter(rule_code=rule_code).exists():
                raise forms.ValidationError("This rule code already exists. Please choose a different one.")
                
        return rule_code


class ChallanTypeForm(forms.ModelForm):
    """Form for creating and editing challan types"""
    class Meta:
        model = ChallanType
        fields = ['name', 'description', 'default_penalty', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Challan Type Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description of this challan type'}),
            'default_penalty': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ChallanGenerationForm(forms.ModelForm):
    """Form for generating new challans"""
    
    vehicle_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vehicle Registration Number'})
    )
    
    violator_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Violator Email (if known)'})
    )
    
    violator_phone = forms.CharField(
        required=False,
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Violator Phone (if known)'})
    )
    
    license_number = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'License Number (if known)'})
    )
    
    selected_rules = forms.ModelMultipleChoiceField(
        queryset=TrafficRule.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'rule-checkbox'})
    )
    
    class Meta:
        model = Challan
        fields = ['vehicle_number', 'violation_place', 'violation_description', 'evidence_image']
        widgets = {
            'violation_place': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location of Violation'}),
            'violation_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description of Violation'}),
            'evidence_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_vehicle_number(self):
        vehicle_number = self.cleaned_data.get('vehicle_number')
        try:
            VehicleRegistration.objects.get(registration_number=vehicle_number)
        except VehicleRegistration.DoesNotExist:
            raise forms.ValidationError("This vehicle registration number is not in our records.")
        return vehicle_number
    
    def clean_violator_email(self):
        email = self.cleaned_data.get('violator_email')
        if email:
            try:
                User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("No user found with this email address.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        selected_rules = cleaned_data.get('selected_rules')
        
        if not selected_rules or len(selected_rules) == 0:
            raise forms.ValidationError("Please select at least one traffic rule violation.")
        
        return cleaned_data


class ChallanSearchForm(forms.Form):
    """Form for searching challans"""
    
    search_type = forms.ChoiceField(
        choices=[
            ('challan_number', 'Challan Number'),
            ('vehicle_number', 'Vehicle Number'),
            ('license_number', 'License Number'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search_value = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter search value'})
    )


class ChallanUpdateForm(forms.ModelForm):
    """Form for updating challan details by officers"""
    
    class Meta:
        model = Challan
        fields = ['status', 'remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ChallanPaymentForm(forms.ModelForm):
    """Form for recording offline challan payments"""
    
    class Meta:
        model = ChallanPayment
        fields = ['amount', 'payment_method', 'transaction_id', 'remarks']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Receipt/Transaction ID'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any additional information'}),
        }
