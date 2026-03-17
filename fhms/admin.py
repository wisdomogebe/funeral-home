"""
Django admin configuration for FHMS models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    CustomUser, Deceased, NextOfKin, ServiceType, FuneralCase, CaseService,
    InventoryItem, InventoryTransaction, Invoice, Payment, AuditLog, Report
)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin for custom user model."""
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'is_active_user')}),
    )
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')


@admin.register(Deceased)
class DeceasedAdmin(admin.ModelAdmin):
    """Admin for Deceased model."""
    list_display = ('full_name', 'date_of_death', 'gender', 'identity_number')
    list_filter = ('gender', 'created_at')
    search_fields = ('first_name', 'last_name', 'identity_number')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(NextOfKin)
class NextOfKinAdmin(admin.ModelAdmin):
    """Admin for NextOfKin model."""
    list_display = ('full_name', 'relationship', 'deceased', 'email', 'phone')
    search_fields = ('full_name', 'email', 'phone')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    """Admin for ServiceType model."""
    list_display = ('name', 'base_cost', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)


@admin.register(FuneralCase)
class FuneralCaseAdmin(admin.ModelAdmin):
    """Admin for FuneralCase model."""
    list_display = ('case_number', 'deceased', 'status', 'scheduled_date')
    list_filter = ('status', 'created_at')
    search_fields = ('case_number', 'deceased__first_name', 'deceased__last_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    filter_horizontal = ('assigned_staff',)


@admin.register(CaseService)
class CaseServiceAdmin(admin.ModelAdmin):
    """Admin for CaseService model."""
    list_display = ('case', 'service_type', 'cost')
    search_fields = ('case__case_number',)
    readonly_fields = ('id',)


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    """Admin for InventoryItem model."""
    list_display = ('name', 'item_code', 'category', 'quantity_in_stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'item_code')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    """Admin for InventoryTransaction model."""
    list_display = ('item', 'transaction_type', 'quantity', 'performed_by', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('item__name',)
    readonly_fields = ('id', 'created_at')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin for Invoice model."""
    list_display = ('invoice_number', 'case', 'total_amount', 'status', 'due_date')
    list_filter = ('status', 'created_at')
    search_fields = ('invoice_number', 'case__case_number')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payment model."""
    list_display = ('receipt_number', 'invoice', 'amount', 'payment_method', 'status')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('receipt_number', 'transaction_reference')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin for AuditLog model."""
    list_display = ('user', 'action', 'model_name', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__email', 'model_name')
    readonly_fields = ('id', 'created_at')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin for Report model."""
    list_display = ('title', 'report_type', 'generated_by', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('title',)
    readonly_fields = ('id', 'created_at')
