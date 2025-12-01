from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime
from .models import Workshop, Registration, Payment
from .forms import RegistrationForm
from .payment_gateway import SSLCommerzPayment
from .utils import send_confirmation_email, send_payment_confirmation_email, generate_receipt_pdf, get_receipt_filename


def workshop_list(request):
    """Display all active workshops"""
    
    workshops = Workshop.objects.filter(is_active=True).order_by('workshop_date')
    
    context = {
        'workshops': workshops,
        'page_title': 'Titanium Science Club Workshops',
    }
    
    return render(request, 'workshops/workshop_list.html', context)


def register_workshop(request, workshop_id):
    """Handle workshop registration"""
    
    workshop = get_object_or_404(Workshop, id=workshop_id, is_active=True)
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST, workshop=workshop)
        
        if form.is_valid():
            # Create registration
            registration = form.save(commit=False)
            registration.workshop = workshop
            
            try:
                registration.save()
                
                # Send confirmation email
                send_confirmation_email(registration)
                
                # If workshop is free, redirect to success page
                if workshop.is_free:
                    messages.success(
                        request,
                        f'Registration successful! Your registration number is {registration.registration_number}'
                    )
                    return redirect('registration_success', registration_id=registration.id)
                
                # If workshop requires payment, redirect to payment page
                else:
                    return redirect('payment_confirmation', registration_id=registration.id)
            
            except Exception as e:
                messages.error(request, f'Error during registration: {str(e)}')
    
    else:
        form = RegistrationForm(workshop=workshop)
    
    context = {
        'form': form,
        'workshop': workshop,
        'page_title': f'Register for {workshop.name}',
    }
    
    return render(request, 'workshops/register.html', context)


def payment_confirmation(request, registration_id):
    """Display payment confirmation and initiate SSLCommerz payment"""
    
    registration = get_object_or_404(Registration, id=registration_id)
    
    # Check if workshop is free
    if registration.workshop.is_free:
        messages.info(request, 'This is a free workshop. No payment required.')
        return redirect('registration_success', registration_id=registration.id)
    
    # Check if payment already completed
    if registration.payment_status == 'completed':
        messages.info(request, 'Payment already completed for this registration.')
        return redirect('registration_success', registration_id=registration.id)
    
    # Initialize payment gateway
    sslcommerz = SSLCommerzPayment()
    
    # Initiate payment
    if request.method == 'POST':
        payment_response = sslcommerz.initiate_payment(registration, request)
        
        if payment_response['success']:
            # Create payment record
            payment = Payment.objects.create(
                registration=registration,
                transaction_id=payment_response['transaction_id'],
                amount=registration.workshop.fee,
                currency=settings.CURRENCY,
                payment_method='sslcommerz',
                sslcommerz_data=payment_response['response_data']
            )
            
            # Redirect to SSLCommerz payment page
            return redirect(payment_response['gateway_url'])
        else:
            messages.error(request, f"Payment initiation failed: {payment_response.get('error', 'Unknown error')}")
    
    context = {
        'registration': registration,
        'workshop': registration.workshop,
        'page_title': 'Payment Confirmation',
    }
    
    return render(request, 'workshops/payment_confirmation.html', context)


@csrf_exempt
def payment_success(request):
    """Handle successful payment callback from SSLCommerz"""
    
    if request.method == 'POST':
        # Get payment data from SSLCommerz
        val_id = request.POST.get('val_id')
        tran_id = request.POST.get('tran_id')
        amount = request.POST.get('amount')
        card_type = request.POST.get('card_type')
        store_amount = request.POST.get('store_amount')
        registration_number = request.POST.get('value_a')
        
        try:
            # Get payment record
            payment = Payment.objects.get(transaction_id=tran_id)
            registration = payment.registration
            
            # Validate payment with SSLCommerz
            sslcommerz = SSLCommerzPayment()
            validation_response = sslcommerz.validate_payment(val_id, tran_id)
            
            if validation_response['success']:
                # Verify amount
                if sslcommerz.verify_payment_amount(amount, registration.workshop.fee):
                    # Mark payment as completed
                    payment.sslcommerz_data = validation_response['response_data']
                    payment.mark_completed()
                    
                    # Send confirmation email
                    send_payment_confirmation_email(registration, payment)
                    
                    messages.success(
                        request,
                        f'Payment successful! Your registration is confirmed. Registration number: {registration.registration_number}'
                    )
                    return redirect('payment_success_page', registration_id=registration.id)
                else:
                    messages.error(request, 'Payment amount mismatch. Please contact support.')
                    payment.mark_failed()
            else:
                messages.error(request, 'Payment validation failed. Please contact support.')
                payment.mark_failed()
        
        except Payment.DoesNotExist:
            messages.error(request, 'Payment record not found.')
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
    
    return redirect('workshop_list')


@csrf_exempt
def payment_fail(request):
    """Handle failed payment callback from SSLCommerz"""
    
    if request.method == 'POST':
        tran_id = request.POST.get('tran_id')
        
        try:
            payment = Payment.objects.get(transaction_id=tran_id)
            payment.mark_failed()
            messages.error(request, 'Payment failed. Please try again or contact support.')
        except Payment.DoesNotExist:
            messages.error(request, 'Payment record not found.')
    
    return redirect('workshop_list')


