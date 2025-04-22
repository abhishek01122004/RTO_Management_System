from django import forms
from .models import LicenseApplication, TestSchedule


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
    
    class Meta:
        model = LicenseApplication
        fields = ['status', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TestScheduleForm(forms.ModelForm):
    """Form for scheduling license tests"""
    
    class Meta:
        model = TestSchedule
        fields = ['test_type', 'scheduled_date', 'venue', 'instructions']
        widgets = {
            'test_type': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


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
