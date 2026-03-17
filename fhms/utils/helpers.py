"""
General utility functions for the FHMS application.
"""
from decimal import Decimal
from datetime import datetime, timedelta
import uuid
from django.utils import timezone


def generate_case_number():
    """Generate a unique case number."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"CASE-{timestamp}-{unique_id}"


def generate_invoice_number():
    """Generate a unique invoice number."""
    timestamp = datetime.now().strftime('%Y%m%d')
    unique_id = str(uuid.uuid4())[:6].upper()
    return f"INV-{timestamp}-{unique_id}"


def generate_receipt_number():
    """Generate a unique receipt number."""
    timestamp = datetime.now().strftime('%Y%m%d')
    unique_id = str(uuid.uuid4())[:6].upper()
    return f"REC-{timestamp}-{unique_id}"


def calculate_invoice_due_date(days=14):
    """Calculate invoice due date (default 14 days from now)."""
    return timezone.now().date() + timedelta(days=days)


def format_currency(amount, currency='NGN'):
    """Format amount as currency string."""
    if isinstance(amount, (int, float)):
        amount = Decimal(str(amount))
    return f"{currency} {amount:,.2f}"


def get_payment_status(invoice):
    """Determine payment status of an invoice."""
    if invoice.status == 'paid':
        return 'Paid'
    elif invoice.status == 'cancelled':
        return 'Cancelled'
    elif invoice.balance_due == 0:
        return 'Paid'
    elif invoice.amount_paid > 0:
        return 'Partially Paid'
    elif invoice.is_overdue:
        return 'Overdue'
    return 'Pending'


def calculate_age(birth_date):
    """Calculate age from birth date."""
    today = timezone.now().date()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def is_valid_phone(phone):
    """Validate phone number format."""
    import re
    # Simple validation - allows 10-20 digits with optional +
    pattern = r'^\+?[0-9]{10,20}$'
    return re.match(pattern, phone) is not None


def paginate_queryset(queryset, page_number, per_page=10):
    """
    Simple pagination function.
    Returns: (items, total_pages, current_page)
    """
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    paginator = Paginator(queryset, per_page)
    try:
        page = paginator.page(page_number)
        return page.object_list, paginator.num_pages, page.number
    except (EmptyPage, PageNotAnInteger):
        return paginator.page(1).object_list, paginator.num_pages, 1


def get_low_stock_items():
    """Get all inventory items that are below reorder level."""
    from fhms.models import InventoryItem
    return InventoryItem.objects.filter(quantity_in_stock__lte=models.F('reorder_level'), is_active=True)


def calculate_inventory_value():
    """Calculate total value of current inventory."""
    from fhms.models import InventoryItem
    from django.db.models import Sum, F
    
    result = InventoryItem.objects.aggregate(
        total_value=Sum(F('quantity_in_stock') * F('unit_cost'), output_field=models.DecimalField())
    )
    return result['total_value'] or Decimal('0.00')
