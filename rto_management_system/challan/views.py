import datetime
import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.db.models import Count, Sum, Q
from django.utils import timezone

from .models import TrafficRule, ChallanType, Challan, ChallanPayment
from .forms import (ChallanGenerationForm, ChallanSearchForm, 
                   ChallanUpdateForm, ChallanPaymentForm)
from accounts.models import User
from vehicle.models import VehicleRegistration
from notifications.utils import send_notification, send_email, send_sms


@login_required
def search_challan(request):
    """View for searching challans by various parameters"""
    form = ChallanSearchForm(request.GET or None)
    challans = []
    
    if form.is_valid():
        search_type = form.cleaned_data['search_type']
        search_value = form.cleaned_data['search_value']
        
        if search_type == 'challan_number':
            challans = Challan.objects.filter(challan_number__iexact=search_value)
        elif search_type == 'vehicle_number':
            challans = Challan.objects.filter(vehicle_number__iexact=search_value)
        elif search_type == 'license_number':
            challans = Challan.objects.filter(license_number__iexact=search_value)
    
    return render(request, 'challan/search.html', {
        'form': form,
        'challans': challans,
        'search_performed': form.is_valid()
    })


@login_required
def my_challans(request):
    """View for citizens to see their challans"""
    if request.user.user_type != 'CITIZEN':
        messages.error(request, "Access denied.")
        return redirect('home')
    
    # Get challans where user is the violator
    challans = Challan.objects.filter(violator=request.user).order_by('-issue_date')
    
    # Get user's vehicles
    user_vehicles = VehicleRegistration.objects.filter(
        owner=request.user,
        status='REGISTERED'
    ).values_list('registration_number', flat=True)
    
    # Get challans for user's vehicles (even if user is not set as violator)
    vehicle_challans = Challan.objects.filter(
        vehicle_number__in=user_vehicles
    ).exclude(violator=request.user).order_by('-issue_date')
    
    return render(request, 'challan/my_challans.html', {
        'challans': challans,
        'vehicle_challans': vehicle_challans
    })


@login_required
def view_challan(request, challan_number):
    """View to see details of a specific challan"""
    challan = get_object_or_404(Challan, challan_number=challan_number)
    
    # Check permissions
    if request.user.user_type == 'CITIZEN':
        # Citizens can view their own challans or challans for their vehicles
        user_vehicles = VehicleRegistration.objects.filter(
            owner=request.user,
            status='REGISTERED'
        ).values_list('registration_number', flat=True)
        
        is_allowed = (challan.violator == request.user or 
                      challan.vehicle_number in user_vehicles)
        
        if not is_allowed:
            messages.error(request, "You don't have permission to view this challan.")
            return redirect('home')
    
    violated_rules = challan.violation_rules.all()
    
    try:
        payment = challan.payment
    except ChallanPayment.DoesNotExist:
        payment = None
    
    return render(request, 'challan/view.html', {
        'challan': challan,
        'violated_rules': violated_rules,
        'payment': payment
    })


