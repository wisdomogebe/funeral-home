# Import all views for easy access
from .auth import (
    login_view,
    logout_view,
    register_view,
    profile_view,
    profile_edit_view,
    home_view,
)

from .dashboard import (
    dashboard,
    admin_dashboard_detail,
)

from .case_management import (
    deceased_list,
    deceased_create,
    deceased_detail,
    deceased_update,
    next_of_kin_create,
    next_of_kin_update,
    case_list,
    case_create,
    case_detail,
    case_update,
    case_add_service,
)

from .inventory_management import (
    inventory_list,
    inventory_create,
    inventory_detail,
    inventory_update,
    inventory_adjust,
    low_stock_alert,
    inventory_report,
)

from .payment_management import (
    invoice_list,
    invoice_create,
    invoice_detail,
    invoice_issue,
    invoice_cancel,
    payment_list,
    payment_create,
    payment_detail,
    download_receipt,
)

from .reporting import (
    financial_report,
    operational_report,
    case_analysis_report,
    inventory_report_view,
    user_activity_report,
    revenue_by_service_report,
)

__all__ = [
    # Auth views
    'login_view',
    'logout_view',
    'register_view',
    'profile_view',
    'profile_edit_view',
    'home_view',
    
    # Dashboard views
    'dashboard',
    'admin_dashboard_detail',
    
    # Case management views
    'deceased_list',
    'deceased_create',
    'deceased_detail',
    'deceased_update',
    'next_of_kin_create',
    'next_of_kin_update',
    'case_list',
    'case_create',
    'case_detail',
    'case_update',
    'case_add_service',
    
    # Inventory management views
    'inventory_list',
    'inventory_create',
    'inventory_detail',
    'inventory_update',
    'inventory_adjust',
    'low_stock_alert',
    'inventory_report',
    
    # Payment management views
    'invoice_list',
    'invoice_create',
    'invoice_detail',
    'invoice_issue',
    'invoice_cancel',
    'payment_list',
    'payment_create',
    'payment_detail',
    'download_receipt',
    
    # Reporting views
    'financial_report',
    'operational_report',
    'case_analysis_report',
    'inventory_report_view',
    'user_activity_report',
    'revenue_by_service_report',
]
