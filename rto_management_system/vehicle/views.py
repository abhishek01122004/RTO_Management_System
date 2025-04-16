import random
import string
import datetime
import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone

from .models import VehicleCategory, VehicleRegistration, VehicleInspection, RegisteredVehicle, VehicleTransfer
from .forms import (VehicleRegistrationForm, VehicleRegistrationReviewForm, 
                  VehicleInspectionForm, InspectionResultForm, VehicleTransferForm)
from accounts.models import User
from notifications.utils import send_notification, send_email, send_sms


# Helper functions
def generate_temporary_number():
    """Generate a unique temporary registration number"""
    prefix = "TR"
    date_str = timezone.now().strftime("%y%m%d")
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{date_str}{random_str}"


def generate_registration_number(state_code="KA"):
    """Generate a vehicle registration number"""
    rto_code = "01"  # Can be made dynamic based on RTO office
    series = ''.join(random.choices(string.ascii_uppercase, k=2))
    number = ''.join(random.choices(string.digits, k=4))
    return f"{state_code} {rto_code} {series} {number}"


# Citizen views
@login_required
def register_vehicle(request):
    """View for citizens to register a vehicle"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Only citizens can register vehicles.")
        return redirect('home')
    
    if request.method == 'POST':
        form = VehicleRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.owner = request.user
            registration.temporary_number = generate_temporary_number()
            registration.save()
            
            # Send notification
            send_notification(
                user=request.user,
                title="Vehicle Registration Submitted",
                message=f"Your vehicle registration application #{registration.temporary_number} has been submitted successfully.",
                notification_type="VEHICLE_REGISTRATION"
            )
            
            send_email(
                to_email=request.user.email,
                subject="Vehicle Registration Submitted",
                message=f"Your vehicle registration application #{registration.temporary_number} has been submitted successfully. "
                        f"You can track your application status in your dashboard."
            )
            
            messages.success(request, "Your vehicle registration application has been submitted successfully.")
            return redirect('vehicle_registration_detail', reg_number=registration.temporary_number)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = VehicleRegistrationForm()
    
    return render(request, 'vehicle/register.html', {'form': form})


@login_required
def my_vehicle_registrations(request):
    """View for citizens to see their vehicle registration applications"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Access denied.")
        return redirect('home')
    
    registrations = VehicleRegistration.objects.filter(owner=request.user).order_by('-application_date')
    
    return render(request, 'vehicle/my_registrations.html', {'registrations': registrations})


@login_required
def vehicle_registration_detail(request, reg_number):
    """View to see details of a specific vehicle registration application"""
    registration = get_object_or_404(
        VehicleRegistration, 
        Q(temporary_number=reg_number) | Q(registration_number=reg_number)
    )
    
    # Check permissions
    if request.user.user_type == 'CITIZEN' and registration.owner != request.user:
        messages.error(request, "You don't have permission to view this registration.")
        return redirect('home')
    
    inspections = VehicleInspection.objects.filter(registration=registration).order_by('-scheduled_date')
    
    return render(request, 'vehicle/registration_detail.html', {
        'registration': registration,
        'inspections': inspections
    })


