from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from license.models import LicenseApplication
from vehicle.models import RegistrationApplication
from challan.models import Challan
from django.contrib.auth.models import User
from django.http import JsonResponse, Http404
from django.core.exceptions import PermissionDenied


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
    try:
        if application_type == 'license':
            application = LicenseApplication.objects.get(application_number=application_number)
        elif application_type == 'vehicle':
            application = RegistrationApplication.objects.get(application_number=application_number)
        elif application_type == 'challan':
            application = Challan.objects.get(challan_number=application_number)
        else:
            raise Http404("Invalid application type")
        
        # Check if user has permission to view this application
        if request.user.user_type == 'CITIZEN':
            if application_type == 'license' and application.applicant != request.user:
                raise PermissionDenied
            elif application_type == 'vehicle' and application.applicant != request.user:
                raise PermissionDenied
            elif application_type == 'challan' and application.violator != request.user:
                raise PermissionDenied
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'application_type': application_type,
                'application_number': application_number,
                'status': application.status,
                'last_updated': application.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        context = {
            'application_type': application_type,
            'application_number': application_number,
            'status': application.status,
            'last_updated': application.updated_at
        }
        
        return render(request, 'dashboard/check_status.html', context)
    
    except (LicenseApplication.DoesNotExist, RegistrationApplication.DoesNotExist, Challan.DoesNotExist):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Application not found'}, status=404)
        raise Http404("Application not found")
    except PermissionDenied:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'You do not have permission to view this application'}, status=403)
        raise PermissionDenied


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


@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_officers(request):
    """View for managing RTO officers."""
    officers = User.objects.filter(user_type='OFFICER')
    context = {
        'officers': officers,
    }
    return render(request, 'dashboard/manage_officers.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def review_applications(request):
    """View for reviewing all applications."""
    # Get all applications that need review
    license_applications = LicenseApplication.objects.filter(status='SUBMITTED')
    vehicle_applications = RegistrationApplication.objects.filter(status='SUBMITTED')
    
    context = {
        'license_applications': license_applications,
        'vehicle_applications': vehicle_applications,
    }
    return render(request, 'dashboard/review_applications.html', context)