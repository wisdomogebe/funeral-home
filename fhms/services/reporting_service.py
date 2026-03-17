"""
Reporting Service
Generates operational and financial reports for the funeral home.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from fhms.models import (
    FuneralCase, Invoice, Payment, InventoryItem, CustomUser, AuditLog
)
from fhms.utils.audit import log_action


class ReportService:
    """Service for generating reports."""
    
    @staticmethod
    def get_financial_summary(start_date, end_date):
        """
        Generate financial summary for a period.
        
        Returns:
            Dictionary with financial metrics
        """
        invoices = Invoice.objects.filter(
            created_at__range=(start_date, end_date)
        )
        
        payments = Payment.objects.filter(
            payment_date__range=(start_date, end_date),
            status='completed'
        )
        
        summary = {
            'period_start': start_date,
            'period_end': end_date,
            'total_invoiced': invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00'),
            'total_collected': payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00'),
            'total_tax': invoices.aggregate(Sum('tax_amount'))['tax_amount__sum'] or Decimal('0.00'),
            'invoice_count': invoices.count(),
            'payment_count': payments.count(),
            'paid_invoices': invoices.filter(status='paid').count(),
            'pending_invoices': invoices.filter(status__in=['draft', 'issued']).count(),
            'overdue_invoices': invoices.filter(
                Q(due_date__lt=timezone.now().date()) & ~Q(status='paid')
            ).count(),
        }
        
        # Calculate collection rate
        if summary['total_invoiced'] > 0:
            summary['collection_rate'] = (summary['total_collected'] / summary['total_invoiced']) * 100
        else:
            summary['collection_rate'] = 0
        
        # Calculate outstanding
        summary['outstanding_amount'] = summary['total_invoiced'] - summary['total_collected']
        
        return summary
    
    @staticmethod
    def get_operational_summary(start_date, end_date):
        """
        Generate operational summary for a period.
        
        Returns:
            Dictionary with operational metrics
        """
        cases = FuneralCase.objects.filter(
            created_at__range=(start_date, end_date)
        )
        
        summary = {
            'period_start': start_date,
            'period_end': end_date,
            'total_cases': cases.count(),
            'completed_cases': cases.filter(status='completed').count(),
            'confirmed_cases': cases.filter(status='confirmed').count(),
            'cancelled_cases': cases.filter(status='cancelled').count(),
            'pending_cases': cases.filter(status='pending').count(),
        }
        
        # Calculate average case cost
        avg_cost = cases.aggregate(
            avg=Sum(F('caseservice__cost')) / Count('id', distinct=True)
        )['avg'] or Decimal('0.00')
        summary['average_case_cost'] = avg_cost
        
        return summary
    
    @staticmethod
    def get_inventory_report():
        """Generate current inventory report."""
        items = InventoryItem.objects.filter(is_active=True)
        
        low_stock_items = items.filter(
            quantity_in_stock__lte=F('reorder_level')
        )
        
        report = {
            'generated_at': timezone.now(),
            'total_items': items.count(),
            'total_value': items.aggregate(
                value=Sum(F('quantity_in_stock') * F('unit_cost'))
            )['value'] or Decimal('0.00'),
            'low_stock_count': low_stock_items.count(),
            'low_stock_value': low_stock_items.aggregate(
                value=Sum(F('quantity_in_stock') * F('unit_cost'))
            )['value'] or Decimal('0.00'),
            'by_category': {}
        }
        
        # Group by category
        for category_code, category_name in InventoryItem.CATEGORY_CHOICES:
            category_items = items.filter(category=category_code)
            report['by_category'][category_name] = {
                'count': category_items.count(),
                'value': category_items.aggregate(
                    value=Sum(F('quantity_in_stock') * F('unit_cost'))
                )['value'] or Decimal('0.00')
            }
        
        return report
    
    @staticmethod
    def get_case_analysis(start_date, end_date):
        """Analyze case data for the period."""
        cases = FuneralCase.objects.filter(
            created_at__range=(start_date, end_date)
        ).prefetch_related('caseservice')
        
        analysis = {
            'period_start': start_date,
            'period_end': end_date,
            'total_cases': cases.count(),
            'cases_by_status': {},
            'popular_services': [],
            'staff_workload': {}
        }
        
        # Cases by status
        for status, _ in FuneralCase.STATUS_CHOICES:
            count = cases.filter(status=status).count()
            if count > 0:
                analysis['cases_by_status'][status] = count
        
        # Popular services (service count in cases)
        from fhms.models import CaseService
        service_stats = CaseService.objects.filter(
            case__in=cases
        ).values('service_type__name').annotate(count=Count('id')).order_by('-count')[:5]
        
        analysis['popular_services'] = list(service_stats)
        
        # Staff workload
        staff_stats = cases.values(
            'funeral_director__first_name',
            'funeral_director__last_name'
        ).annotate(case_count=Count('id')).order_by('-case_count')
        
        analysis['staff_workload'] = list(staff_stats)
        
        return analysis
    
    @staticmethod
    def get_user_activity_report(start_date, end_date):
        """Generate user activity report from audit logs."""
        logs = AuditLog.objects.filter(
            created_at__range=(start_date, end_date)
        )
        
        report = {
            'period_start': start_date,
            'period_end': end_date,
            'total_actions': logs.count(),
            'actions_by_type': {},
            'users_activity': {}
        }
        
        # Actions by type
        for action, _ in AuditLog.ACTION_CHOICES:
            count = logs.filter(action=action).count()
            if count > 0:
                report['actions_by_type'][action] = count
        
        # Activity by user
        user_stats = logs.values(
            'user__email',
            'user__first_name',
            'user__last_name'
        ).annotate(action_count=Count('id')).order_by('-action_count')[:10]
        
        report['users_activity'] = list(user_stats)
        
        return report
    
    @staticmethod
    def get_revenue_by_service(start_date, end_date):
        """Generate revenue breakdown by service type."""
        from fhms.models import CaseService
        
        services = CaseService.objects.filter(
            case__created_at__range=(start_date, end_date)
        ).values('service_type__name').annotate(
            total_revenue=Sum('cost'),
            count=Count('id'),
            avg_cost=Sum('cost') / Count('id', distinct=True)
        ).order_by('-total_revenue')
        
        return {
            'period_start': start_date,
            'period_end': end_date,
            'services': list(services),
            'total_revenue': sum(s['total_revenue'] for s in services)
        }
