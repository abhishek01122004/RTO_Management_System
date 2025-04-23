from django import forms
from .models import LicenseApplication, TestSchedule
from django.utils import timezone


class LicenseApplicationForm(forms.ModelForm):
    """Form for applying for a driving license"""
    
    class Meta:
        model = LicenseApplication
        fields = ['license_type', 'application_type', 'photo', 'signature', 
                  'id_proof', 'address_proof']
        widgets = {
            'license_type': forms.Select(attrs={'class': 'form-control'}),
            'application_type': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'signature': forms.FileInput(attrs={'class': 'form-control'}),
            'id_proof': forms.FileInput(attrs={'class': 'form-control'}),
            'address_proof': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add custom validation or field modifications based on user
        if user and user.user_type != 'CITIZEN':
            self.fields['application_type'].widget.attrs['disabled'] = True
            self.fields['license_type'].widget.attrs['disabled'] = True


class LicenseApplicationReviewForm(forms.ModelForm):
    """Form for RTO officers to review license applications"""
    
    test_date = forms.DateTimeField(
        required=False,
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
            }
        ),
        help_text="Select date and time for the test"
    )
    
    class Meta:
        model = LicenseApplication
        fields = ['status', 'rejection_reason', 'test_date']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_test_date(self):
        test_date = self.cleaned_data.get('test_date')
        if test_date:
            # Ensure test_date is timezone-aware
            if timezone.is_naive(test_date):
                test_date = timezone.make_aware(test_date)
            
            if test_date < timezone.now():
                raise forms.ValidationError("Test date cannot be in the past.")
        return test_date


class TestScheduleForm(forms.ModelForm):
    """Form for scheduling license tests"""
    
    scheduled_date = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
            }
        )
    )
    
    class Meta:
        model = TestSchedule
        fields = ['test_type', 'scheduled_date', 'venue', 'instructions']
        widgets = {
            'test_type': forms.Select(attrs={'class': 'form-control'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date and scheduled_date < timezone.now():
            raise forms.ValidationError("Test date cannot be in the past.")
        return scheduled_date


class TestResultForm(forms.ModelForm):
    """Form for recording license test results"""
    
    class Meta:
        model = TestSchedule
        fields = ['passed', 'notes']
        widgets = {
            'passed': forms.Select(attrs={'class': 'form-control'}, 
                                 choices=[(True, 'Pass'), (False, 'Fail')]),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
