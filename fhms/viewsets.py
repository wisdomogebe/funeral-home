"""
REST API viewsets for the FHMS application (extensible).
Can be used for mobile app integration or advanced frontend.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from fhms.models import FuneralCase, Invoice, Payment, InventoryItem
from fhms.serializers import (
    FuneralCaseSerializer, InvoiceSerializer, PaymentSerializer,
    InventoryItemSerializer
)


class FuneralCaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing funeral cases.
    GET /api/cases/ - List all cases
    GET /api/cases/{id}/ - Get case details
    """
    queryset = FuneralCase.objects.all()
    serializer_class = FuneralCaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['deceased__first_name', 'deceased__last_name', 'case_number']
    
    def get_queryset(self):
        """Filter cases by user role."""
        user = self.request.user
        if user.is_family_client:
            return FuneralCase.objects.filter(client_family=user)
        return FuneralCase.objects.all()


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing invoices.
    GET /api/invoices/ - List all invoices
    GET /api/invoices/{id}/ - Get invoice details
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['invoice_number', 'case__case_number']
    
    def get_queryset(self):
        """Filter invoices by user role."""
        user = self.request.user
        if user.is_family_client:
            return Invoice.objects.filter(client=user)
        return Invoice.objects.all()


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing payments.
    GET /api/payments/ - List all payments
    GET /api/payments/{id}/ - Get payment details
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_method']
    
    def get_queryset(self):
        """Filter payments by user role."""
        user = self.request.user
        if user.is_family_client:
            return Payment.objects.filter(invoice__client=user)
        return Payment.objects.all()


class InventoryItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing inventory items.
    GET /api/inventory/ - List all items
    GET /api/inventory/{id}/ - Get item details
    """
    queryset = InventoryItem.objects.filter(is_active=True)
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'item_code']
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get items below reorder level."""
        items = self.get_queryset().filter(quantity_in_stock__lte__model_f='reorder_level')
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
