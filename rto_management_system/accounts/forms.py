from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import User, CitizenProfile, OfficerProfile


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form with bootstrap styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email Address'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})


class CitizenRegistrationForm(UserCreationForm):
    """Custom form for citizen registration"""
    
    phone_number = forms.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    
    aadhaar_number = forms.CharField(
        max_length=14,  # Increased to allow for spaces
        validators=[
            RegexValidator(
                regex=r'^\d{4}[\s-]?\d{4}[\s-]?\d{4}$|^\d{12}$',
                message="Aadhaar number must be 12 digits with or without spaces/hyphens (e.g., 1234 5678 9012 or 123456789012)"
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Aadhaar Number (e.g., 1234 5678 9012)'})
    )
    
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Full Address', 'rows': 3})
    )
    
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    blood_group = forms.ChoiceField(
        choices=[
            ('', 'Select Blood Group'),
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-'),
            ('O+', 'O+'),
            ('O-', 'O-'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    emergency_contact = forms.CharField(
        max_length=15,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact Number'})
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'aadhaar_number', 
                 'address', 'password1', 'password2')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'CITIZEN'
        if commit:
            user.save()
            CitizenProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                blood_group=self.cleaned_data.get('blood_group'),
                emergency_contact=self.cleaned_data.get('emergency_contact')
            )
        return user


class OfficerRegistrationForm(UserCreationForm):
    """Custom form for officer registration (admin use only)"""
    
    employee_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee ID'})
    )
    
    designation = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Designation'})
    )
    
    department = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'})
    )
    
    joining_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'OFFICER'
        if commit:
            user.save()
            OfficerProfile.objects.create(
                user=user,
                employee_id=self.cleaned_data.get('employee_id'),
                designation=self.cleaned_data.get('designation'),
                department=self.cleaned_data.get('department'),
                joining_date=self.cleaned_data.get('joining_date')
            )
        return user


class UserProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'address', 'profile_picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CitizenProfileUpdateForm(forms.ModelForm):
    """Form for updating citizen profile"""
    
    class Meta:
        model = CitizenProfile
        fields = ('date_of_birth', 'blood_group', 'emergency_contact')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
                ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
            ]),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
        }
