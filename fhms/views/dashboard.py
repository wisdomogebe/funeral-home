"""
Dashboard views - main hub for different user roles.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import F
from fhms.utils.rbac import role_required
from fhms.models import FuneralCase, Invoice, InventoryItem, Payment, InventoryTransaction
from fhms.services.reporting_service import ReportService
from datetime import datetime, timedelta
from django.utils import timezone


@login_required(login_url='login')
@require_http_methods(['GET'])
def dashboard(request):
    """
    Main dashboard view with role-based content.
    Each role sees relevant information.
    """
    user = request.user
    context = {'user': user}
    
    if user.is_admin:
        # Admin dashboard - full system overview
        context.update({
            'total_cases': FuneralCase.objects.count(),
            'completed_cases': FuneralCase.objects.filter(status='completed').count(),
            'pending_invoices': Invoice.objects.filter(status__in=['draft', 'issued']).count(),
            'new_cases': FuneralCase.objects.filter(status='pending')[:5],
            'low_stock_items': InventoryItem.objects.filter(quantity_in_stock__lte=F('reorder_level'), is_active=True).count(),
        })
        template = 'dashboard/admin_dashboard.html'
    
    elif user.is_director:
        # Funeral Director dashboard - case management focus
        context.update({
            'my_cases': FuneralCase.objects.filter(funeral_director=user),
            'assigned_cases': FuneralCase.objects.filter(assigned_staff=user).distinct(),
            'pending_cases': FuneralCase.objects.filter(funeral_director=user, status='pending'),
            'today_scheduled': FuneralCase.objects.filter(
                funeral_director=user,
                scheduled_date__date=timezone.now().date()
            )
        })
        template = 'dashboard/director_dashboard.html'
    
    elif user.is_accountant:
        # Accountant dashboard - financial focus
        invoices = Invoice.objects.all()
        context.update({
            'total_invoices': invoices.count(),
            'paid_invoices': invoices.filter(status='paid').count(),
            'pending_payments': invoices.filter(status__in=['draft', 'issued', 'partially_paid']).count(),
            'overdue_invoices': invoices.filter(amount_paid__lt=F('total_amount')).count(),
            'recent_payments': Payment.objects.filter(status='completed').order_by('-payment_date')[:10]
        })
        template = 'dashboard/accountant_dashboard.html'
    
    elif user.is_inventory_manager:
        # Inventory Manager dashboard - stock focus
        context.update({
            'total_items': InventoryItem.objects.filter(is_active=True).count(),
            'low_stock_items': InventoryItem.objects.filter(
                quantity_in_stock__lte=F('reorder_level'),
                is_active=True
            ),
            'recent_transactions': InventoryTransaction.objects.all().order_by('-created_at')[:10],
        })
        template = 'dashboard/inventory_dashboard.html'
    
    else:  # Family Client
        # Family Client dashboard - their funeral arrangements
        context.update({
            'my_cases': FuneralCase.objects.filter(client_family=user),
            'my_invoices': Invoice.objects.filter(client=user),
            'pending_payments': Invoice.objects.filter(client=user).exclude(status='paid'),
        })
        template = 'dashboard/family_dashboard.html'
    
    return render(request, template, context)


@login_required(login_url='login')
@require_http_methods(['GET'])
@role_required('admin')
def admin_dashboard_detail(request):
    """Detailed admin dashboard with metrics."""
    # Financial metrics
    start_date = timezone.now().date() - timedelta(days=30)
    end_date = timezone.now().date()
    
    financial_summary = ReportService.get_financial_summary(start_date, end_date)
    operational_summary = ReportService.get_operational_summary(start_date, end_date)
    
    context = {
        'financial_summary': financial_summary,
        'operational_summary': operational_summary,
        'period': f'{start_date} to {end_date}'
    }
    
    return render(request, 'dashboard/admin_detail.html', context)
