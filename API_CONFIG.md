"""
Optional API URL configuration
Add this to memorial_care/urls.py to enable REST API endpoints
"""

# In memorial_care/urls.py, add:

"""
from rest_framework.routers import DefaultRouter
from fhms.viewsets import (
    FuneralCaseViewSet, InvoiceViewSet, PaymentViewSet, 
    InventoryItemViewSet
)

router = DefaultRouter()
router.register(r'cases', FuneralCaseViewSet, basename='case-api')
router.register(r'invoices', InvoiceViewSet, basename='invoice-api')
router.register(r'payments', PaymentViewSet, basename='payment-api')
router.register(r'inventory', InventoryItemViewSet, basename='inventory-api')

urlpatterns = [
    # ... existing patterns ...
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
]
"""

# To use this:
# 1. Uncomment the code above in memorial_care/urls.py
# 2. Ensure rest_framework is in INSTALLED_APPS (already is)
# 3. Configure REST_FRAMEWORK in settings.py (optional):

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# Usage Examples:

"""
GET /api/cases/
Query params:
- ?status=confirmed
- ?search=case%20number
- ?page=2

GET /api/invoices/
Query params:
- ?status=paid
- ?search=invoice%20number

GET /api/inventory/low_stock/
- Returns items below reorder level

GET /api/inventory/
Query params:
- ?category=casket
- ?search=premium
"""
