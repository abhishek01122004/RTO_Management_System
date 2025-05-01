from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import PermissionDenied
from .models import Vehicle, RegistrationApplication, VehicleDocument, VehicleTransfer, VehicleModel, VehicleCategory, VehicleMake
from .forms import (
    VehicleRegistrationForm, VehicleDocumentForm,
    VehicleTransferForm, VehicleReviewForm, TransferReviewForm, VehicleForm
)
import random
import string
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db import models

def generate_application_number():
    prefix = 'REG'
    timestamp = timezone.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{timestamp}{random_str}"

def generate_transfer_number():
    prefix = 'TRF'
    timestamp = timezone.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{timestamp}{random_str}"

def is_citizen(user):
    return user.user_type == 'CITIZEN'

def is_officer(user):
    return user.user_type == 'OFFICER'

def is_admin(user):
    return user.user_type == 'ADMIN'

@login_required
def vehicle_dashboard(request):
    if is_citizen(request.user):
        vehicles = Vehicle.objects.filter(owner=request.user)
        applications = RegistrationApplication.objects.filter(applicant=request.user)
        transfers = VehicleTransfer.objects.filter(seller=request.user)
    elif is_officer(request.user):
        vehicles = Vehicle.objects.all()
        applications = RegistrationApplication.objects.filter(status='SUBMITTED')
        transfers = VehicleTransfer.objects.filter(status='PENDING')
    else:
        vehicles = Vehicle.objects.all()
        applications = RegistrationApplication.objects.all()
        transfers = VehicleTransfer.objects.all()
        
    context = {
        'vehicles': vehicles[:5],
        'applications': applications[:5],
        'transfers': transfers[:5],
    }
    return render(request, 'vehicle/dashboard.html', context)

@login_required
@user_passes_test(is_citizen)
def register_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                vehicle = form.save(commit=False)
                vehicle.owner = request.user
                vehicle.status = 'PENDING'
                vehicle.save()
                
                application = RegistrationApplication.objects.create(
                    applicant=request.user,
                    vehicle=vehicle,
                    application_number=generate_application_number(),
                    status='DRAFT'
                )
                
                messages.success(request, 'Vehicle registration application created successfully.')
                return redirect('vehicle:vehicle_application_detail', application_id=application.id)
    else:
        form = VehicleForm()
        
    return render(request, 'vehicle/register.html', {'form': form})

@login_required
def vehicle_application_detail(request, application_id):
    application = get_object_or_404(RegistrationApplication, id=application_id)
    
    if not (application.applicant == request.user or is_officer(request.user) or is_admin(request.user)):
        raise PermissionDenied
        
    if request.method == 'POST' and application.status == 'DRAFT':
        form = VehicleDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.application = application
            document.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('vehicle:vehicle_application_detail', application_id=application.id)
    else:
        form = VehicleDocumentForm()
        
    context = {
        'application': application,
        'form': form,
        'documents': application.documents.all(),
    }
    return render(request, 'vehicle/application_detail.html', context)

@login_required
@user_passes_test(is_citizen)
def submit_application(request, application_id):
    application = get_object_or_404(RegistrationApplication, id=application_id, applicant=request.user)
    
    if application.status != 'DRAFT':
        messages.error(request, 'Application has already been submitted.')
        return redirect('vehicle:vehicle_application_detail', application_id=application.id)
        
    if not application.documents.exists():
        messages.error(request, 'Please upload at least one document before submitting.')
        return redirect('vehicle:vehicle_application_detail', application_id=application.id)
        
    application.status = 'SUBMITTED'
    application.submitted_at = timezone.now()
    application.save()
    
    messages.success(request, 'Application submitted successfully.')
    return redirect('vehicle:vehicle_application_detail', application_id=application.id)

@login_required
@user_passes_test(is_officer)
def review_application(request, application_id):
    application = get_object_or_404(RegistrationApplication, id=application_id)
    
    if request.method == 'POST':
        form = VehicleReviewForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save(commit=False)
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            
            if application.status == 'APPROVED':
                application.vehicle.status = 'ACTIVE'
                application.vehicle.save()
                
            messages.success(request, 'Application reviewed successfully.')
            return redirect('vehicle:vehicle_application_detail', application_id=application.id)
    else:
        form = VehicleReviewForm(instance=application)
        
    context = {
        'application': application,
        'form': form,
        'documents': application.documents.all(),
    }
    return render(request, 'vehicle/review_application.html', context)

@login_required
def my_vehicles(request):
    try:
        # Get vehicles owned by the user
        vehicles = Vehicle.objects.filter(owner=request.user)
        
        # For citizens, exclude vehicles that were transferred to someone else
        if is_citizen(request.user):
            vehicles = vehicles.exclude(
                vehicletransfer__status='APPROVED',
                vehicletransfer__seller=request.user
            )
        
        now = timezone.now().date()
        
        # Update status for all vehicles
        for vehicle in vehicles:
            if vehicle.expiry_date and vehicle.expiry_date < now:
                if vehicle.status != 'EXPIRED':
                    vehicle.status = 'EXPIRED'
                    vehicle.save()
        
        context = {
            'vehicles': vehicles,
            'now': now
        }
        return render(request, 'vehicle/my_vehicles.html', context)
    except Exception as e:
        # Log the error for debugging
        print(f"Error in my_vehicles view: {str(e)}")
        # Return a proper error page or redirect
        return render(request, 'vehicle/my_vehicles.html', {'vehicles': []})

