"""
Database models for MemorialCare FHMS.
Defines all main entities: Users, Cases, Inventory, Payments, etc.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Supports multiple roles: Administrator, Funeral Director, Accountant, Inventory Manager, Family Client.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('director', 'Funeral Director'),
        ('accountant', 'Accountant'),
        ('inventory_manager', 'Inventory Manager'),
        ('family_client', 'Family Client'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='family_client')
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active_user = models.BooleanField(default=True, help_text="Indicates if the user account is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Override related names to avoid clashes with default User model
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='customuser_set',
        related_query_name='customuser'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='customuser_set',
        related_query_name='customuser'
    )
    
    class Meta:
        db_table = 'custom_users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def has_role(self, role):
        """Check if user has a specific role."""
        return self.role == role
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_director(self):
        return self.role == 'director'
    
    @property
    def is_accountant(self):
        return self.role == 'accountant'
    
    @property
    def is_inventory_manager(self):
        return self.role == 'inventory_manager'
    
    @property
    def is_family_client(self):
        return self.role == 'family_client'


class Deceased(models.Model):
    """
    Model for storing deceased persons' information.
    Contains personal details and medical information.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    date_of_death = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    identity_number = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    cause_of_death = models.CharField(max_length=255, blank=True)
    medical_notes = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='deceased_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'deceased'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class NextOfKin(models.Model):
    """
    Model for storing next-of-kin information related to a deceased.
    Tracks family relationships and contact details.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deceased = models.OneToOneField(Deceased, on_delete=models.CASCADE, related_name='next_of_kin')
    full_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'next_of_kin'
    
    def __str__(self):
        return f"{self.full_name} ({self.relationship})"


class ServiceType(models.Model):
    """
    Model for funeral service types offered by the home.
    Examples: Funeral Service, Wake Keeping, Graveside Service, etc.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    base_cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_types'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class FuneralCase(models.Model):
    """
    Model representing a funeral case/arrangement.
    Links deceased, services, staff, and payments.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deceased = models.OneToOneField(Deceased, on_delete=models.PROTECT, related_name='funeral_case')
    case_number = models.CharField(max_length=50, unique=True)
    client_family = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, 
                                      limit_choices_to={'role': 'family_client'},
                                      related_name='funeral_cases')
    funeral_director = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                        limit_choices_to={'role': 'director'},
                                        related_name='directed_cases')
    assigned_staff = models.ManyToManyField(CustomUser, blank=True, related_name='assigned_cases',
                                           limit_choices_to={'role__in': ['director', 'admin']})
    services = models.ManyToManyField(ServiceType, through='CaseService')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_date = models.DateTimeField()
    venue = models.CharField(max_length=255)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'funeral_cases'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Case {self.case_number} - {self.deceased.full_name}"
    
    @property
    def total_cost(self):
        """Calculate total cost of all services in the case."""
        return sum(cs.cost for cs in self.caseservice_set.all())


class CaseService(models.Model):
    """
    Intermediate model linking FuneralCase with ServiceType.
    Stores service-specific arrangement details and costs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(FuneralCase, on_delete=models.CASCADE)
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT)
    cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'case_services'
        unique_together = ('case', 'service_type')
    
    def __str__(self):
        return f"{self.case.case_number} - {self.service_type.name}"


class InventoryItem(models.Model):
    """
    Model for funeral home inventory items.
    Tracks caskets, equipment, flowers, accessories, etc.
    """
    CATEGORY_CHOICES = [
        ('casket', 'Caskets'),
        ('equipment', 'Equipment'),
        ('flower', 'Flowers'),
        ('accessory', 'Accessories'),
        ('cloth', 'Cloth Materials'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    quantity_in_stock = models.IntegerField(validators=[MinValueValidator(0)])
    reorder_level = models.IntegerField(validators=[MinValueValidator(0)], help_text="Minimum stock level before alert")
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    supplier = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory_items'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.item_code})"
    
    @property
    def is_low_stock(self):
        """Check if item is below reorder level."""
        return self.quantity_in_stock <= self.reorder_level
    
    @property
    def stock_value(self):
        """Calculate total value of stock for this item."""
        return self.quantity_in_stock * self.unit_cost
    
    def add_stock(self, quantity, reason=""):
        """Add stock to inventory."""
        self.quantity_in_stock += quantity
        self.save()
        InventoryTransaction.objects.create(
            item=self,
            transaction_type='addition',
            quantity=quantity,
            reason=reason or 'Stock addition'
        )
    
    def remove_stock(self, quantity, reason=""):
        """Remove stock from inventory."""
        if quantity > self.quantity_in_stock:
            raise ValueError("Insufficient stock")
        self.quantity_in_stock -= quantity
        self.save()
        InventoryTransaction.objects.create(
            item=self,
            transaction_type='removal',
            quantity=quantity,
            reason=reason or 'Stock removal'
        )


class InventoryTransaction(models.Model):
    """
    Audit trail for inventory movements.
    Tracks all additions, removals, and adjustments.
    """
    TRANSACTION_TYPE_CHOICES = [
        ('addition', 'Addition'),
        ('removal', 'Removal'),
        ('adjustment', 'Adjustment'),
        ('damage', 'Damage/Loss'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    reason = models.TextField(blank=True)
    performed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.item.name} - {self.get_transaction_type_display()}"


class Invoice(models.Model):
    """
    Model for funeral service invoices.
    Generated for funeral cases and tracks all charges.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True)
    case = models.OneToOneField(FuneralCase, on_delete=models.PROTECT, related_name='invoice')
    client = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    due_date = models.DateField()
    notes = models.TextField(blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    @property
    def balance_due(self):
        """Calculate remaining balance."""
        return self.total_amount - self.amount_paid
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue."""
        return timezone.now().date() > self.due_date and self.status != 'paid'


class Payment(models.Model):
    """
    Model for tracking payments made towards invoices.
    Stores transaction details and payment gateway information.
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('cheque', 'Cheque'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_reference = models.CharField(max_length=255, blank=True, help_text="External transaction ID")
    receipt_number = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment {self.receipt_number}"


class AuditLog(models.Model):
    """
    Audit trail for critical actions in the system.
    Tracks user actions for compliance and troubleshooting.
    """
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('PAYMENT', 'Payment'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('ACCESS_DENIED', 'Access Denied'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} on {self.model_name} by {self.user}"


class Report(models.Model):
    """
    Model for storing generated reports.
    Supports both operational and financial reports.
    """
    REPORT_TYPE_CHOICES = [
        ('operational', 'Operational Report'),
        ('financial', 'Financial Report'),
        ('inventory', 'Inventory Report'),
        ('case_summary', 'Case Summary Report'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    generated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    data = models.JSONField(help_text="Report data stored as JSON")
    file = models.FileField(upload_to='reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title}"
