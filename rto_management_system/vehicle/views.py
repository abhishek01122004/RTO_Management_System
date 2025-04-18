import random
import string
import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count, Q, Sum
from django.utils import timezone

from .models import (VehicleClass, VehicleMaker, VehicleModel, 
                    RegistrationApplication, VehicleRegistration, VehicleTransfer,
                    FUEL_TYPES, VEHICLE_TYPES)
from accounts.models import User

# Try to import from notifications app, but fall back to local implementation if not available
try:
    from notifications.utils import send_notification, send_email, send_sms
except ImportError:
    # Mock implementation for local testing
    def send_notification(user, title, message, notification_type):
        print(f"Notification to {user.email}: {title} - {message} ({notification_type})")
        
    def send_email(to_email, subject, message):
        print(f"Email to {to_email}: {subject} - {message}")
        
    def send_sms(phone_number, message):
        print(f"SMS to {phone_number}: {message}")


# Helper functions
def generate_application_number():
    """Generate a unique application number for vehicle registration"""
    prefix = "VR"
    date_str = timezone.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{date_str}{random_str}"


# Citizen views
@login_required
def vehicle_dashboard(request):
    """Dashboard view for citizen's vehicles"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Access denied.")
        return redirect('home')
    
    # Get user's vehicles and applications
    vehicles = VehicleRegistration.objects.filter(owner=request.user).order_by('-registered_date')
    applications = RegistrationApplication.objects.filter(applicant=request.user).order_by('-application_date')
    transfers_as_seller = VehicleTransfer.objects.filter(current_owner=request.user).order_by('-application_date')
    transfers_as_buyer = VehicleTransfer.objects.filter(new_owner=request.user).order_by('-application_date')
    
    # Calculate statistics
    total_vehicles = vehicles.count()
    pending_applications = applications.filter(status__in=['PENDING', 'DOCUMENT_VERIFICATION', 'INSPECTION_SCHEDULED']).count()
    vehicles_expiring_soon = vehicles.filter(
        expiry_date__lte=timezone.now().date() + datetime.timedelta(days=90),
        is_active=True
    ).count()
    
    context = {
        'total_vehicles': total_vehicles,
        'pending_applications': pending_applications,
        'vehicles_expiring_soon': vehicles_expiring_soon,
        'vehicles': vehicles[:5],  # Show only the 5 most recent
        'applications': applications[:5],
        'transfers_as_seller': transfers_as_seller[:3],
        'transfers_as_buyer': transfers_as_buyer[:3]
    }
    
    return render(request, 'vehicle/dashboard.html', context)


@login_required
def my_vehicles(request):
    """View for citizens to see their vehicles"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Access denied.")
        return redirect('home')
    
    vehicles = VehicleRegistration.objects.filter(owner=request.user).order_by('-registered_date')
    
    return render(request, 'vehicle/my_vehicles.html', {'vehicles': vehicles})


@login_required
def vehicle_detail(request, registration_number):
    """View to see details of a specific vehicle"""
    vehicle = get_object_or_404(VehicleRegistration, registration_number=registration_number)
    
    # Check permissions
    if request.user.user_type == 'CITIZEN' and vehicle.owner != request.user:
        messages.error(request, "You don't have permission to view this vehicle.")
        return redirect('home')
    
    # Get transfer history
    transfers = VehicleTransfer.objects.filter(vehicle=vehicle).order_by('-application_date')
    
    return render(request, 'vehicle/vehicle_detail.html', {
        'vehicle': vehicle,
        'transfers': transfers
    })


@login_required
def apply_for_registration(request):
    """View for citizens to apply for vehicle registration"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Only citizens can apply for vehicle registration.")
        return redirect('home')
    
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented in a separate step with the form
        pass
    else:
        # Prepare context for GET request
        vehicle_classes = VehicleClass.objects.filter(is_active=True)
        vehicle_makers = VehicleMaker.objects.filter(is_active=True)
        context = {
            'vehicle_classes': vehicle_classes,
            'vehicle_makers': vehicle_makers,
        }
    
    return render(request, 'vehicle/apply.html', context)


@login_required
def my_registration_applications(request):
    """View for citizens to see their vehicle registration applications"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Access denied.")
        return redirect('home')
    
    applications = RegistrationApplication.objects.filter(applicant=request.user).order_by('-application_date')
    
    return render(request, 'vehicle/my_applications.html', {'applications': applications})


@login_required
def registration_application_detail(request, application_number):
    """View to see details of a specific registration application"""
    application = get_object_or_404(RegistrationApplication, application_number=application_number)
    
    # Check permissions
    if request.user.user_type == 'CITIZEN' and application.applicant != request.user:
        messages.error(request, "You don't have permission to view this application.")
        return redirect('home')
    
    return render(request, 'vehicle/application_detail.html', {'application': application})