@login_required
def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if not (vehicle.owner == request.user or is_officer(request.user) or is_admin(request.user)):
        raise PermissionDenied
        
    return render(request, 'vehicle/vehicle_detail.html', {'vehicle': vehicle})

@login_required
@user_passes_test(is_citizen)
def transfer_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    
    if request.method == 'POST':
        form = VehicleTransferForm(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.vehicle = vehicle
            transfer.seller = request.user
            transfer.transfer_number = generate_transfer_number()
            transfer.save()
            
            messages.success(request, 'Transfer request submitted successfully.')
            return redirect('vehicle:vehicle_detail', vehicle_id=vehicle.id)
    else:
        form = VehicleTransferForm()
        
    return render(request, 'vehicle/transfer.html', {'form': form, 'vehicle': vehicle})

@login_required
@user_passes_test(is_officer)
def review_transfer(request, transfer_id):
    transfer = get_object_or_404(VehicleTransfer, id=transfer_id)
    
    if request.method == 'POST':
        form = TransferReviewForm(request.POST, instance=transfer)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.reviewed_by = request.user
            transfer.reviewed_at = timezone.now()
            
            if transfer.status == 'APPROVED':
                # Update vehicle ownership and status
                transfer.vehicle.owner = transfer.buyer
                transfer.vehicle.status = 'TRANSFERRED'  # Explicitly set status to TRANSFERRED
                transfer.vehicle.save()
                
            transfer.save()
            
            messages.success(request, 'Transfer reviewed successfully.')
            return redirect('vehicle:vehicle_transfers')
    else:
        form = TransferReviewForm(instance=transfer)
        
    return render(request, 'vehicle/review_transfer.html', {'form': form, 'transfer': transfer})

@login_required
def vehicle_transfers(request):
    """View for listing vehicle transfers based on user role."""
    if is_officer(request.user):
        # For officers, show all pending transfers
        transfers = VehicleTransfer.objects.filter(status='PENDING').order_by('-created_at')
        return render(request, 'vehicle/review_transfers.html', {'transfers': transfers})
    else:
        # For citizens, show their transfers
        transfers_sent = VehicleTransfer.objects.filter(seller=request.user)
        transfers_received = VehicleTransfer.objects.filter(buyer=request.user)
        return render(request, 'vehicle/transfers.html', {
            'transfers_sent': transfers_sent,
            'transfers_received': transfers_received,
        })

@require_GET
def get_models(request):
    make_id = request.GET.get('make_id')
    print(f"Make ID received: {make_id}")  # Debug print
    if make_id:
        try:
            models = VehicleModel.objects.filter(make_id=make_id)
            print(f"Models found: {models.count()}")  # Debug print
            for model in models:
                print(f"Model: {model.id} - {model.name}")  # Debug print
            models_list = list(models.values_list('id', 'name'))
            print(f"Models list: {models_list}")  # Debug print
            return JsonResponse(dict(models_list))
        except Exception as e:
            print(f"Error: {str(e)}")  # Debug print
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({})

@login_required
@user_passes_test(is_officer)
def review_registration_applications(request):
    """View for RTO officers to review vehicle registration applications"""
    applications = RegistrationApplication.objects.filter(status='SUBMITTED').order_by('-created_at')
    context = {
        'applications': applications,
    }
    return render(request, 'vehicle/review_applications.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def vehicle_statistics(request):
    """View for displaying vehicle-related statistics"""
    # Get total number of vehicles
    total_vehicles = Vehicle.objects.count()
    
    # Get vehicles by category
    vehicles_by_category = Vehicle.objects.values('category').annotate(count=models.Count('id'))
    
    # Get vehicles by fuel type
    vehicles_by_fuel = Vehicle.objects.values('fuel_type').annotate(count=models.Count('id'))
    
    # Get registration applications by status
    applications_by_status = RegistrationApplication.objects.values('status').annotate(count=models.Count('id'))
    
    # Get recent transfers
    recent_transfers = VehicleTransfer.objects.order_by('-created_at')[:5]
    
    context = {
        'total_vehicles': total_vehicles,
        'vehicles_by_category': vehicles_by_category,
        'vehicles_by_fuel': vehicles_by_fuel,
        'applications_by_status': applications_by_status,
        'recent_transfers': recent_transfers,
    }
    
    return render(request, 'vehicle/statistics.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def vehicle_classes(request):
    """View for displaying and managing vehicle categories."""
    categories = VehicleCategory.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'vehicle/vehicle_classes.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def vehicle_makes(request):
    """View for displaying and managing vehicle makes."""
    makes = VehicleMake.objects.all()
    context = {
        'makes': makes,
    }
    return render(request, 'vehicle/vehicle_makes.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def vehicle_models(request):
    """View for displaying and managing vehicle models."""
    models = VehicleModel.objects.all()
    context = {
        'models': models,
    }
    return render(request, 'vehicle/vehicle_models.html', context) 