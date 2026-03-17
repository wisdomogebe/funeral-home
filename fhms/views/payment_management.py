"""
Payment and Invoice management views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from decimal import Decimal
from fhms.utils.rbac import role_required, accountant_required
from fhms.models import Invoice, Payment, FuneralCase
from fhms.forms import InvoiceForm, PaymentForm
from fhms.services.payment_service import InvoiceService, PaymentService
from fhms.utils.audit import log_action
from fhms.utils.helpers import format_currency


@login_required(login_url='login')
@role_required('admin', 'accountant', 'family_client')
@require_http_methods(['GET'])
def invoice_list(request):
    """List invoices with filters."""
    page = request.GET.get('page', 1)
    status_filter = request.GET.get('status', '')
    
    queryset = Invoice.objects.all()
    
    # Family clients see only their invoices
    if request.user.is_family_client:
        queryset = queryset.filter(client=request.user)
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    queryset = queryset.order_by('-created_at')
    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(page)
    
    # Calculate summary for accountants
    summary = None
    if request.user.is_accountant or request.user.is_admin:
        all_invoices = Invoice.objects.all()
        summary = {
            'total_invoices': all_invoices.count(),
            'paid': all_invoices.filter(status='paid').count(),
            'pending': all_invoices.exclude(status='paid').exclude(status='cancelled').count(),
            'total_amount': sum(i.total_amount for i in all_invoices),
            'amount_paid': sum(i.amount_paid for i in all_invoices),
        }
    
    context = {
        'invoices': page_obj,
        'status_filter': status_filter,
        'status_choices': Invoice.STATUS_CHOICES,
        'summary': summary
    }
    return render(request, 'invoice/list.html', context)


@login_required(login_url='login')
@role_required('admin', 'accountant', 'director')
@require_http_methods(['GET', 'POST'])
def invoice_create(request):
    """Create a new invoice."""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            try:
                case = form.cleaned_data['case']
                invoice = InvoiceService.generate_invoice(case.id, tax_rate=0.0)
                log_action(request.user, 'CREATE', 'Invoice', invoice.id,
                          f'Created invoice {invoice.invoice_number}', request)
                messages.success(request, f'Invoice {invoice.invoice_number} created.')
                return redirect('fhms:invoice_detail', pk=invoice.id)
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = InvoiceForm()
    
    return render(request, 'invoice/form.html', {'form': form, 'action': 'Create'})


@login_required(login_url='login')
@role_required('admin', 'accountant', 'family_client')
@require_http_methods(['GET'])
def invoice_detail(request, pk):
    """View invoice details."""
    invoice = get_object_or_404(Invoice, id=pk)
    
    # Check access
    if request.user.is_family_client and invoice.client != request.user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    details = InvoiceService.get_invoice_details(pk)
    
    context = {
        'invoice': invoice,
        'case': invoice.case,
        'payments': details['payments'] if details else [],
        'formatted_total': format_currency(invoice.total_amount),
        'formatted_balance': format_currency(invoice.balance_due),
        'formatted_paid': format_currency(invoice.amount_paid)
    }
    return render(request, 'invoice/detail.html', context)


@login_required(login_url='login')
@role_required('admin', 'accountant')
@require_http_methods(['POST'])
def invoice_issue(request, pk):
    """Issue (finalize) an invoice."""
    invoice = get_object_or_404(Invoice, id=pk)
    
    try:
        InvoiceService.issue_invoice(pk)
        log_action(request.user, 'UPDATE', 'Invoice', invoice.id,
                  f'Issued invoice {invoice.invoice_number}', request)
        messages.success(request, f'Invoice {invoice.invoice_number} issued.')
    except ValueError as e:
        messages.error(request, str(e))
    
    return redirect('fhms:invoice_detail', pk=pk)


@login_required(login_url='login')
@role_required('admin', 'accountant')
@require_http_methods(['POST'])
def invoice_cancel(request, pk):
    """Cancel an invoice."""
    invoice = get_object_or_404(Invoice, id=pk)
    invoice.status = 'cancelled'
    invoice.save()
    
    log_action(request.user, 'UPDATE', 'Invoice', invoice.id,
              f'Cancelled invoice {invoice.invoice_number}', request)
    messages.success(request, 'Invoice cancelled.')
    return redirect('fhms:invoice_list')


# ============ PAYMENT VIEWS ============

@login_required(login_url='login')
@role_required('admin', 'accountant', 'family_client')
@require_http_methods(['GET'])
def payment_list(request):
    """List payments."""
    page = request.GET.get('page', 1)
    
    queryset = Payment.objects.all()
    
    # Family clients see only their payments
    if request.user.is_family_client:
        queryset = queryset.filter(invoice__client=request.user)
    
    queryset = queryset.order_by('-payment_date')
    paginator = Paginator(queryset, 15)
    page_obj = paginator.get_page(page)
    
    context = {'payments': page_obj}
    return render(request, 'payment/list.html', context)


@login_required(login_url='login')
@role_required('admin', 'accountant', 'family_client')
@require_http_methods(['GET', 'POST'])
def payment_create(request):
    """Record a payment."""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                invoice = form.cleaned_data['invoice']
                amount = form.cleaned_data['amount']
                payment_method = form.cleaned_data['payment_method']
                transaction_ref = form.cleaned_data.get('transaction_reference', '')
                
                payment = PaymentService.process_payment(
                    invoice.id, amount, payment_method, transaction_ref
                )
                
                log_action(request.user, 'PAYMENT', 'Payment', payment.id,
                          f'Recorded payment {payment.receipt_number}', request)
                messages.success(request, f'Payment recorded: {payment.receipt_number}')
                return redirect('fhms:payment_detail', pk=payment.id)
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = PaymentForm()
    
    return render(request, 'payment/form.html', {'form': form, 'action': 'Record Payment'})


@login_required(login_url='login')
@role_required('admin', 'accountant', 'family_client')
@require_http_methods(['GET'])
def payment_detail(request, pk):
    """View payment details."""
    payment = get_object_or_404(Payment, id=pk)
    
    # Check access
    if request.user.is_family_client and payment.invoice.client != request.user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    context = {
        'payment': payment,
        'invoice': payment.invoice,
        'formatted_amount': format_currency(payment.amount)
    }
    return render(request, 'payment/detail.html', context)


@login_required(login_url='login')
@role_required('admin', 'family_client')
@require_http_methods(['GET'])
def download_receipt(request, pk):
    """Download payment receipt as PDF (simplified)."""
    payment = get_object_or_404(Payment, id=pk)
    
    # Check access
    if request.user.is_family_client and payment.invoice.client != request.user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # This would typically generate a PDF
    # For now, return a simple text receipt
    context = {
        'payment': payment,
        'invoice': payment.invoice,
        'case': payment.invoice.case
    }
    
    from django.http import HttpResponse
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.receipt_number}.txt"'
    
    receipt_text = f"""
    MEMORIAL CARE FUNERAL HOME
    OFFICIAL RECEIPT
    
    Receipt Number: {payment.receipt_number}
    Date: {payment.payment_date.strftime('%Y-%m-%d %H:%M')}
    
    INVOICE DETAILS
    Invoice Number: {payment.invoice.invoice_number}
    Case Number: {payment.invoice.case.case_number}
    Deceased: {payment.invoice.case.deceased.full_name}
    
    PAYMENT DETAILS
    Amount Paid: {format_currency(payment.amount)}
    Payment Method: {payment.get_payment_method_display()}
    Status: {payment.get_status_display()}
    
    Invoice Balance: {format_currency(payment.invoice.balance_due)}
    
    Thank you for your payment!
    """
    
    response.write(receipt_text)
    return response
