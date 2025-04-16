from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse

from accounts.models import User
from license.models import LicenseApplication, DrivingLicense, TestSchedule
from vehicle.models import VehicleRegistration, RegisteredVehicle, VehicleInspection
from challan.models import Challan, ChallanPayment
from notifications.models import Notification


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
    
    # Get user's license applications
    license_applications = LicenseApplication.objects.filter(
        applicant=request.user
    ).order_by('-application_date')[:5]
    
    # Get user's driving licenses
    driving_licenses = DrivingLicense.objects.filter(
        holder=request.user
    ).order_by('-issued_date')
    
    # Get user's vehicle registrations
    vehicle_registrations = VehicleRegistration.objects.filter(
        owner=request.user
    ).order_by('-application_date')[:5]
    
    # Get user's registered vehicles
    registered_vehicles = VehicleRegistration.objects.filter(
        owner=request.user,
        status='REGISTERED'
    ).select_related('registered_vehicle').order_by('-registration_date')
    
    # Get user's challans
    challans = Challan.objects.filter(
        Q(violator=request.user) | 
        Q(vehicle_number__in=registered_vehicles.values_list('registration_number', flat=True))
    ).order_by('-issue_date')[:5]
    
    # Get unpaid challans count and total amount
    unpaid_challans = Challan.objects.filter(
        (Q(violator=request.user) | 
        Q(vehicle_number__in=registered_vehicles.values_list('registration_number', flat=True))),
        payment_status=False
    )
    unpaid_count = unpaid_challans.count()
    unpaid_amount = unpaid_challans.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Get upcoming test/inspection schedules
    upcoming_tests = TestSchedule.objects.filter(
        application__applicant=request.user,
        scheduled_date__gte=timezone.now(),
        is_completed=False
    ).order_by('scheduled_date')[:3]
    
    upcoming_inspections = VehicleInspection.objects.filter(
        registration__owner=request.user,
        scheduled_date__gte=timezone.now(),
        is_completed=False
    ).order_by('scheduled_date')[:3]
    
    # Get recent notifications
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    # Check if user profile is complete
    profile_complete = True
    missing_fields = []
    
    if not request.user.first_name or not request.user.last_name:
        profile_complete = False
        missing_fields.append('Name')
    
    if not request.user.phone_number:
        profile_complete = False
        missing_fields.append('Phone Number')
    
    if not request.user.address:
        profile_complete = False
        missing_fields.append('Address')
    
    try:
        citizen_profile = request.user.citizen_profile
        if not citizen_profile.date_of_birth:
            profile_complete = False
            missing_fields.append('Date of Birth')
        if not citizen_profile.blood_group:
            profile_complete = False
            missing_fields.append('Blood Group')
    except:
        profile_complete = False
        missing_fields.append('Citizen Profile Details')
    
    context = {
        'license_applications': license_applications,
        'driving_licenses': driving_licenses,
        'vehicle_registrations': vehicle_registrations,
        'registered_vehicles': registered_vehicles,
        'challans': challans,
        'unpaid_count': unpaid_count,
        'unpaid_amount': unpaid_amount,
        'upcoming_tests': upcoming_tests,
        'upcoming_inspections': upcoming_inspections,
        'notifications': notifications,
        'profile_complete': profile_complete,
        'missing_fields': missing_fields,
    }
    
    return render(request, 'dashboard/citizen_dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.user_type == 'OFFICER')
def officer_dashboard(request):
    """Dashboard view for RTO officers"""
    # Get pending applications count
    pending_license_count = LicenseApplication.objects.filter(
        payment_status=True,
        status__in=['PENDING', 'DOCUMENT_VERIFICATION']
    ).count()
    
    pending_vehicle_count = VehicleRegistration.objects.filter(
        payment_status=True,
        status__in=['PENDING', 'DOCUMENT_VERIFICATION']
    ).count()
    
    # Get scheduled tests/inspections for today
    today = timezone.now().date()
    tests_today = TestSchedule.objects.filter(
        scheduled_date__date=today,
        is_completed=False
    ).order_by('scheduled_date')
    
    inspections_today = VehicleInspection.objects.filter(
        scheduled_date__date=today,
        is_completed=False
    ).order_by('scheduled_date')
    
    # Get recent applications
    recent_license_applications = LicenseApplication.objects.filter(
        payment_status=True
    ).order_by('-application_date')[:5]
    
    recent_vehicle_registrations = VehicleRegistration.objects.filter(
        payment_status=True
    ).order_by('-application_date')[:5]
    
    # Get recently issued challans and disputed challans
    recent_challans = Challan.objects.filter(issued_by=request.user).order_by('-issue_date')[:5]
    disputed_challans = Challan.objects.filter(status='DISPUTED').order_by('-updated_at')[:5]
    
    # Get statistics for last 7 days
    last_week = timezone.now().date() - timedelta(days=7)
    
    licenses_issued_weekly = DrivingLicense.objects.filter(
        issued_date__gte=last_week
    ).count()
    
    vehicles_registered_weekly = RegisteredVehicle.objects.filter(
        registration__registration_date__gte=last_week
    ).count()
    
    challans_issued_weekly = Challan.objects.filter(
        issue_date__gte=last_week
    ).count()
    
    payments_received_weekly = ChallanPayment.objects.filter(
        payment_date__date__gte=last_week
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'pending_license_count': pending_license_count,
        'pending_vehicle_count': pending_vehicle_count,
        'tests_today': tests_today,
        'inspections_today': inspections_today,
        'recent_license_applications': recent_license_applications,
        'recent_vehicle_registrations': recent_vehicle_registrations,
        'recent_challans': recent_challans,
        'disputed_challans': disputed_challans,
        'licenses_issued_weekly': licenses_issued_weekly,
        'vehicles_registered_weekly': vehicles_registered_weekly,
        'challans_issued_weekly': challans_issued_weekly,
        'payments_received_weekly': payments_received_weekly,
    }
    
    return render(request, 'dashboard/officer_dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def admin_dashboard(request):
    """Dashboard view for administrators"""
    # Get user statistics
    total_users = User.objects.count()
    total_citizens = User.objects.filter(user_type='CITIZEN').count()
    total_officers = User.objects.filter(user_type='OFFICER').count()
    total_admins = User.objects.filter(user_type='ADMIN').count()
    
    # Get application statistics
    total_license_applications = LicenseApplication.objects.count()
    total_licenses_issued = DrivingLicense.objects.count()
    
    total_vehicle_registrations = VehicleRegistration.objects.count()
    total_vehicles_registered = RegisteredVehicle.objects.count()
    
    total_challans = Challan.objects.count()
    total_challan_revenue = ChallanPayment.objects.aggregate(total=Sum('amount'))['total'] or 0
    
    # Get monthly statistics
    current_year = timezone.now().year
    current_month = timezone.now().month
    
    monthly_licenses = []
    monthly_vehicles = []
    monthly_challans = []
    monthly_revenue = []
    
    for month in range(1, 13):
        # Licenses issued in this month
        month_licenses = DrivingLicense.objects.filter(
            issued_date__year=current_year,
            issued_date__month=month
        ).count()
        monthly_licenses.append(month_licenses)
        
        # Vehicles registered in this month
        month_vehicles = RegisteredVehicle.objects.filter(
            registration__registration_date__year=current_year,
            registration__registration_date__month=month
        ).count()
        monthly_vehicles.append(month_vehicles)
        
        # Challans issued in this month
        month_challans = Challan.objects.filter(
            issue_date__year=current_year,
            issue_date__month=month
        ).count()
        monthly_challans.append(month_challans)
        
        # Revenue in this month
        month_revenue = ChallanPayment.objects.filter(
            payment_date__year=current_year,
            payment_date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_revenue.append(float(month_revenue))
    
    # Get pending actions requiring admin attention
    pending_officer_registrations = User.objects.filter(
        user_type='OFFICER',
        is_active=False
    ).count()
    
    # Get recent activities
    recent_license_applications = LicenseApplication.objects.order_by('-application_date')[:5]
    recent_vehicle_registrations = VehicleRegistration.objects.order_by('-application_date')[:5]
    recent_challans = Challan.objects.order_by('-issue_date')[:5]
    
    context = {
        'total_users': total_users,
        'total_citizens': total_citizens,
        'total_officers': total_officers,
        'total_admins': total_admins,
        'total_license_applications': total_license_applications,
        'total_licenses_issued': total_licenses_issued,
        'total_vehicle_registrations': total_vehicle_registrations,
        'total_vehicles_registered': total_vehicles_registered,
        'total_challans': total_challans,
        'total_challan_revenue': total_challan_revenue,
        'monthly_licenses': monthly_licenses,
        'monthly_vehicles': monthly_vehicles,
        'monthly_challans': monthly_challans,
        'monthly_revenue': monthly_revenue,
        'pending_officer_registrations': pending_officer_registrations,
        'recent_license_applications': recent_license_applications,
        'recent_vehicle_registrations': recent_vehicle_registrations,
        'recent_challans': recent_challans,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def check_application_status(request, application_type, application_number):
    """View to check status of an application (AJAX or direct view)"""
    try:
        if application_type == 'license':
            application = LicenseApplication.objects.get(application_number=application_number)
            
            # Check if user is allowed to view this application
            if request.user.user_type == 'CITIZEN' and application.applicant != request.user:
                return JsonResponse({'error': 'You do not have permission to view this application'}, status=403)
            
            data = {
                'application_number': application.application_number,
                'applicant_name': application.applicant.get_full_name(),
                'application_type': application.get_application_type_display(),
                'license_type': application.license_type.name,
                'application_date': application.application_date.strftime('%d-%m-%Y'),
                'current_status': application.get_status_display(),
                'payment_status': 'Paid' if application.payment_status else 'Pending',
            }
            
            # Add test details if available
            test_schedules = TestSchedule.objects.filter(application=application).order_by('-scheduled_date')
            if test_schedules.exists():
                latest_test = test_schedules.first()
                data['test_type'] = latest_test.get_test_type_display()
                data['test_date'] = latest_test.scheduled_date.strftime('%d-%m-%Y %H:%M')
                data['test_venue'] = latest_test.venue
                data['test_completed'] = latest_test.is_completed
                if latest_test.is_completed:
                    data['test_result'] = 'Passed' if latest_test.passed else 'Failed'
            
            # Add license details if issued
            try:
                license = application.issued_license
                data['license_number'] = license.license_number
                data['issued_date'] = license.issued_date.strftime('%d-%m-%Y')
                data['valid_until'] = license.valid_until.strftime('%d-%m-%Y')
            except DrivingLicense.DoesNotExist:
                pass
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'data': data})
            
            return render(request, 'license/status.html', {'application': application, 'data': data})
        
        elif application_type == 'vehicle':
            registration = VehicleRegistration.objects.get(
                Q(temporary_number=application_number) | Q(registration_number=application_number)
            )
            
            # Check if user is allowed to view this registration
            if request.user.user_type == 'CITIZEN' and registration.owner != request.user:
                return JsonResponse({'error': 'You do not have permission to view this registration'}, status=403)
            
            data = {
                'application_number': registration.temporary_number,
                'registration_number': registration.registration_number,
                'owner_name': registration.owner.get_full_name(),
                'registration_type': registration.get_registration_type_display(),
                'vehicle_category': registration.vehicle_category.name,
                'make_model': f"{registration.make} {registration.model}",
                'application_date': registration.application_date.strftime('%d-%m-%Y'),
                'current_status': registration.get_status_display(),
                'payment_status': 'Paid' if registration.payment_status else 'Pending',
            }
            
            # Add inspection details if available
            inspections = VehicleInspection.objects.filter(registration=registration).order_by('-scheduled_date')
            if inspections.exists():
                latest_inspection = inspections.first()
                data['inspection_date'] = latest_inspection.scheduled_date.strftime('%d-%m-%Y %H:%M')
                data['inspection_venue'] = latest_inspection.venue
                data['inspection_completed'] = latest_inspection.is_completed
                if latest_inspection.is_completed:
                    data['inspection_result'] = 'Passed' if latest_inspection.passed else 'Failed'
            
            # Add registration details if registered
            if registration.status == 'REGISTERED':
                data['registration_date'] = registration.registration_date.strftime('%d-%m-%Y')
                data['valid_until'] = registration.valid_until.strftime('%d-%m-%Y')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'data': data})
            
            return render(request, 'vehicle/status.html', {'registration': registration, 'data': data})
        
        else:
            return JsonResponse({'error': 'Invalid application type'}, status=400)
        
    except (LicenseApplication.DoesNotExist, VehicleRegistration.DoesNotExist):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Application not found'}, status=404)
        
        error_message = f"No {application_type} application found with number {application_number}"
        return render(request, 'error.html', {'error_message': error_message})
