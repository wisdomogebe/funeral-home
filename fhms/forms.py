"""
Django forms for user input and validation.
Implements forms for all major entities in the FHMS.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (
    CustomUser, Deceased, NextOfKin, ServiceType, FuneralCase, CaseService,
    InventoryItem, Invoice, Payment
)


class CustomUserCreationForm(UserCreationForm):
    """Form for self-registration of new users (family clients)."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone = forms.CharField(max_length=20, required=False)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone', 'password1', 'password2')
    
    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class CustomUserChangeForm(UserChangeForm):
    """Form for updating user information."""
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone', 'role', 'is_active')


class CustomUserUpdateForm(forms.ModelForm):
    """Form for users to update their profile."""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class DeceasedForm(forms.ModelForm):
    """Form for creating and updating deceased records."""
    class Meta:
        model = Deceased
        fields = ('first_name', 'last_name', 'date_of_birth', 'date_of_death', 
                  'gender', 'identity_number', 'address', 'cause_of_death', 
                  'medical_notes', 'photo')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_death': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'identity_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Identity Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cause_of_death': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cause of Death'}),
            'medical_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class NextOfKinForm(forms.ModelForm):
    """Form for creating and updating next-of-kin information."""
    class Meta:
        model = NextOfKin
        fields = ('full_name', 'relationship', 'email', 'phone', 'address')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Relationship'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ServiceTypeForm(forms.ModelForm):
    """Form for creating and updating service types."""
    class Meta:
        model = ServiceType
        fields = ('name', 'description', 'base_cost', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'base_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FuneralCaseForm(forms.ModelForm):
    """Form for creating and updating funeral cases."""
    class Meta:
        model = FuneralCase
        fields = ('deceased', 'client_family', 'funeral_director', 'status', 
                  'scheduled_date', 'venue', 'special_requests')
        widgets = {
            'deceased': forms.Select(attrs={'class': 'form-control'}),
            'client_family': forms.Select(attrs={'class': 'form-control'}),
            'funeral_director': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CaseServiceForm(forms.ModelForm):
    """Form for adding services to a funeral case."""
    class Meta:
        model = CaseService
        fields = ('service_type', 'cost', 'notes')
        widgets = {
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class InventoryItemForm(forms.ModelForm):
    """Form for creating and updating inventory items."""
    class Meta:
        model = InventoryItem
        fields = ('item_code', 'name', 'description', 'category', 'quantity_in_stock',
                  'reorder_level', 'unit_cost', 'supplier', 'is_active')
        widgets = {
            'item_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Code'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier Name'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InventoryAdjustmentForm(forms.Form):
    """Form for adjusting inventory stock."""
    ADJUSTMENT_CHOICES = [
        ('add', 'Add Stock'),
        ('remove', 'Remove Stock'),
    ]
    
    adjustment_type = forms.ChoiceField(choices=ADJUSTMENT_CHOICES, widget=forms.RadioSelect)
    quantity = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    reason = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))


class InvoiceForm(forms.ModelForm):
    """Form for creating and updating invoices."""
    class Meta:
        model = Invoice
        fields = ('case', 'due_date', 'tax_amount', 'notes')
        widgets = {
            'case': forms.Select(attrs={'class': 'form-control'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PaymentForm(forms.ModelForm):
    """Form for recording payments."""
    class Meta:
        model = Payment
        fields = ('invoice', 'amount', 'payment_method', 'transaction_reference', 'notes')
        widgets = {
            'invoice': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transaction_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction Reference'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class LoginForm(forms.Form):
    """Custom login form."""
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
