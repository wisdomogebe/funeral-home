"""
Inventory management views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import F
from fhms.utils.rbac import role_required, inventory_manager_required
from fhms.models import InventoryItem, InventoryTransaction
from fhms.forms import InventoryItemForm, InventoryAdjustmentForm
from fhms.services.inventory_service import InventoryService
from fhms.utils.audit import log_action


@login_required(login_url='login')
@role_required('admin', 'inventory_manager')
@require_http_methods(['GET'])
def inventory_list(request):
    """List all inventory items."""
    page = request.GET.get('page', 1)
    category_filter = request.GET.get('category', '')
    search = request.GET.get('search', '')
    low_stock_only = request.GET.get('low_stock', False)
    
    queryset = InventoryItem.objects.filter(is_active=True)
    
    if category_filter:
        queryset = queryset.filter(category=category_filter)
    
    if search:
        queryset = queryset.filter(name__icontains=search) | queryset.filter(item_code__icontains=search)
    
    if low_stock_only:
        queryset = queryset.filter(quantity_in_stock__lte=F('reorder_level'))
    
    queryset = queryset.order_by('name')
    paginator = Paginator(queryset, 15)
    page_obj = paginator.get_page(page)
    
    # Get inventory summary
    summary = InventoryService.get_inventory_summary()
    
    context = {
        'items': page_obj,
        'categories': InventoryItem.CATEGORY_CHOICES,
        'category_filter': category_filter,
        'search': search,
        'low_stock_only': low_stock_only,
        'summary': summary
    }
    return render(request, 'inventory/list.html', context)


@login_required(login_url='login')
@role_required('admin', 'inventory_manager')
@require_http_methods(['GET', 'POST'])
def inventory_create(request):
    """Create a new inventory item."""
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            log_action(request.user, 'CREATE', 'InventoryItem', item.id,
                      f'Created inventory item {item.name}', request)
            messages.success(request, f'Inventory item {item.name} created.')
            return redirect('fhms:inventory_detail', pk=item.id)
    else:
        form = InventoryItemForm()
    
    return render(request, 'inventory/form.html', {'form': form, 'action': 'Create'})


@login_required(login_url='login')
@role_required('admin', 'inventory_manager')
@require_http_methods(['GET'])
def inventory_detail(request, pk):
    """View inventory item details."""
    item = get_object_or_404(InventoryItem, id=pk)
    transactions = InventoryService.get_transaction_history(pk, limit=20)
    
    context = {
        'item': item,
        'transactions': transactions,
        'is_low_stock': item.is_low_stock,
        'stock_value': item.stock_value
    }
    return render(request, 'inventory/detail.html', context)


@login_required(login_url='login')
@role_required('admin', 'inventory_manager')
@require_http_methods(['GET', 'POST'])
def inventory_update(request, pk):
    """Update inventory item."""
    item = get_object_or_404(InventoryItem, id=pk)
    
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            log_action(request.user, 'UPDATE', 'InventoryItem', item.id,
                      f'Updated inventory item {item.name}', request)
            messages.success(request, 'Item updated.')
            return redirect('fhms:inventory_detail', pk=item.id)
    else:
        form = InventoryItemForm(instance=item)
    
    return render(request, 'inventory/form.html', {'form': form, 'action': 'Update', 'item': item})


@login_required(login_url='login')
@role_required('admin', 'inventory_manager')
@require_http_methods(['GET', 'POST'])
def inventory_adjust(request, pk):
    """Adjust inventory stock (add or remove)."""
    item = get_object_or_404(InventoryItem, id=pk)
    
    if request.method == 'POST':
        form = InventoryAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment_type = form.cleaned_data['adjustment_type']
            quantity = form.cleaned_data['quantity']
            reason = form.cleaned_data.get('reason', '')
            
            try:
                if adjustment_type == 'add':
                    InventoryService.add_stock(pk, quantity, reason or 'Manual adjustment')
                    messages.success(request, f'Added {quantity} units to {item.name}.')
                else:
                    InventoryService.remove_stock(pk, quantity, reason or 'Manual adjustment')
                    messages.success(request, f'Removed {quantity} units from {item.name}.')
                
                log_action(request.user, 'UPDATE', 'InventoryItem', item.id,
                          f'{adjustment_type.capitalize()} {quantity} units', request)
                
                return redirect('fhms:inventory_detail', pk=pk)
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = InventoryAdjustmentForm()
    
    context = {
        'form': form,
        'item': item,
        'action': 'Adjust Stock'
    }
    return render(request, 'inventory/adjust.html', context)


@login_required(login_url='login')
@role_required('admin', 'inventory_manager')
@require_http_methods(['GET'])
def low_stock_alert(request):
    """Display low stock warnings."""
    low_stock_items = InventoryService.get_low_stock_items()
    
    context = {
        'items': low_stock_items,
        'count': low_stock_items.count()
    }
    return render(request, 'inventory/low_stock_alert.html', context)


@login_required(login_url='login')
@role_required('admin', 'inventory_manager')
@require_http_methods(['GET'])
def inventory_report(request):
    """Generate inventory report."""
    report = InventoryService.get_inventory_summary()
    
    context = {
        'report': report,
        'categories_list': InventoryItem.CATEGORY_CHOICES
    }
    return render(request, 'inventory/report.html', context)