@login_required
def my_vehicles(request):
    """View for citizens to see their registered vehicles"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Access denied.")
        return redirect('home')
    
    # Get vehicle registrations that have been registered
    registrations = VehicleRegistration.objects.filter(
        owner=request.user,
        status='REGISTERED'
    ).select_related('registered_vehicle').order_by('-registration_date')
    
    return render(request, 'vehicle/my_vehicles.html', {'registrations': registrations})


@login_required
def vehicle_detail(request, reg_number):
    """View to see details of a specific registered vehicle"""
    registration = get_object_or_404(
        VehicleRegistration, 
        registration_number=reg_number,
        status='REGISTERED'
    )
    
    # Check permissions
    if request.user.user_type == 'CITIZEN' and registration.owner != request.user:
        messages.error(request, "You don't have permission to view this vehicle.")
        return redirect('home')
    
    try:
        registered_vehicle = registration.registered_vehicle
    except RegisteredVehicle.DoesNotExist:
        messages.error(request, "Vehicle registration details not found.")
        return redirect('my_vehicles')
    
    return render(request, 'vehicle/vehicle_detail.html', {
        'registration': registration,
        'registered_vehicle': registered_vehicle
    })


@login_required
def vehicle_registration_payment(request, reg_number):
    """View for making vehicle registration payment"""
    registration = get_object_or_404(
        VehicleRegistration, 
        Q(temporary_number=reg_number) | Q(registration_number=reg_number)
    )
    
    # Check permissions
    if request.user.user_type == 'CITIZEN' and registration.owner != request.user:
        messages.error(request, "You don't have permission to pay for this registration.")
        return redirect('home')
    
    # Check if payment is already done
    if registration.payment_status:
        messages.info(request, "Payment has already been completed for this registration.")
        return redirect('vehicle_registration_detail', reg_number=reg_number)
    
    # Initialize Razorpay
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Create order
    amount = int(registration.vehicle_category.registration_fee * 100)  # Convert to paise
    payment_data = {
        'amount': amount,
        'currency': 'INR',
        'receipt': f'receipt_{registration.temporary_number}',
        'notes': {
            'registration_number': registration.temporary_number,
            'owner_email': registration.owner.email
        }
    }
    
    # Create Razorpay order
    try:
        order = client.order.create(data=payment_data)
        
        context = {
            'registration': registration,
            'order_id': order['id'],
            'amount': amount / 100,  # Convert back to rupees for display
            'key_id': settings.RAZORPAY_KEY_ID,
            'user_name': f"{request.user.first_name} {request.user.last_name}",
            'user_email': request.user.email,
            'user_phone': request.user.phone_number,
        }
        
        return render(request, 'vehicle/payment.html', context)
    except Exception as e:
        messages.error(request, f"Payment initialization failed: {str(e)}")
        return redirect('vehicle_registration_detail', reg_number=reg_number)


@login_required
def vehicle_registration_payment_success(request, reg_number):
    """Handle successful payment for vehicle registration"""
    registration = get_object_or_404(
        VehicleRegistration, 
        Q(temporary_number=reg_number) | Q(registration_number=reg_number)
    )
    
    # Verify payment with Razorpay
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')
        
        # Verify signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        try:
            client.utility.verify_payment_signature({
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            })
            
            # Update registration payment status
            registration.payment_status = True
            registration.payment_date = timezone.now()
            registration.payment_transaction_id = payment_id
            registration.save()
            
            # Send notification
            send_notification(
                user=registration.owner,
                title="Vehicle Registration Payment Successful",
                message=f"Payment for your vehicle registration application #{registration.temporary_number} has been received.",
                notification_type="PAYMENT"
            )
            
            send_email(
                to_email=registration.owner.email,
                subject="Vehicle Registration Payment Successful",
                message=f"Your payment for vehicle registration application #{registration.temporary_number} has been received. "
                        f"Your application is now under review."
            )
            
            messages.success(request, "Payment successful! Your application will be reviewed by an RTO officer.")
            return redirect('vehicle_registration_detail', reg_number=reg_number)
        
        except Exception as e:
            messages.error(request, f"Payment verification failed: {str(e)}")
            return redirect('vehicle_registration_payment', reg_number=reg_number)
    
    return redirect('vehicle_registration_detail', reg_number=reg_number)


@login_required
def initiate_vehicle_transfer(request, reg_number):
    """View for initiating vehicle ownership transfer"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Only citizens can initiate vehicle transfers.")
        return redirect('home')
    
    registration = get_object_or_404(
        VehicleRegistration, 
        registration_number=reg_number,
        status='REGISTERED',
        owner=request.user
    )
    
    try:
        registered_vehicle = registration.registered_vehicle
    except RegisteredVehicle.DoesNotExist:
        messages.error(request, "Vehicle is not fully registered.")
        return redirect('my_vehicles')
    
    if request.method == 'POST':
        form = VehicleTransferForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if new owner exists
            new_owner_email = form.cleaned_data['new_owner_email']
            try:
                new_owner = User.objects.get(email=new_owner_email, user_type='CITIZEN')
            except User.DoesNotExist:
                messages.error(request, "New owner not found. Please ensure the email is correct and the user is registered.")
                return render(request, 'vehicle/initiate_transfer.html', {'form': form, 'vehicle': registration})
            
            # Create transfer record
            transfer = form.save(commit=False)
            transfer.vehicle = registered_vehicle
            transfer.current_owner = request.user
            transfer.new_owner = new_owner
            transfer.save()
            
            # Send notifications
            send_notification(
                user=request.user,
                title="Vehicle Transfer Initiated",
                message=f"You have initiated the transfer of vehicle {registration.registration_number} to {new_owner.email}.",
                notification_type="VEHICLE_TRANSFER"
            )
            
            send_notification(
                user=new_owner,
                title="Vehicle Transfer Notification",
                message=f"{request.user.get_full_name()} has initiated the transfer of vehicle {registration.registration_number} to you.",
                notification_type="VEHICLE_TRANSFER"
            )
            
            send_email(
                to_email=request.user.email,
                subject="Vehicle Transfer Initiated",
                message=f"You have initiated the transfer of vehicle {registration.registration_number} to {new_owner.email}. "
                        f"Please complete the payment to proceed with the transfer."
            )
            
            send_email(
                to_email=new_owner.email,
                subject="Vehicle Transfer Notification",
                message=f"{request.user.get_full_name()} has initiated the transfer of vehicle {registration.registration_number} to you. "
                        f"You will be notified once the transfer is approved by RTO."
            )
            
            messages.success(request, "Vehicle transfer initiated successfully. Please complete the payment.")
            return redirect('my_vehicle_transfers')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = VehicleTransferForm()
    
    return render(request, 'vehicle/initiate_transfer.html', {
        'form': form,
        'vehicle': registration
    })


