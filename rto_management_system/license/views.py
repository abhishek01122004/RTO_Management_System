import random
import string
import datetime

# Try to import razorpay, but provide a mock if not available
try:
    import razorpay
except ImportError:
    # Create a mock Razorpay client for development
    class MockRazorpay:
        class Client:
            def __init__(self, auth):
                self.auth = auth
                self.order = self
                self.utility = self
                print(f"Mock Razorpay initialized with keys: {auth[0][:4]}... and {auth[1][:4]}...")
            
            def create(self, data):
                # Return a mock order object
                order_id = f"order_{random.randint(1000000, 9999999)}"
                print(f"Creating mock Razorpay order: {order_id} for amount {data.get('amount', 0)/100} {data.get('currency', 'INR')}")
                return {
                    'id': order_id,
                    'amount': data.get('amount', 0),
                    'currency': data.get('currency', 'INR'),
                    'receipt': data.get('receipt', ''),
                }
            
            def verify_payment_signature(self, data):
                # Always return True for mock verification
                print(f"Mock verifying payment: {data.get('razorpay_payment_id', '')}")
                return True
    
    # Replace the actual razorpay module with our mock
    razorpay = MockRazorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone

from .models import LicenseType, LicenseApplication, DrivingLicense, TestSchedule
from .forms import (LicenseApplicationForm, LicenseApplicationReviewForm, 
                   TestScheduleForm, TestResultForm)
# Try to import from notifications app, but fall back to local implementation if not available
try:
    from notifications.utils import send_notification, send_email, send_sms
except ImportError:
    from .notifications_utils import send_notification, send_email, send_sms


# Helper functions
def generate_application_number():
    """Generate a unique application number"""
    prefix = "LA"
    date_str = timezone.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{date_str}{random_str}"


def generate_license_number():
    """Generate a unique license number"""
    prefix = "DL"
    date_str = timezone.now().strftime("%Y%m")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{date_str}{random_str}"


# Citizen views
@login_required
def apply_for_license(request):
    """View for citizens to apply for a license"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Only citizens can apply for a license.")
        return redirect('home')
    
    if request.method == 'POST':
        form = LicenseApplicationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.application_number = generate_application_number()
            application.save()
            
            # Send notification
            send_notification(
                user=request.user,
                title="License Application Submitted",
                message=f"Your license application #{application.application_number} has been submitted successfully.",
                notification_type="LICENSE_APPLICATION"
            )
            
            send_email(
                to_email=request.user.email,
                subject="License Application Submitted",
                message=f"Your license application #{application.application_number} has been submitted successfully. "
                        f"You can track your application status in your dashboard."
            )
            
            messages.success(request, "Your license application has been submitted successfully.")
            return redirect('license_application_detail', application_number=application.application_number)
    else:
        form = LicenseApplicationForm(user=request.user)
    
    return render(request, 'license/apply.html', {'form': form})


@login_required
def my_license_applications(request):
    """View for citizens to see their license applications"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Access denied.")
        return redirect('home')
    
    applications = LicenseApplication.objects.filter(applicant=request.user).order_by('-application_date')
    
    return render(request, 'license/my_applications.html', {'applications': applications})


@login_required
def license_application_detail(request, application_number):
    """View to see details of a specific license application"""
    application = get_object_or_404(
        LicenseApplication, 
        application_number=application_number
    )
    
    # Check permissions
    if request.user.user_type == 'CITIZEN' and application.applicant != request.user:
        messages.error(request, "You don't have permission to view this application.")
        return redirect('home')
    
    test_schedules = TestSchedule.objects.filter(application=application).order_by('-scheduled_date')
    
    return render(request, 'license/application_detail.html', {
        'application': application,
        'test_schedules': test_schedules
    })


