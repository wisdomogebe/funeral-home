"""
Payment and Invoice Management Service
Handles billing, invoicing, and payment processing.
"""
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from fhms.models import Invoice, Payment, FuneralCase
from fhms.utils.helpers import generate_invoice_number, generate_receipt_number, calculate_invoice_due_date
from fhms.utils.audit import log_action


class InvoiceService:
    """Service for managing invoices."""
    
    @staticmethod
    def generate_invoice(case_id, tax_rate=0.0):
        """
        Generate an invoice for a funeral case.
        
        Args:
            case_id: UUID of the funeral case
            tax_rate: Tax percentage (e.g., 0.05 for 5%)
            
        Returns:
            Invoice instance
        """
        try:
            case = FuneralCase.objects.get(id=case_id)
            
            # Calculate totals
            subtotal = case.total_cost
            tax_amount = subtotal * Decimal(str(tax_rate))
            total_amount = subtotal + tax_amount
            
            invoice = Invoice.objects.create(
                invoice_number=generate_invoice_number(),
                case=case,
                client=case.client_family,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                due_date=calculate_invoice_due_date()
            )
            
            log_action(None, 'CREATE', 'Invoice', invoice.id,
                      f'Generated invoice {invoice.invoice_number} for case {case.case_number}')
            return invoice
        except FuneralCase.DoesNotExist:
            raise ValueError("Case not found")
    
    @staticmethod
    def issue_invoice(invoice_id):
        """Mark an invoice as issued."""
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            if invoice.status != 'draft':
                raise ValueError("Only draft invoices can be issued")
            
            invoice.status = 'issued'
            invoice.issued_at = timezone.now()
            invoice.save()
            
            log_action(None, 'UPDATE', 'Invoice', invoice.id,
                      f'Invoice {invoice.invoice_number} issued')
            return invoice
        except Invoice.DoesNotExist:
            raise ValueError("Invoice not found")
    
    @staticmethod
    def get_invoice_details(invoice_id):
        """Get complete invoice details."""
        try:
            invoice = Invoice.objects.select_related('case', 'client').get(id=invoice_id)
            return {
                'invoice': invoice,
                'case': invoice.case,
                'client': invoice.client,
                'payments': invoice.payments.all(),
                'balance_due': invoice.balance_due,
                'status': invoice.status
            }
        except Invoice.DoesNotExist:
            return None
    
    @staticmethod
    def update_invoice_status(invoice_id):
        """Update invoice status based on payment amount."""
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            
            if invoice.balance_due == 0:
                invoice.status = 'paid'
            elif invoice.amount_paid > 0:
                invoice.status = 'partially_paid'
            elif invoice.is_overdue and invoice.status != 'paid':
                invoice.status = 'overdue'
            
            invoice.save()
            return invoice
        except Invoice.DoesNotExist:
            raise ValueError("Invoice not found")


class PaymentService:
    """Service for managing payments."""
    
    @staticmethod
    @transaction.atomic
    def process_payment(invoice_id, amount, payment_method, transaction_reference=""):
        """
        Process a payment for an invoice.
        
        Args:
            invoice_id: UUID of the invoice
            amount: Payment amount
            payment_method: Method of payment
            transaction_reference: External transaction ID (for online payments)
            
        Returns:
            Payment instance
        """
        try:
            invoice = Invoice.objects.select_for_update().get(id=invoice_id)
            
            # Validate payment
            if amount <= 0:
                raise ValueError("Payment amount must be positive")
            if amount > invoice.balance_due:
                raise ValueError("Payment exceeds outstanding balance")
            
            # Create payment record
            payment = Payment.objects.create(
                invoice=invoice,
                amount=amount,
                payment_method=payment_method,
                transaction_reference=transaction_reference,
                receipt_number=generate_receipt_number(),
                status='completed'
            )
            
            # Update invoice
            invoice.amount_paid += amount
            invoice.save()
            
            # Update invoice status
            InvoiceService.update_invoice_status(invoice_id)
            
            log_action(None, 'PAYMENT', 'Payment', payment.id,
                      f'Payment of {amount} received for invoice {invoice.invoice_number}')
            
            return payment
        except Invoice.DoesNotExist:
            raise ValueError("Invoice not found")
    
    @staticmethod
    def get_payment_history(invoice_id):
        """Get payment history for an invoice."""
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            payments = invoice.payments.filter(status='completed').order_by('-payment_date')
            return list(payments)
        except Invoice.DoesNotExist:
            return []
    
    @staticmethod
    def refund_payment(payment_id):
        """Refund a payment."""
        try:
            payment = Payment.objects.get(id=payment_id)
            
            if payment.status != 'completed':
                raise ValueError("Only completed payments can be refunded")
            
            # Update payment status
            payment.status = 'refunded'
            payment.save()
            
            # Update invoice
            payment.invoice.amount_paid -= payment.amount
            payment.invoice.save()
            
            # Update invoice status
            InvoiceService.update_invoice_status(payment.invoice.id)
            
            log_action(None, 'UPDATE', 'Payment', payment.id,
                      f'Payment {payment.receipt_number} refunded')
            
            return payment
        except Payment.DoesNotExist:
            raise ValueError("Payment not found")
    
    @staticmethod
    def get_pending_payments():
        """Get all pending payments."""
        return Payment.objects.filter(status='pending').select_related('invoice')