@login_required
def my_vehicle_transfers(request):
    """View for citizens to see their vehicle transfers"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Access denied.")
        return redirect('home')
    
    # Get transfers where the user is either the current owner or new owner
    transfers_as_owner = VehicleTransfer.objects.filter(current_owner=request.user)
    transfers_as_buyer = VehicleTransfer.objects.filter(new_owner=request.user)
    
    context = {
        'transfers_as_owner': transfers_as_owner,
        'transfers_as_buyer': transfers_as_buyer
    }
    
    return render(request, 'vehicle/my_transfers.html', context)


# Officer views
@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def review_vehicle_registrations(request):
    """View for officers to review vehicle registration applications"""
    status_filter = request.GET.get('status', '')
    
    if status_filter:
        registrations = VehicleRegistration.objects.filter(
            status=status_filter,
            payment_status=True
        ).order_by('-application_date')
    else:
        registrations = VehicleRegistration.objects.filter(
            payment_status=True
        ).order_by('-application_date')
    
    return render(request, 'vehicle/review_registrations.html', {
        'registrations': registrations,
        'status_filter': status_filter
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def review_vehicle_registration(request, reg_number):
    """View for officers to review a specific vehicle registration application"""
    registration = get_object_or_404(
        VehicleRegistration, 
        Q(temporary_number=reg_number) | Q(registration_number=reg_number)
    )
    
    if request.method == 'POST':
        form = VehicleRegistrationReviewForm(request.POST, instance=registration)
        if form.is_valid():
            updated_registration = form.save(commit=False)
            updated_registration.reviewed_by = request.user
            updated_registration.save()
            
            # Send notification
            send_notification(
                user=registration.owner,
                title="Vehicle Registration Status Updated",
                message=f"Your vehicle registration application #{registration.temporary_number} status has been updated to {registration.get_status_display()}.",
                notification_type="REGISTRATION_STATUS"
            )
            
            send_email(
                to_email=registration.owner.email,
                subject="Vehicle Registration Status Updated",
                message=f"Your vehicle registration application #{registration.temporary_number} status has been updated to {registration.get_status_display()}. "
                        f"Please check your dashboard for more details."
            )
            
            if registration.status == 'REJECTED':
                rejection_reason = registration.rejection_reason or "No specific reason provided"
                send_email(
                    to_email=registration.owner.email,
                    subject="Vehicle Registration Rejected",
                    message=f"Your vehicle registration application #{registration.temporary_number} has been rejected. "
                            f"Reason: {rejection_reason}. "
                            f"Please contact the RTO office for more information."
                )
            
            messages.success(request, f"Registration status updated to {registration.get_status_display()}.")
            return redirect('review_vehicle_registrations')
    else:
        form = VehicleRegistrationReviewForm(instance=registration)
    
    inspections = VehicleInspection.objects.filter(registration=registration).order_by('-scheduled_date')
    
    return render(request, 'vehicle/review.html', {
        'registration': registration,
        'form': form,
        'inspections': inspections
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def schedule_inspection(request, reg_number):
    """View for scheduling a vehicle inspection"""
    registration = get_object_or_404(
        VehicleRegistration, 
        Q(temporary_number=reg_number) | Q(registration_number=reg_number)
    )
    
    if request.method == 'POST':
        form = VehicleInspectionForm(request.POST)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.registration = registration
            inspection.save()
            
            # Update registration status
            registration.status = 'INSPECTION_SCHEDULED'
            registration.inspection_date = inspection.scheduled_date
            registration.save()
            
            # Send notification
            send_notification(
                user=registration.owner,
                title="Vehicle Inspection Scheduled",
                message=f"Your vehicle inspection has been scheduled on {inspection.scheduled_date.strftime('%d-%m-%Y %H:%M')} at {inspection.venue}.",
                notification_type="INSPECTION_SCHEDULE"
            )
            
            send_email(
                to_email=registration.owner.email,
                subject="Vehicle Inspection Scheduled",
                message=f"Your vehicle inspection for registration #{registration.temporary_number} "
                        f"has been scheduled on {inspection.scheduled_date.strftime('%d-%m-%Y %H:%M')} at {inspection.venue}. "
                        f"Instructions: {inspection.instructions}"
            )
            
            # Send SMS if phone number is available
            if registration.owner.phone_number:
                send_sms(
                    to_number=registration.owner.phone_number,
                    message=f"RTO: Your vehicle inspection is scheduled on "
                            f"{inspection.scheduled_date.strftime('%d-%m-%Y %H:%M')} at {inspection.venue}."
                )
            
            messages.success(request, "Inspection scheduled successfully.")
            return redirect('review_vehicle_registration', reg_number=reg_number)
    else:
        form = VehicleInspectionForm()
    
    return render(request, 'vehicle/schedule_inspection.html', {
        'registration': registration,
        'form': form
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def record_inspection_result(request, inspection_id):
    """View for recording inspection results"""
    inspection = get_object_or_404(VehicleInspection, id=inspection_id)
    registration = inspection.registration
    
    if request.method == 'POST':
        form = InspectionResultForm(request.POST, request.FILES, instance=inspection)
        if form.is_valid():
            updated_inspection = form.save(commit=False)
            updated_inspection.is_completed = True
            updated_inspection.inspector = request.user
            updated_inspection.save()
            
            # Update registration status based on inspection result
            if updated_inspection.passed:
                registration.status = 'INSPECTION_PASSED'
                registration.inspection_result = True
                success_message = "Inspection marked as passed."
                notification_message = "Congratulations! Your vehicle has passed the inspection."
            else:
                registration.status = 'INSPECTION_FAILED'
                registration.inspection_result = False
                success_message = "Inspection marked as failed."
                notification_message = "Your vehicle did not pass the inspection. Please check the notes for details."
            
            registration.inspection_notes = updated_inspection.notes
            registration.save()
            
            # Send notification
            send_notification(
                user=registration.owner,
                title="Vehicle Inspection Result",
                message=notification_message,
                notification_type="INSPECTION_RESULT"
            )
            
            send_email(
                to_email=registration.owner.email,
                subject="Vehicle Inspection Result",
                message=f"{notification_message} "
                        f"Notes from inspector: {updated_inspection.notes or 'No specific notes provided'}. "
                        f"Please check your dashboard for more details."
            )
            
            messages.success(request, success_message)
            return redirect('review_vehicle_registration', reg_number=registration.temporary_number or registration.registration_number)
    else:
        form = InspectionResultForm(instance=inspection)
    
    return render(request, 'vehicle/record_inspection_result.html', {
        'inspection': inspection,
        'registration': registration,
        'form': form
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def assign_registration_number(request, reg_number):
    """View for assigning a permanent registration number to a vehicle"""
    registration = get_object_or_404(
        VehicleRegistration, 
        temporary_number=reg_number,
        status='APPROVED'
    )
    
    if request.method == 'POST':
        # Generate or get registration number
        input_reg_number = request.POST.get('registration_number')
        if input_reg_number:
            registration_number = input_reg_number
        else:
            registration_number = generate_registration_number()
        
        # Calculate validity period
        registration_date = timezone.now().date()
        valid_until = registration_date.replace(year=registration_date.year + 15)  # Usually 15 years validity
        
        # Update registration
        registration.registration_number = registration_number
        registration.status = 'REGISTERED'
        registration.registration_date = registration_date
        registration.valid_until = valid_until
        registration.save()
        
        # Create registered vehicle entry
        registered_vehicle = RegisteredVehicle.objects.create(
            registration=registration,
            is_active=True
        )
        
        # Send notification
        send_notification(
            user=registration.owner,
            title="Vehicle Registered Successfully",
            message=f"Your vehicle has been registered with number {registration_number} and is valid until {valid_until.strftime('%d-%m-%Y')}.",
            notification_type="VEHICLE_REGISTERED"
        )
        
        send_email(
            to_email=registration.owner.email,
            subject="Vehicle Registration Completed",
            message=f"Congratulations! Your vehicle has been registered with number {registration_number}. "
                    f"It is valid from {registration_date.strftime('%d-%m-%Y')} to {valid_until.strftime('%d-%m-%Y')}. "
                    f"You can download your registration certificate from the dashboard."
        )
        
        # Send SMS if phone number is available
        if registration.owner.phone_number:
            send_sms(
                to_number=registration.owner.phone_number,
                message=f"RTO: Your vehicle has been registered with number {registration_number} and is valid until {valid_until.strftime('%d-%m-%Y')}."
            )
        
        messages.success(request, f"Vehicle registered successfully with number {registration_number}.")
        return redirect('review_vehicle_registrations')
    
    return render(request, 'vehicle/assign_registration_number.html', {
        'registration': registration
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def review_vehicle_transfers(request):
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
def review_vehicle_transfer(request, transfer_id):
    """View for officers to review a specific vehicle transfer application"""
    transfer = get_object_or_404(VehicleTransfer, id=transfer_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            # Update transfer status
            transfer.status = 'APPROVED'
            transfer.reviewed_by = request.user
            transfer.save()
            
            # Send notifications
            send_notification(
                user=transfer.current_owner,
                title="Vehicle Transfer Approved",
                message=f"Your request to transfer vehicle {transfer.vehicle.registration.registration_number} has been approved.",
                notification_type="TRANSFER_STATUS"
            )
            
            send_notification(
                user=transfer.new_owner,
                title="Vehicle Transfer Approved",
                message=f"Transfer of vehicle {transfer.vehicle.registration.registration_number} to you has been approved.",
                notification_type="TRANSFER_STATUS"
            )
            
            messages.success(request, "Transfer approved successfully.")
            
        elif action == 'complete':
            # Update transfer status
            transfer.status = 'COMPLETED'
            transfer.completion_date = timezone.now().date()
            transfer.save()
            
            # Update vehicle registration
            registration = transfer.vehicle.registration
            registration.owner = transfer.new_owner
            registration.save()
            
            # Send notifications
            send_notification(
                user=transfer.current_owner,
                title="Vehicle Transfer Completed",
                message=f"Your vehicle {registration.registration_number} has been transferred to {transfer.new_owner.email}.",
                notification_type="TRANSFER_STATUS"
            )
            
            send_notification(
                user=transfer.new_owner,
                title="Vehicle Transfer Completed",
                message=f"Vehicle {registration.registration_number} has been transferred to you. You are now the registered owner.",
                notification_type="TRANSFER_STATUS"
            )
            
            # Send emails
            send_email(
                to_email=transfer.current_owner.email,
                subject="Vehicle Transfer Completed",
                message=f"Your vehicle {registration.registration_number} has been transferred to {transfer.new_owner.email}. "
                        f"The transfer process is now complete."
            )
            
            send_email(
                to_email=transfer.new_owner.email,
                subject="Vehicle Transfer Completed",
                message=f"Vehicle {registration.registration_number} has been transferred to you. "
                        f"You are now the registered owner of this vehicle."
            )
            
            messages.success(request, "Transfer completed successfully. Ownership has been transferred.")
            
        elif action == 'reject':
            rejection_reason = request.POST.get('rejection_reason')
            
            # Update transfer status
            transfer.status = 'REJECTED'
            transfer.rejection_reason = rejection_reason
            transfer.reviewed_by = request.user
            transfer.save()
            
            # Send notifications
            send_notification(
                user=transfer.current_owner,
                title="Vehicle Transfer Rejected",
                message=f"Your request to transfer vehicle {transfer.vehicle.registration.registration_number} has been rejected.",
                notification_type="TRANSFER_STATUS"
            )
            
            send_notification(
                user=transfer.new_owner,
                title="Vehicle Transfer Rejected",
                message=f"Transfer of vehicle {transfer.vehicle.registration.registration_number} to you has been rejected.",
                notification_type="TRANSFER_STATUS"
            )
            
            # Send emails with rejection reason
            send_email(
                to_email=transfer.current_owner.email,
                subject="Vehicle Transfer Rejected",
                message=f"Your request to transfer vehicle {transfer.vehicle.registration.registration_number} has been rejected. "
                        f"Reason: {rejection_reason or 'No specific reason provided'}. "
                        f"Please contact the RTO office for more information."
            )
            
            messages.success(request, "Transfer rejected successfully.")
        
        return redirect('review_vehicle_transfers')
    
    return render(request, 'vehicle/review_transfer.html', {
        'transfer': transfer
    })


# Admin views
@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def vehicle_categories(request):
    """View to manage vehicle categories"""
    categories = VehicleCategory.objects.all()
    return render(request, 'vehicle/categories.html', {'categories': categories})


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def add_vehicle_category(request):
    """View to add a new vehicle category"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        registration_fee = request.POST.get('registration_fee')
        
        VehicleCategory.objects.create(
            name=name,
            description=description,
            registration_fee=registration_fee
        )
        
        messages.success(request, "Vehicle category added successfully.")
        return redirect('vehicle_categories')
    
    return render(request, 'vehicle/add_category.html')


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def edit_vehicle_category(request, category_id):
    """View to edit a vehicle category"""
    category = get_object_or_404(VehicleCategory, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.registration_fee = request.POST.get('registration_fee')
        category.save()
        
        messages.success(request, "Vehicle category updated successfully.")
        return redirect('vehicle_categories')
    
    return render(request, 'vehicle/edit_category.html', {'category': category})


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def vehicle_statistics(request):
    """View to show vehicle statistics"""
    # Get date range filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base queryset
    registrations_qs = VehicleRegistration.objects.all()
    transfers_qs = VehicleTransfer.objects.all()
    
    # Apply date filters if provided
    if start_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        registrations_qs = registrations_qs.filter(application_date__gte=start_date)
        transfers_qs = transfers_qs.filter(application_date__gte=start_date)
    
    if end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        registrations_qs = registrations_qs.filter(application_date__lte=end_date)
        transfers_qs = transfers_qs.filter(application_date__lte=end_date)
    
    # Calculate statistics
    total_registrations = registrations_qs.count()
    total_registered_vehicles = registrations_qs.filter(status='REGISTERED').count()
    
    # Registrations by status
    status_counts = registrations_qs.values('status').annotate(count=Count('status'))
    
    # Registrations by type
    type_counts = registrations_qs.values('registration_type').annotate(count=Count('registration_type'))
    
    # Registrations by vehicle category
    category_counts = registrations_qs.values('vehicle_category__name').annotate(count=Count('vehicle_category'))
    
    # Transfer statistics
    total_transfers = transfers_qs.count()
    completed_transfers = transfers_qs.filter(status='COMPLETED').count()
    
    # Revenue from registration fees
    total_revenue = registrations_qs.filter(status='REGISTERED').aggregate(
        total=models.Sum('vehicle_category__registration_fee')
    )['total'] or 0
    
    context = {
        'total_registrations': total_registrations,
        'total_registered_vehicles': total_registered_vehicles,
        'status_counts': status_counts,
        'type_counts': type_counts,
        'category_counts': category_counts,
        'total_transfers': total_transfers,
        'completed_transfers': completed_transfers,
        'total_revenue': total_revenue,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'vehicle/statistics.html', context)