@login_required
def my_licenses(request):
    """View for citizens to see their driving licenses"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Access denied.")
        return redirect('home')
    
    licenses = DrivingLicense.objects.filter(holder=request.user).order_by('-issued_date')
    
    return render(request, 'license/my_licenses.html', {'licenses': licenses})


@login_required
def license_detail(request, license_number):
    """View to see details of a specific driving license"""
    license = get_object_or_404(DrivingLicense, license_number=license_number)
    
    # Check permissions
    if request.user.user_type == 'CITIZEN' and license.holder != request.user:
        messages.error(request, "You don't have permission to view this license.")
        return redirect('home')
    
    return render(request, 'license/license_detail.html', {'license': license})


@login_required
def license_payment(request, application_number):
    """View for making license application payment"""
    application = get_object_or_404(
        LicenseApplication, 
        application_number=application_number
    )
    
    # Check permissions
    if request.user.user_type == 'CITIZEN' and application.applicant != request.user:
        messages.error(request, "You don't have permission to pay for this application.")
        return redirect('home')
    
    # Check if payment is already done
    if application.payment_status:
        messages.info(request, "Payment has already been completed for this application.")
        return redirect('license_application_detail', application_number=application_number)
    
    # Initialize Razorpay
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Create order
    amount = int(application.license_type.fee * 100)  # Convert to paise
    payment_data = {
        'amount': amount,
        'currency': 'INR',
        'receipt': f'receipt_{application.application_number}',
        'notes': {
            'application_number': application.application_number,
            'applicant_email': application.applicant.email
        }
    }
    
    # Create Razorpay order
    try:
        order = client.order.create(data=payment_data)
        
        context = {
            'application': application,
            'order_id': order['id'],
            'amount': amount / 100,  # Convert back to rupees for display
            'key_id': settings.RAZORPAY_KEY_ID,
            'user_name': f"{request.user.first_name} {request.user.last_name}",
            'user_email': request.user.email,
            'user_phone': request.user.phone_number,
        }
        
        return render(request, 'license/payment.html', context)
    except Exception as e:
        messages.error(request, f"Payment initialization failed: {str(e)}")
        return redirect('license_application_detail', application_number=application_number)


@login_required
def license_payment_success(request, application_number):
    """Handle successful payment for license application"""
    application = get_object_or_404(
        LicenseApplication, 
        application_number=application_number
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
            
            # Update application payment status
            application.payment_status = True
            application.payment_date = timezone.now()
            application.payment_transaction_id = payment_id
            application.save()
            
            # Send notification
            send_notification(
                user=application.applicant,
                title="License Application Payment Successful",
                message=f"Payment for your license application #{application.application_number} has been received.",
                notification_type="PAYMENT"
            )
            
            send_email(
                to_email=application.applicant.email,
                subject="License Application Payment Successful",
                message=f"Your payment for license application #{application.application_number} has been received. "
                        f"Your application is now under review."
            )
            
            messages.success(request, "Payment successful! Your application will be reviewed by an RTO officer.")
            return redirect('license_application_detail', application_number=application_number)
        
        except Exception as e:
            messages.error(request, f"Payment verification failed: {str(e)}")
            return redirect('license_payment', application_number=application_number)
    
    return redirect('license_application_detail', application_number=application_number)


# Officer views
@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def review_license_applications(request):
    """View for officers to review license applications"""
    status_filter = request.GET.get('status', '')
    
    if status_filter:
        applications = LicenseApplication.objects.filter(
            status=status_filter,
            payment_status=True
        ).order_by('-application_date')
    else:
        applications = LicenseApplication.objects.filter(
            payment_status=True
        ).order_by('-application_date')
    
    return render(request, 'license/review_applications.html', {
        'applications': applications,
        'status_filter': status_filter
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def review_license_application(request, application_number):
    """View for officers to review a specific license application"""
    application = get_object_or_404(
        LicenseApplication, 
        application_number=application_number
    )
    
    if request.method == 'POST':
        form = LicenseApplicationReviewForm(request.POST, instance=application)
        if form.is_valid():
            updated_application = form.save(commit=False)
            updated_application.reviewed_by = request.user
            updated_application.save()
            
            # Send notification
            send_notification(
                user=application.applicant,
                title="License Application Status Updated",
                message=f"Your license application #{application.application_number} status has been updated to {application.get_status_display()}.",
                notification_type="APPLICATION_STATUS"
            )
            
            send_email(
                to_email=application.applicant.email,
                subject="License Application Status Updated",
                message=f"Your license application #{application.application_number} status has been updated to {application.get_status_display()}. "
                        f"Please check your dashboard for more details."
            )
            
            if application.status == 'REJECTED':
                rejection_reason = application.rejection_reason or "No specific reason provided"
                send_email(
                    to_email=application.applicant.email,
                    subject="License Application Rejected",
                    message=f"Your license application #{application.application_number} has been rejected. "
                            f"Reason: {rejection_reason}. "
                            f"Please contact the RTO office for more information."
                )
            
            messages.success(request, f"Application status updated to {application.get_status_display()}.")
            return redirect('review_license_applications')
    else:
        form = LicenseApplicationReviewForm(instance=application)
    
    test_schedules = TestSchedule.objects.filter(application=application).order_by('-scheduled_date')
    
    return render(request, 'license/review.html', {
        'application': application,
        'form': form,
        'test_schedules': test_schedules
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def schedule_test(request, application_number):
    """View for scheduling a test for a license application"""
    application = get_object_or_404(
        LicenseApplication, 
        application_number=application_number
    )
    
    if request.method == 'POST':
        form = TestScheduleForm(request.POST)
        if form.is_valid():
            test_schedule = form.save(commit=False)
            test_schedule.application = application
            test_schedule.save()
            
            # Update application status
            application.status = 'SCHEDULED_FOR_TEST'
            application.test_date = test_schedule.scheduled_date
            application.save()
            
            # Send notification
            send_notification(
                user=application.applicant,
                title="License Test Scheduled",
                message=f"Your {test_schedule.get_test_type_display()} has been scheduled on {test_schedule.scheduled_date.strftime('%d-%m-%Y %H:%M')} at {test_schedule.venue}.",
                notification_type="TEST_SCHEDULE"
            )
            
            send_email(
                to_email=application.applicant.email,
                subject="License Test Scheduled",
                message=f"Your {test_schedule.get_test_type_display()} for license application #{application.application_number} "
                        f"has been scheduled on {test_schedule.scheduled_date.strftime('%d-%m-%Y %H:%M')} at {test_schedule.venue}. "
                        f"Instructions: {test_schedule.instructions}"
            )
            
            # Send SMS if phone number is available
            if application.applicant.phone_number:
                send_sms(
                    to_number=application.applicant.phone_number,
                    message=f"RTO: Your {test_schedule.get_test_type_display()} is scheduled on "
                            f"{test_schedule.scheduled_date.strftime('%d-%m-%Y %H:%M')} at {test_schedule.venue}."
                )
            
            messages.success(request, "Test scheduled successfully.")
            return redirect('review_license_application', application_number=application_number)
    else:
        form = TestScheduleForm()
    
    return render(request, 'license/schedule_test.html', {
        'application': application,
        'form': form
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def record_test_result(request, test_id):
    """View for recording test results"""
    test = get_object_or_404(TestSchedule, id=test_id)
    application = test.application
    
    if request.method == 'POST':
        form = TestResultForm(request.POST, instance=test)
        if form.is_valid():
            updated_test = form.save(commit=False)
            updated_test.is_completed = True
            updated_test.examiner = request.user
            updated_test.save()
            
            # Update application status based on test result
            if updated_test.passed:
                application.status = 'TEST_PASSED'
                application.test_result = True
                success_message = "Test marked as passed."
                notification_message = "Congratulations! You have passed your driving test."
            else:
                application.status = 'TEST_FAILED'
                application.test_result = False
                success_message = "Test marked as failed."
                notification_message = "You did not pass your driving test. Please contact RTO for rescheduling."
            
            application.save()
            
            # Send notification
            send_notification(
                user=application.applicant,
                title="License Test Result",
                message=notification_message,
                notification_type="TEST_RESULT"
            )
            
            send_email(
                to_email=application.applicant.email,
                subject="License Test Result",
                message=f"{notification_message} "
                        f"Notes from examiner: {updated_test.notes or 'No specific notes provided'}. "
                        f"Please check your dashboard for more details."
            )
            
            messages.success(request, success_message)
            return redirect('review_license_application', application_number=application.application_number)
    else:
        form = TestResultForm(instance=test)
    
    return render(request, 'license/record_test_result.html', {
        'test': test,
        'application': application,
        'form': form
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def issue_license(request, application_number):
    """View for issuing a license after application approval"""
    application = get_object_or_404(
        LicenseApplication, 
        application_number=application_number,
        status='APPROVED'
    )
    
    if request.method == 'POST':
        # Generate license number
        license_number = generate_license_number()
        
        # Calculate validity period
        issued_date = timezone.now().date()
        valid_until = issued_date.replace(year=issued_date.year + application.license_type.validity_years)
        
        # Create driving license
        license = DrivingLicense.objects.create(
            license_number=license_number,
            application=application,
            holder=application.applicant,
            license_type=application.license_type,
            issued_date=issued_date,
            valid_until=valid_until,
            is_active=True
        )
        
        # Update application status
        application.status = 'ISSUED'
        application.issued_date = issued_date
        application.valid_until = valid_until
        application.save()
        
        # Send notification
        send_notification(
            user=application.applicant,
            title="License Issued",
            message=f"Your driving license #{license_number} has been issued and is valid until {valid_until.strftime('%d-%m-%Y')}.",
            notification_type="LICENSE_ISSUED"
        )
        
        send_email(
            to_email=application.applicant.email,
            subject="Your Driving License Has Been Issued",
            message=f"Congratulations! Your driving license #{license_number} has been issued. "
                    f"It is valid from {issued_date.strftime('%d-%m-%Y')} to {valid_until.strftime('%d-%m-%Y')}. "
                    f"You can download your digital license from the dashboard."
        )
        
        # Send SMS if phone number is available
        if application.applicant.phone_number:
            send_sms(
                to_number=application.applicant.phone_number,
                message=f"RTO: Your driving license #{license_number} has been issued and is valid until {valid_until.strftime('%d-%m-%Y')}."
            )
        
        messages.success(request, f"License #{license_number} has been issued successfully.")
        return redirect('review_license_applications')
    
    return render(request, 'license/issue_license.html', {
        'application': application
    })


# Admin views
@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def license_types(request):
    """View to manage license types"""
    license_types = LicenseType.objects.all()
    return render(request, 'license/license_types.html', {'license_types': license_types})


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def add_license_type(request):
    """View to add a new license type"""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description')
        age_requirement = request.POST.get('age_requirement')
        validity_years = request.POST.get('validity_years')
        fee = request.POST.get('fee')
        
        LicenseType.objects.create(
            name=name,
            code=code,
            description=description,
            age_requirement=age_requirement,
            validity_years=validity_years,
            fee=fee
        )
        
        messages.success(request, "License type added successfully.")
        return redirect('license_types')
    
    return render(request, 'license/add_license_type.html')


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def edit_license_type(request, type_id):
    """View to edit a license type"""
    license_type = get_object_or_404(LicenseType, id=type_id)
    
    if request.method == 'POST':
        license_type.name = request.POST.get('name')
        license_type.code = request.POST.get('code')
        license_type.description = request.POST.get('description')
        license_type.age_requirement = request.POST.get('age_requirement')
        license_type.validity_years = request.POST.get('validity_years')
        license_type.fee = request.POST.get('fee')
        license_type.save()
        
        messages.success(request, "License type updated successfully.")
        return redirect('license_types')
    
    return render(request, 'license/edit_license_type.html', {'license_type': license_type})


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def license_statistics(request):
    """View to show license statistics"""
    # Get date range filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base queryset
    applications_qs = LicenseApplication.objects.all()
    licenses_qs = DrivingLicense.objects.all()
    
    # Apply date filters if provided
    if start_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        applications_qs = applications_qs.filter(application_date__gte=start_date)
        licenses_qs = licenses_qs.filter(issued_date__gte=start_date)
    
    if end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        applications_qs = applications_qs.filter(application_date__lte=end_date)
        licenses_qs = licenses_qs.filter(issued_date__lte=end_date)
    
    # Calculate statistics
    total_applications = applications_qs.count()
    total_licenses_issued = licenses_qs.count()
    
    # Applications by status
    status_counts = applications_qs.values('status').annotate(count=Count('status'))
    
    # Applications by type
    type_counts = applications_qs.values('application_type').annotate(count=Count('application_type'))
    
    # Licenses by type
    license_type_counts = licenses_qs.values('license_type__name').annotate(count=Count('license_type'))
    
    # Revenue from license fees
    total_revenue = licenses_qs.aggregate(
        total=models.Sum('application__license_type__fee')
    )['total'] or 0
    
    context = {
        'total_applications': total_applications,
        'total_licenses_issued': total_licenses_issued,
        'status_counts': status_counts,
        'type_counts': type_counts,
        'license_type_counts': license_type_counts,
        'total_revenue': total_revenue,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'license/statistics.html', context)