@login_required
def vehicle_transfers(request):
    """View for citizens to see their vehicle transfers"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Access denied.")
        return redirect('home')
    
    transfers_as_seller = VehicleTransfer.objects.filter(current_owner=request.user).order_by('-application_date')
    transfers_as_buyer = VehicleTransfer.objects.filter(new_owner=request.user).order_by('-application_date')
    
    return render(request, 'vehicle/transfers.html', {
        'transfers_as_seller': transfers_as_seller,
        'transfers_as_buyer': transfers_as_buyer
    })


@login_required
def transfer_vehicle(request, registration_number):
    """View for initiating vehicle ownership transfer"""
    vehicle = get_object_or_404(VehicleRegistration, registration_number=registration_number)
    
    # Check if user is the owner
    if vehicle.owner != request.user:
        messages.error(request, "You are not authorized to transfer this vehicle.")
        return redirect('my_vehicles')
    
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented in a separate step with the form
        pass
    else:
        # Prepare context for GET request
        context = {
            'vehicle': vehicle,
        }
    
    return render(request, 'vehicle/transfer.html', context)


# Officer views
@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def review_registration_applications(request):
    """View for officers to review vehicle registration applications"""
    status_filter = request.GET.get('status', '')
    
    if status_filter:
        applications = RegistrationApplication.objects.filter(
            status=status_filter,
            payment_status=True
        ).order_by('-application_date')
    else:
        applications = RegistrationApplication.objects.filter(
            payment_status=True
        ).order_by('-application_date')
    
    return render(request, 'vehicle/review_applications.html', {
        'applications': applications,
        'status_filter': status_filter
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def review_registration_application(request, application_number):
    """View for officers to review a specific registration application"""
    application = get_object_or_404(RegistrationApplication, application_number=application_number)
    
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented in a separate step with the form
        pass
    else:
        # Prepare context for GET request
        context = {
            'application': application,
        }
    
    return render(request, 'vehicle/review.html', context)


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def schedule_inspection(request, application_number):
    """View for scheduling a vehicle inspection"""
    application = get_object_or_404(RegistrationApplication, application_number=application_number)
    
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented in a separate step with the form
        pass
    else:
        # Prepare context for GET request
        context = {
            'application': application,
        }
    
    return render(request, 'vehicle/schedule_inspection.html', context)


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def record_inspection_result(request, application_number):
    """View for recording vehicle inspection results"""
    application = get_object_or_404(RegistrationApplication, application_number=application_number)
    
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented in a separate step with the form
        pass
    else:
        # Prepare context for GET request
        context = {
            'application': application,
        }
    
    return render(request, 'vehicle/record_inspection.html', context)


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def issue_registration(request, application_number):
    """View for issuing a vehicle registration"""
    application = get_object_or_404(RegistrationApplication, application_number=application_number)
    
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented in a separate step with the form
        pass
    else:
        # Prepare context for GET request
        context = {
            'application': application,
        }
    
    return render(request, 'vehicle/issue_registration.html', context)


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def review_transfer_applications(request):
    """View for officers to review vehicle transfer applications"""
    status_filter = request.GET.get('status', '')
    
    if status_filter:
        transfers = VehicleTransfer.objects.filter(
            status=status_filter,
            payment_status=True
        ).order_by('-application_date')
    else:
        transfers = VehicleTransfer.objects.filter(
            payment_status=True
        ).order_by('-application_date')
    
    return render(request, 'vehicle/review_transfers.html', {
        'transfers': transfers,
        'status_filter': status_filter
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def review_transfer(request, transfer_id):
    """View for officers to review a specific vehicle transfer"""
    transfer = get_object_or_404(VehicleTransfer, id=transfer_id)
    
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented in a separate step with the form
        pass
    else:
        # Prepare context for GET request
        context = {
            'transfer': transfer,
        }
    
    return render(request, 'vehicle/review_transfer.html', context)


# Admin views
@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def vehicle_classes(request):
    """View to manage vehicle classes"""
    classes = VehicleClass.objects.all().order_by('name')
    
    return render(request, 'vehicle/classes.html', {'classes': classes})


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def add_vehicle_class(request):
    """View to add a new vehicle class"""
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented in a separate step with the form
        pass
    else:
        # Prepare context for GET request
        context = {}
    
    return render(request, 'vehicle/add_class.html', context)


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def edit_vehicle_class(request, class_id):
    """View to edit a vehicle class"""
    vehicle_class = get_object_or_404(VehicleClass, id=class_id)
    
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented in a separate step with the form
        pass
    else:
        # Prepare context for GET request
        context = {
            'vehicle_class': vehicle_class
        }
    
    return render(request, 'vehicle/edit_class.html', context)


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def vehicle_makers(request):
    """View to manage vehicle makers"""
    makers = VehicleMaker.objects.all().order_by('name')
    
    return render(request, 'vehicle/makers.html', {'makers': makers})


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def add_vehicle_maker(request):
    """View to add a new vehicle maker"""
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented in a separate step with the form
        pass
    else:
        # Prepare context for GET request
        context = {}
    
    return render(request, 'vehicle/add_maker.html', context)


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def edit_vehicle_maker(request, maker_id):
    """View to edit a vehicle maker"""
    maker = get_object_or_404(VehicleMaker, id=maker_id)
    
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented in a separate step with the form
        pass
    else:
        # Prepare context for GET request
        context = {
            'maker': maker
        }
    
    return render(request, 'vehicle/edit_maker.html', context)


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def vehicle_models(request):
    """View to manage vehicle models"""
    maker_filter = request.GET.get('maker', '')
    
    if maker_filter:
        models = VehicleModel.objects.filter(maker_id=maker_filter).order_by('name')
    else:
        models = VehicleModel.objects.all().order_by('maker__name', 'name')
    
    makers = VehicleMaker.objects.all().order_by('name')
    
    return render(request, 'vehicle/models.html', {
        'models': models,
        'makers': makers,
        'maker_filter': maker_filter
    })


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def add_vehicle_model(request):
    """View to add a new vehicle model"""
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented in a separate step with the form
        pass
    else:
        # Prepare context for GET request
        makers = VehicleMaker.objects.filter(is_active=True).order_by('name')
        context = {
            'makers': makers,
            'fuel_types': FUEL_TYPES,
            'vehicle_types': VEHICLE_TYPES
        }
    
    return render(request, 'vehicle/add_model.html', context)


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def edit_vehicle_model(request, model_id):
    """View to edit a vehicle model"""
    vehicle_model = get_object_or_404(VehicleModel, id=model_id)
    
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented in a separate step with the form
        pass
    else:
        # Prepare context for GET request
        makers = VehicleMaker.objects.filter(is_active=True).order_by('name')
        context = {
            'vehicle_model': vehicle_model,
            'makers': makers,
            'fuel_types': FUEL_TYPES,
            'vehicle_types': VEHICLE_TYPES
        }
    
    return render(request, 'vehicle/edit_model.html', context)


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def vehicle_statistics(request):
    """View to show vehicle registration statistics"""
    # Get date range filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base queryset
    registrations_qs = VehicleRegistration.objects.all()
    applications_qs = RegistrationApplication.objects.all()
    transfers_qs = VehicleTransfer.objects.all()
    
    # Apply date filters if provided
    if start_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        registrations_qs = registrations_qs.filter(registered_date__gte=start_date)
        applications_qs = applications_qs.filter(application_date__gte=start_date)
        transfers_qs = transfers_qs.filter(application_date__gte=start_date)
    
    if end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        registrations_qs = registrations_qs.filter(registered_date__lte=end_date)
        applications_qs = applications_qs.filter(application_date__lte=end_date)
        transfers_qs = transfers_qs.filter(application_date__lte=end_date)
    
    # Calculate statistics
    total_registrations = registrations_qs.count()
    total_applications = applications_qs.count()
    total_transfers = transfers_qs.count()
    
    # Applications by status
    application_status_counts = applications_qs.values('status').annotate(count=Count('status'))
    
    # Applications by type
    application_type_counts = applications_qs.values('application_type').annotate(count=Count('application_type'))
    
    # Registrations by vehicle class
    class_counts = registrations_qs.values('application__vehicle_class__name').annotate(count=Count('application__vehicle_class'))
    
    # Revenue from registration fees
    total_registration_revenue = applications_qs.filter(payment_status=True).aggregate(
        total=Sum('fee')
    )['total'] or 0
    
    # Revenue from transfer fees
    total_transfer_revenue = transfers_qs.filter(payment_status=True).aggregate(
        total=Sum('transfer_fee')
    )['total'] or 0
    
    # Total revenue
    total_revenue = total_registration_revenue + total_transfer_revenue
    
    context = {
        'total_registrations': total_registrations,
        'total_applications': total_applications,
        'total_transfers': total_transfers,
        'application_status_counts': application_status_counts,
        'application_type_counts': application_type_counts,
        'class_counts': class_counts,
        'total_registration_revenue': total_registration_revenue,
        'total_transfer_revenue': total_transfer_revenue,
        'total_revenue': total_revenue,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'vehicle/statistics.html', context)