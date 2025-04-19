from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from license.models import LicenseApplication


@login_required
def dashboard(request):
    """Main dashboard view that redirects to appropriate role-specific dashboard"""
    user_type = request.user.user_type
    
    if user_type == 'CITIZEN':
        return citizen_dashboard(request)
    elif user_type == 'OFFICER':
        return officer_dashboard(request)
    elif user_type == 'ADMIN':
        return admin_dashboard(request)
    else:
        # Default dashboard
        return render(request, 'dashboard/dashboard.html')


@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on user type"""
    if request.user.user_type == 'CITIZEN':
        return redirect('citizen_dashboard')
    elif request.user.user_type == 'OFFICER':
        return redirect('officer_dashboard')
    elif request.user.user_type == 'ADMIN':
        return redirect('admin_dashboard')
    else:
        return redirect('home')


@login_required
def citizen_dashboard(request):
    """Dashboard view for citizens"""
    if request.user.user_type != 'CITIZEN':
        return redirect('dashboard')
    
    # Basic user information
    context = {
        'user': request.user,
        'current_date': timezone.now(),
    }
    
    return render(request, 'dashboard/citizen_dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.user_type == 'OFFICER')
def officer_dashboard(request):
    """Dashboard view for RTO officers"""
    context = {
        'user': request.user,
        'current_date': timezone.now(),
    }
    
    return render(request, 'dashboard/officer_dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def admin_dashboard(request):
    """Dashboard view for administrators"""
    context = {
        'user': request.user,
        'current_date': timezone.now(),
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def check_application_status(request, application_type, application_number):
    """View to check status of an application"""
    # This is a placeholder function, you'll implement actual functionality later
    context = {
        'application_type': application_type,
        'application_number': application_number,
        'status': 'Placeholder status',
    }
    
    return render(request, 'dashboard/check_status.html', context)


@login_required
def track_license_status(request):
    """View to track status of all license applications for the logged-in citizen"""
    # Check if user is a citizen
    if request.user.user_type != 'CITIZEN':
        return redirect('dashboard')
    
    # Get all license applications for the current user
    applications = LicenseApplication.objects.filter(applicant=request.user).order_by('-application_date')
    
    context = {
        'applications': applications,
        'current_date': timezone.now(),
    }
    
    return render(request, 'dashboard/track_license_status.html', context)