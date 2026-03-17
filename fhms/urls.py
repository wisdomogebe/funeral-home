"""
URL Configuration for FHMS app.
"""
from django.urls import path
from fhms.views import (
    # Auth views
    login_view, logout_view, register_view, profile_view, profile_edit_view,
    # Dashboard views
    dashboard, admin_dashboard_detail,
    # Case management views
    deceased_list, deceased_create, deceased_detail, deceased_update,
    next_of_kin_create, next_of_kin_update,
    case_list, case_create, case_detail, case_update, case_add_service,
    # Inventory views
    inventory_list, inventory_create, inventory_detail, inventory_update,
    inventory_adjust, low_stock_alert, inventory_report,
    # Payment views
    invoice_list, invoice_create, invoice_detail, invoice_issue, invoice_cancel,
    payment_list, payment_create, payment_detail, download_receipt,
    # Reporting views
    financial_report, operational_report, case_analysis_report,
    inventory_report_view, user_activity_report, revenue_by_service_report,
)

# Authentication URLs
auth_patterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
]

# Dashboard URLs
dashboard_patterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/admin/', admin_dashboard_detail, name='admin_dashboard_detail'),
]

# Deceased Management URLs
deceased_patterns = [
    path('deceased/', deceased_list, name='deceased_list'),
    path('deceased/create/', deceased_create, name='deceased_create'),
    path('deceased/<uuid:pk>/', deceased_detail, name='deceased_detail'),
    path('deceased/<uuid:pk>/update/', deceased_update, name='deceased_update'),
]

# Next of Kin URLs
kin_patterns = [
    path('deceased/<uuid:deceased_id>/kin/create/', next_of_kin_create, name='next_of_kin_create'),
    path('kin/<uuid:pk>/update/', next_of_kin_update, name='next_of_kin_update'),
]

# Funeral Case URLs
case_patterns = [
    path('cases/', case_list, name='case_list'),
    path('cases/create/', case_create, name='case_create'),
    path('cases/<uuid:pk>/', case_detail, name='case_detail'),
    path('cases/<uuid:pk>/update/', case_update, name='case_update'),
    path('cases/<uuid:pk>/add-service/', case_add_service, name='case_add_service'),
]

# Inventory URLs
inventory_patterns = [
    path('inventory/', inventory_list, name='inventory_list'),
    path('inventory/create/', inventory_create, name='inventory_create'),
    path('inventory/<uuid:pk>/', inventory_detail, name='inventory_detail'),
    path('inventory/<uuid:pk>/update/', inventory_update, name='inventory_update'),
    path('inventory/<uuid:pk>/adjust/', inventory_adjust, name='inventory_adjust'),
    path('inventory/low-stock/', low_stock_alert, name='low_stock_alert'),
    path('inventory/report/', inventory_report, name='inventory_report'),
]

# Invoice URLs
invoice_patterns = [
    path('invoices/', invoice_list, name='invoice_list'),
    path('invoices/create/', invoice_create, name='invoice_create'),
    path('invoices/<uuid:pk>/', invoice_detail, name='invoice_detail'),
    path('invoices/<uuid:pk>/issue/', invoice_issue, name='invoice_issue'),
    path('invoices/<uuid:pk>/cancel/', invoice_cancel, name='invoice_cancel'),
]

# Payment URLs
payment_patterns = [
    path('payments/', payment_list, name='payment_list'),
    path('payments/create/', payment_create, name='payment_create'),
    path('payments/<uuid:pk>/', payment_detail, name='payment_detail'),
    path('payments/<uuid:pk>/receipt/', download_receipt, name='download_receipt'),
]

# Reporting URLs
reporting_patterns = [
    path('reports/financial/', financial_report, name='financial_report'),
    path('reports/operational/', operational_report, name='operational_report'),
    path('reports/cases/', case_analysis_report, name='case_analysis_report'),
    path('reports/inventory/', inventory_report_view, name='inventory_report_view'),
    path('reports/users/', user_activity_report, name='user_activity_report'),
    path('reports/revenue/', revenue_by_service_report, name='revenue_by_service_report'),
]

# Combine all URL patterns
urlpatterns = (
    auth_patterns +
    dashboard_patterns +
    deceased_patterns +
    kin_patterns +
    case_patterns +
    inventory_patterns +
    invoice_patterns +
    payment_patterns +
    reporting_patterns
)

app_name = 'fhms'