@csrf_exempt
def payment_cancel(request):
    """Handle cancelled payment callback from SSLCommerz"""
    
    if request.method == 'POST':
        tran_id = request.POST.get('tran_id')
        
        try:
            payment = Payment.objects.get(transaction_id=tran_id)
            payment.payment_status = 'cancelled'
            payment.registration.payment_status = 'cancelled'
            payment.registration.save()
            payment.save()
            messages.warning(request, 'Payment cancelled. You can try again from your registration.')
        except Payment.DoesNotExist:
            messages.error(request, 'Payment record not found.')
    
    return redirect('workshop_list')


def payment_success_page(request, registration_id):
    """Display payment success page"""
    
    registration = get_object_or_404(Registration, id=registration_id)
    
    context = {
        'registration': registration,
        'workshop': registration.workshop,
        'payment': registration.payment if hasattr(registration, 'payment') else None,
        'page_title': 'Registration Successful',
    }
    
    return render(request, 'workshops/payment_success.html', context)


def registration_success(request, registration_id):
    """Display registration success page for free workshops"""
    
    registration = get_object_or_404(Registration, id=registration_id)
    
    context = {
        'registration': registration,
        'workshop': registration.workshop,
        'page_title': 'Registration Successful',
    }
    
    return render(request, 'workshops/registration_success.html', context)


def download_receipt(request, registration_id):
    """Generate and download PDF receipt"""
    
    registration = get_object_or_404(Registration, id=registration_id)
    
    # Check if registration is confirmed
    if registration.payment_status not in ['completed', 'free']:
        raise Http404("Receipt not available for pending registrations")
    
    try:
        # Generate PDF
        pdf_buffer = generate_receipt_pdf(registration)
        
        # Create response
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{get_receipt_filename(registration)}"'
        
        return response
    
    except Exception as e:
        messages.error(request, f'Error generating receipt: {str(e)}')
        return redirect('workshop_list')


def view_receipt(request, registration_id):
    """View receipt in browser"""
    
    registration = get_object_or_404(Registration, id=registration_id)
    
    context = {
        'registration': registration,
        'workshop': registration.workshop,
        'page_title': 'Registration Receipt',
    }
    
    return render(request, 'workshops/receipt.html', context)


def admin_dashboard(request):
    """Admin dashboard with statistics and analytics"""
    
    # Check if user is authenticated and is staff
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'You must be logged in as staff to access the admin dashboard.')
        return redirect('workshop_list')
    
    from django.db.models import Sum, Count, Q
    from decimal import Decimal
    
    # Get all workshops
    workshops = Workshop.objects.all().order_by('-workshop_date')
    
    # Total registrations
    total_registrations = Registration.objects.count()
    
    # Total revenue (completed payments only)
    total_revenue = Payment.objects.filter(
        payment_status='completed'
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Active workshops (upcoming)
    active_workshops = Workshop.objects.filter(is_active=True).count()
    
    # Pending payments count
    pending_payments = Registration.objects.filter(
        payment_status='pending'
    ).count()
    
    # Event-wise participant counts
    event_stats = Workshop.objects.annotate(
        total_participants=Count('registrations'),
        completed_payments=Count('registrations', filter=Q(registrations__payment_status='completed')),
        pending_payments=Count('registrations', filter=Q(registrations__payment_status='pending')),
        free_registrations=Count('registrations', filter=Q(registrations__payment_status='free')),
        revenue=Sum('registrations__payment__amount', filter=Q(registrations__payment__payment_status='completed'))
    ).order_by('-workshop_date')
    
    # Payment status breakdown
    payment_breakdown = {
        'completed': Registration.objects.filter(payment_status='completed').count(),
        'pending': Registration.objects.filter(payment_status='pending').count(),
        'failed': Registration.objects.filter(payment_status='failed').count(),
        'free': Registration.objects.filter(payment_status='free').count(),
    }
    
    # Recent registrations (last 10)
    recent_registrations = Registration.objects.select_related(
        'workshop'
    ).order_by('-registered_at')[:10]
    
    # Revenue by workshop (for chart)
    revenue_by_workshop = []
    for workshop in workshops:
        workshop_revenue = Payment.objects.filter(
            registration__workshop=workshop,
            payment_status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        revenue_by_workshop.append({
            'name': workshop.name[:30],  # Truncate long names
            'revenue': float(workshop_revenue),
            'participants': workshop.registrations.count()
        })
    
    context = {
        'page_title': 'Admin Dashboard',
        'total_registrations': total_registrations,
        'total_revenue': total_revenue,
        'active_workshops': active_workshops,
        'pending_payments': pending_payments,
        'event_stats': event_stats,
        'payment_breakdown': payment_breakdown,
        'recent_registrations': recent_registrations,
        'revenue_by_workshop': revenue_by_workshop[:10],  # Limit to 10 for chart
    }
    
    return render(request, 'workshops/admin_dashboard.html', context)