@login_required
def pay_challan(request, challan_number):
    """View for making challan payment"""
    challan = get_object_or_404(Challan, challan_number=challan_number)
    
    # Check if challan is already paid
    if challan.payment_status:
        messages.info(request, "This challan has already been paid.")
        return redirect('view_challan', challan_number=challan_number)
    
    # Check permissions
    if request.user.user_type == 'CITIZEN':
        # Citizens can pay their own challans or challans for their vehicles
        user_vehicles = VehicleRegistration.objects.filter(
            owner=request.user,
            status='REGISTERED'
        ).values_list('registration_number', flat=True)
        
        is_allowed = (challan.violator == request.user or 
                      challan.vehicle_number in user_vehicles)
        
        if not is_allowed:
            messages.error(request, "You don't have permission to pay this challan.")
            return redirect('home')
    
    # Handle POST for development mode direct payment
    if request.method == 'POST' and not settings.RAZORPAY_KEY_ID:
        # Create payment record in development mode
        ChallanPayment.objects.create(
            challan=challan,
            amount=challan.total_amount,
            payment_method='ONLINE',
            transaction_id=f"mock_payment_{timezone.now().strftime('%Y%m%d%H%M%S')}",
            payment_gateway_response="Development mode payment"
        )
        
        # Send notification
        if challan.violator:
            try:
                send_notification(
                    user=challan.violator,
                    title="Challan Payment Successful",
                    message=f"Payment for challan #{challan.challan_number} has been received.",
                    notification_type="PAYMENT"
                )
                
                send_email(
                    to_email=challan.violator.email,
                    subject="Challan Payment Successful",
                    message=f"Your payment for challan #{challan.challan_number} has been received. "
                            f"Thank you for the payment."
                )
            except Exception as e:
                # Continue even if notification fails
                print(f"Notification error: {str(e)}")
        
        messages.success(request, "Development mode: Payment completed successfully.")
        return redirect('view_challan', challan_number=challan_number)
    
    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID or 'rzp_test_mock', settings.RAZORPAY_KEY_SECRET or 'mock_secret'))
    
    # Create order
    amount = int(challan.total_amount * 100)  # Convert to paise
    payment_data = {
        'amount': amount,
        'currency': 'INR',
        'receipt': f'receipt_{challan.challan_number}',
        'notes': {
            'challan_number': challan.challan_number,
            'vehicle_number': challan.vehicle_number
        }
    }
    
    # Check if in development mode without Razorpay keys
    dev_mode = not settings.RAZORPAY_KEY_ID
    
    try:
        # Create Razorpay order if keys are available
        if not dev_mode:
            order = client.order.create(data=payment_data)
            order_id = order['id']
        else:
            # Mock order ID for development
            order_id = f"dev_order_{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        context = {
            'challan': challan,
            'order_id': order_id,
            'amount': amount / 100,  # Convert back to rupees for display
            'key_id': settings.RAZORPAY_KEY_ID,
            'user_name': f"{request.user.first_name} {request.user.last_name}",
            'user_email': request.user.email,
            'user_phone': request.user.phone_number,
            'dev_mode': dev_mode
        }
        
        return render(request, 'challan/pay.html', context)
    except Exception as e:
        messages.error(request, f"Payment initialization failed: {str(e)}")
        return redirect('view_challan', challan_number=challan_number)


@login_required
def challan_payment_success(request, challan_number):
    """Handle successful payment for challan"""
    challan = get_object_or_404(Challan, challan_number=challan_number)
    
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
            
            # Create payment record
            ChallanPayment.objects.create(
                challan=challan,
                amount=challan.total_amount,
                payment_method='ONLINE',
                transaction_id=payment_id,
                payment_gateway_response=f"Order ID: {order_id}, Signature: {signature}"
            )
            
            # Send notification
            if challan.violator:
                send_notification(
                    user=challan.violator,
                    title="Challan Payment Successful",
                    message=f"Payment for challan #{challan.challan_number} has been received.",
                    notification_type="PAYMENT"
                )
                
                send_email(
                    to_email=challan.violator.email,
                    subject="Challan Payment Successful",
                    message=f"Your payment for challan #{challan.challan_number} has been received. "
                            f"Thank you for the payment."
                )
            
            messages.success(request, "Payment successful! Your challan has been marked as paid.")
            return redirect('view_challan', challan_number=challan_number)
        
        except Exception as e:
            messages.error(request, f"Payment verification failed: {str(e)}")
            return redirect('pay_challan', challan_number=challan_number)
    
    return redirect('view_challan', challan_number=challan_number)


@login_required
def dispute_challan(request, challan_number):
    """View for disputing a challan"""
    challan = get_object_or_404(Challan, challan_number=challan_number)
    
    # Check if challan can be disputed
    if challan.status == 'PAID':
        messages.error(request, "Paid challans cannot be disputed.")
        return redirect('view_challan', challan_number=challan_number)
    
    # Check permissions
    if request.user.user_type == 'CITIZEN':
        # Citizens can dispute their own challans or challans for their vehicles
        user_vehicles = VehicleRegistration.objects.filter(
            owner=request.user,
            status='REGISTERED'
        ).values_list('registration_number', flat=True)
        
        is_allowed = (challan.violator == request.user or 
                      challan.vehicle_number in user_vehicles)
        
        if not is_allowed:
            messages.error(request, "You don't have permission to dispute this challan.")
            return redirect('home')
    
    if request.method == 'POST':
        dispute_reason = request.POST.get('dispute_reason', '')
        
        if not dispute_reason:
            messages.error(request, "Please provide a reason for disputing the challan.")
            return render(request, 'challan/dispute.html', {'challan': challan})
        
        # Update challan status
        challan.status = 'DISPUTED'
        challan.remarks = f"Disputed by {request.user.email}. Reason: {dispute_reason}"
        challan.save()
        
        # Send notification to officers
        officers = User.objects.filter(user_type='OFFICER')
        for officer in officers:
            send_notification(
                user=officer,
                title="Challan Disputed",
                message=f"Challan #{challan.challan_number} has been disputed by {request.user.email}.",
                notification_type="CHALLAN_DISPUTE"
            )
        
        # Send confirmation to user
        send_notification(
            user=request.user,
            title="Challan Dispute Submitted",
            message=f"Your dispute for challan #{challan.challan_number} has been submitted successfully.",
            notification_type="CHALLAN_DISPUTE"
        )
        
        send_email(
            to_email=request.user.email,
            subject="Challan Dispute Submitted",
            message=f"Your dispute for challan #{challan.challan_number} has been submitted successfully. "
                    f"An RTO officer will review your dispute and update the status accordingly."
        )
        
        messages.success(request, "Your dispute has been submitted successfully. An RTO officer will review it.")
        return redirect('view_challan', challan_number=challan_number)
    
    return render(request, 'challan/dispute.html', {'challan': challan})


