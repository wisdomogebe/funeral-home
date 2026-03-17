"""
Reporting views for financial and operational reports.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
from fhms.utils.rbac import role_required
from fhms.services.reporting_service import ReportService


@login_required(login_url='login')
@role_required('admin', 'accountant')
@require_http_methods(['GET'])
def financial_report(request):
    """Display financial report."""
    days = request.GET.get('days', 30)
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    summary = ReportService.get_financial_summary(start_date, end_date)
    
    context = {
        'summary': summary,
        'days': days,
        'report_title': f'Financial Report - Last {days} Days'
    }
    return render(request, 'reports/financial_report.html', context)


@login_required(login_url='login')
@role_required('admin', 'director')
@require_http_methods(['GET'])
def operational_report(request):
    """Display operational report."""
    days = request.GET.get('days', 30)
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    summary = ReportService.get_operational_summary(start_date, end_date)
    
    context = {
        'summary': summary,
        'days': days,
        'report_title': f'Operational Report - Last {days} Days'
    }
    return render(request, 'reports/operational_report.html', context)


@login_required(login_url='login')
@role_required('admin', 'accountant', 'director')
@require_http_methods(['GET'])
def case_analysis_report(request):
    """Display case analysis report."""
    days = request.GET.get('days', 30)
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    analysis = ReportService.get_case_analysis(start_date, end_date)
    
    context = {
        'analysis': analysis,
        'days': days,
        'report_title': f'Case Analysis Report - Last {days} Days'
    }
    return render(request, 'reports/case_analysis.html', context)


@login_required(login_url='login')
@role_required('admin', 'inventory_manager')
@require_http_methods(['GET'])
def inventory_report_view(request):
    """Display inventory report."""
    report = ReportService.get_inventory_report()
    
    context = {
        'report': report,
        'report_title': 'Current Inventory Report'
    }
    return render(request, 'reports/inventory_report.html', context)


@login_required(login_url='login')
@role_required('admin')
@require_http_methods(['GET'])
def user_activity_report(request):
    """Display user activity report."""
    days = request.GET.get('days', 7)
    try:
        days = int(days)
    except ValueError:
        days = 7
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    report = ReportService.get_user_activity_report(start_date, end_date)
    
    context = {
        'report': report,
        'days': days,
        'report_title': f'User Activity Report - Last {days} Days'
    }
    return render(request, 'reports/user_activity.html', context)


@login_required(login_url='login')
@role_required('admin', 'accountant')
@require_http_methods(['GET'])
def revenue_by_service_report(request):
    """Display revenue breakdown by service."""
    days = request.GET.get('days', 30)
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    report = ReportService.get_revenue_by_service(start_date, end_date)
    
    context = {
        'report': report,
        'days': days,
        'report_title': f'Revenue by Service - Last {days} Days'
    }
    return render(request, 'reports/revenue_by_service.html', context)
