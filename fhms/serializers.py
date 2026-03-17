"""
Sample API serializers for REST API (extensible)
"""
from rest_framework import serializers
from fhms.models import (
    FuneralCase, Invoice, Payment, InventoryItem, Deceased
)


class DeceasedSerializer(serializers.ModelSerializer):
    """Serializer for Deceased model."""
    class Meta:
        model = Deceased
        fields = [
            'id', 'first_name', 'last_name', 'date_of_birth',
            'date_of_death', 'gender', 'identity_number', 'full_name'
        ]
        read_only_fields = ['id']


class FuneralCaseSerializer(serializers.ModelSerializer):
    """Serializer for Funeral Case model."""
    deceased = DeceasedSerializer(read_only=True)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = FuneralCase
        fields = [
            'id', 'case_number', 'deceased', 'status', 
            'scheduled_date', 'venue', 'total_cost'
        ]
        read_only_fields = ['id', 'case_number', 'total_cost']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    case = FuneralCaseSerializer(read_only=True)
    balance_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'case', 'total_amount',
            'amount_paid', 'balance_due', 'status', 'due_date'
        ]
        read_only_fields = ['id', 'invoice_number', 'balance_due']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    class Meta:
        model = Payment
        fields = [
            'id', 'receipt_number', 'amount', 'payment_method',
            'status', 'payment_date', 'transaction_reference'
        ]
        read_only_fields = ['id', 'receipt_number', 'payment_date']


class InventoryItemSerializer(serializers.ModelSerializer):
    """Serializer for InventoryItem model."""
    is_low_stock = serializers.BooleanField(read_only=True)
    stock_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'item_code', 'name', 'category', 'quantity_in_stock',
            'reorder_level', 'unit_cost', 'is_low_stock', 'stock_value'
        ]
        read_only_fields = ['id', 'is_low_stock', 'stock_value']