# Officer views
@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def generate_challan(request):
    """View for officers to generate new challans"""
    if request.method == 'POST':
        form = ChallanGenerationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create challan
            challan = form.save(commit=False)
            challan.issued_by = request.user
            
            # Calculate total amount
            selected_rules = form.cleaned_data['selected_rules']
            total_amount = sum(rule.penalty_amount for rule in selected_rules)
            challan.total_amount = total_amount
            
            # Try to find violator by email
            violator_email = form.cleaned_data.get('violator_email')
            violator_phone = form.cleaned_data.get('violator_phone')
            license_number = form.cleaned_data.get('license_number')
            
            if violator_email:
                try:
                    violator = User.objects.get(email=violator_email)
                    challan.violator = violator
                except User.DoesNotExist:
                    pass
            
            if not challan.violator and violator_phone:
                try:
                    violator = User.objects.get(phone_number=violator_phone)
                    challan.violator = violator
                except User.DoesNotExist:
                    pass
            
            # Try to find vehicle owner
            if not challan.violator:
                try:
                    vehicle = VehicleRegistration.objects.get(
                        registration_number=challan.vehicle_number,
                        status='REGISTERED'
                    )
                    challan.violator = vehicle.owner
                except VehicleRegistration.DoesNotExist:
                    pass
            
            # Save challan with license number
            challan.license_number = license_number
            challan.save()
            
            # Add violated rules
            challan.violation_rules.set(selected_rules)
            
            # Send notifications
            if challan.violator:
                send_notification(
                    user=challan.violator,
                    title="New Challan Issued",
                    message=f"A challan #{challan.challan_number} has been issued for vehicle {challan.vehicle_number}.",
                    notification_type="CHALLAN_ISSUED"
                )
                
                send_email(
                    to_email=challan.violator.email,
                    subject="New Traffic Challan Issued",
                    message=f"A challan #{challan.challan_number} has been issued for vehicle {challan.vehicle_number}. "
                            f"Violation: {challan.violation_description}. "
                            f"Total Amount: ₹{challan.total_amount}. "
                            f"Due Date: {challan.due_date.strftime('%d-%m-%Y')}. "
                            f"Please visit the RTO website to pay the challan."
                )
                
                # Send SMS if phone number is available
                if challan.violator.phone_number:
                    send_sms(
                        to_number=challan.violator.phone_number,
                        message=f"RTO: Challan #{challan.challan_number} issued for {challan.vehicle_number}. "
                                f"Amount: ₹{challan.total_amount}. Pay by {challan.due_date.strftime('%d-%m-%Y')}."
                    )
            
            messages.success(request, f"Challan #{challan.challan_number} generated successfully.")
            return redirect('view_challan', challan_number=challan.challan_number)
    else:
        form = ChallanGenerationForm()
    
    traffic_rules = TrafficRule.objects.filter(is_active=True)
    
    return render(request, 'challan/generate.html', {
        'form': form,
        'traffic_rules': traffic_rules
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def manage_challans(request):
    """View for officers to manage challans"""
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    challans = Challan.objects.all()
    
    # Apply filters
    if status_filter:
        challans = challans.filter(status=status_filter)
    
    if date_from:
        try:
            date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            challans = challans.filter(issue_date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            challans = challans.filter(issue_date__lte=date_to)
        except ValueError:
            pass
    
    # Sort by most recent first
    challans = challans.order_by('-issue_date')
    
    return render(request, 'challan/manage.html', {
        'challans': challans,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def update_challan(request, challan_number):
    """View for officers to update a challan"""
    challan = get_object_or_404(Challan, challan_number=challan_number)
    
    if request.method == 'POST':
        form = ChallanUpdateForm(request.POST, instance=challan)
        if form.is_valid():
            updated_challan = form.save()
            
            # Send notification if status changed to CONFIRMED after being DISPUTED
            if updated_challan.status == 'CONFIRMED' and 'DISPUTED' in request.POST.get('original_status', ''):
                if updated_challan.violator:
                    send_notification(
                        user=updated_challan.violator,
                        title="Challan Dispute Resolution",
                        message=f"Your dispute for challan #{challan.challan_number} has been reviewed and the challan has been confirmed.",
                        notification_type="CHALLAN_STATUS"
                    )
                    
                    send_email(
                        to_email=updated_challan.violator.email,
                        subject="Challan Dispute Resolution",
                        message=f"Your dispute for challan #{challan.challan_number} has been reviewed and the challan has been confirmed. "
                                f"Reason: {updated_challan.remarks or 'No specific reason provided'}. "
                                f"Please proceed with the payment to avoid additional penalties."
                    )
            
            # Send notification if status changed to CANCELED
            if updated_challan.status == 'CANCELED':
                if updated_challan.violator:
                    send_notification(
                        user=updated_challan.violator,
                        title="Challan Canceled",
                        message=f"Challan #{challan.challan_number} has been canceled.",
                        notification_type="CHALLAN_STATUS"
                    )
                    
                    send_email(
                        to_email=updated_challan.violator.email,
                        subject="Challan Canceled",
                        message=f"Challan #{challan.challan_number} has been canceled. "
                                f"Reason: {updated_challan.remarks or 'No specific reason provided'}."
                    )
            
            messages.success(request, f"Challan #{challan.challan_number} updated successfully.")
            return redirect('manage_challans')
    else:
        form = ChallanUpdateForm(instance=challan)
    
    violated_rules = challan.violation_rules.all()
    
    return render(request, 'challan/update.html', {
        'form': form,
        'challan': challan,
        'violated_rules': violated_rules,
        'original_status': challan.status
    })


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def record_offline_payment(request, challan_number):
    """View for officers to record offline challan payments"""
    challan = get_object_or_404(Challan, challan_number=challan_number)
    
    # Check if challan is already paid
    if challan.payment_status:
        messages.info(request, "This challan has already been paid.")
        return redirect('view_challan', challan_number=challan_number)
    
    if request.method == 'POST':
        form = ChallanPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.challan = challan
            
            # Validate amount matches challan total
            if payment.amount != challan.total_amount:
                messages.error(request, f"Payment amount (₹{payment.amount}) does not match challan amount (₹{challan.total_amount}).")
                form = ChallanPaymentForm(initial={'amount': challan.total_amount})
                return render(request, 'challan/record_payment.html', {'form': form, 'challan': challan})
            
            payment.save()
            
            # Send notification
            if challan.violator:
                send_notification(
                    user=challan.violator,
                    title="Challan Payment Recorded",
                    message=f"Your payment for challan #{challan.challan_number} has been recorded.",
                    notification_type="PAYMENT"
                )
                
                send_email(
                    to_email=challan.violator.email,
                    subject="Challan Payment Recorded",
                    message=f"Your payment for challan #{challan.challan_number} has been recorded. "
                            f"Payment Method: {payment.get_payment_method_display()}. "
                            f"Transaction ID: {payment.transaction_id}. "
                            f"Thank you for the payment."
                )
            
            messages.success(request, f"Payment for challan #{challan.challan_number} recorded successfully.")
            return redirect('view_challan', challan_number=challan_number)
    else:
        form = ChallanPaymentForm(initial={'amount': challan.total_amount})
    
    return render(request, 'challan/record_payment.html', {
        'form': form,
        'challan': challan
    })


# Admin views
@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def traffic_rules(request):
    """View to manage traffic rules"""
    rules = TrafficRule.objects.all().order_by('rule_code')
    return render(request, 'challan/traffic_rules.html', {'rules': rules})


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def add_traffic_rule(request):
    """View to add a new traffic rule"""
    if request.method == 'POST':
        rule_code = request.POST.get('rule_code')
        description = request.POST.get('description')
        penalty_amount = request.POST.get('penalty_amount')
        is_active = request.POST.get('is_active') == 'on'
        
        TrafficRule.objects.create(
            rule_code=rule_code,
            description=description,
            penalty_amount=penalty_amount,
            is_active=is_active
        )
        
        messages.success(request, "Traffic rule added successfully.")
        return redirect('traffic_rules')
    
    return render(request, 'challan/add_traffic_rule.html')


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def edit_traffic_rule(request, rule_id):
    """View to edit a traffic rule"""
    rule = get_object_or_404(TrafficRule, id=rule_id)
    
    if request.method == 'POST':
        rule.rule_code = request.POST.get('rule_code')
        rule.description = request.POST.get('description')
        rule.penalty_amount = request.POST.get('penalty_amount')
        rule.is_active = request.POST.get('is_active') == 'on'
        rule.save()
        
        messages.success(request, "Traffic rule updated successfully.")
        return redirect('traffic_rules')
    
    return render(request, 'challan/edit_traffic_rule.html', {'rule': rule})


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def challan_types(request):
    """View to manage challan types"""
    types = ChallanType.objects.all().order_by('name')
    return render(request, 'challan/challan_types.html', {'types': types})


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def add_challan_type(request):
    """View to add a new challan type"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        default_penalty = request.POST.get('default_penalty')
        is_active = request.POST.get('is_active') == 'on'
        
        ChallanType.objects.create(
            name=name,
            description=description,
            default_penalty=default_penalty,
            is_active=is_active
        )
        
        messages.success(request, "Challan type added successfully.")
        return redirect('challan_types')
    
    return render(request, 'challan/add_challan_type.html')


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def edit_challan_type(request, type_id):
    """View to edit a challan type"""
    challan_type = get_object_or_404(ChallanType, id=type_id)
    
    if request.method == 'POST':
        challan_type.name = request.POST.get('name')
        challan_type.description = request.POST.get('description')
        challan_type.default_penalty = request.POST.get('default_penalty')
        challan_type.is_active = request.POST.get('is_active') == 'on'
        challan_type.save()
        
        messages.success(request, "Challan type updated successfully.")
        return redirect('challan_types')
    
    return render(request, 'challan/edit_challan_type.html', {'challan_type': challan_type})


@login_required
@user_passes_test(lambda u: u.user_type in ['OFFICER', 'ADMIN'])
def challan_statistics(request):
    """View to show challan statistics"""
    # Get date range filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base queryset
    challans_qs = Challan.objects.all()
    
    # Apply date filters if provided
    if start_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        challans_qs = challans_qs.filter(issue_date__gte=start_date)
    
    if end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        challans_qs = challans_qs.filter(issue_date__lte=end_date)
    
    # Calculate statistics
    total_challans = challans_qs.count()
    paid_challans = challans_qs.filter(payment_status=True).count()
    unpaid_challans = challans_qs.filter(payment_status=False).count()
    disputed_challans = challans_qs.filter(status='DISPUTED').count()
    
    # Total revenue from paid challans
    total_revenue = challans_qs.filter(payment_status=True).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Challans by status
    status_counts = challans_qs.values('status').annotate(count=Count('status'))
    
    # Most common violations
    most_common_violations = TrafficRule.objects.filter(
        challans__in=challans_qs
    ).annotate(
        count=Count('challans')
    ).order_by('-count')[:10]
    
    # Monthly trends
    monthly_counts = challans_qs.extra(
        select={'month': "EXTRACT(MONTH FROM issue_date)"}
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    monthly_revenue = challans_qs.filter(
        payment_status=True
    ).extra(
        select={'month': "EXTRACT(MONTH FROM issue_date)"}
    ).values('month').annotate(
        sum=Sum('total_amount')
    ).order_by('month')
    
    context = {
        'total_challans': total_challans,
        'paid_challans': paid_challans,
        'unpaid_challans': unpaid_challans,
        'disputed_challans': disputed_challans,
        'total_revenue': total_revenue,
        'status_counts': status_counts,
        'most_common_violations': most_common_violations,
        'monthly_counts': monthly_counts,
        'monthly_revenue': monthly_revenue,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'challan/statistics.html', context)
