"""
Inventory Management Service
Handles inventory tracking, stock management, and low-stock alerts.
"""
from decimal import Decimal
from django.db.models import F, Sum, DecimalField
from fhms.models import InventoryItem, InventoryTransaction
from fhms.utils.audit import log_action


class InventoryService:
    """Service for managing inventory."""
    
    @staticmethod
    def create_inventory_item(item_code, name, category, quantity, reorder_level, 
                             unit_cost, description="", supplier=""):
        """
        Create a new inventory item.
        
        Args:
            item_code: Unique item identifier
            name: Item name
            category: Item category
            quantity: Initial quantity
            reorder_level: Reorder threshold
            unit_cost: Cost per unit
            description: Item description
            supplier: Supplier name
            
        Returns:
            InventoryItem instance
        """
        item = InventoryItem.objects.create(
            item_code=item_code,
            name=name,
            category=category,
            quantity_in_stock=quantity,
            reorder_level=reorder_level,
            unit_cost=unit_cost,
            description=description,
            supplier=supplier
        )
        
        log_action(None, 'CREATE', 'InventoryItem', item.id,
                  f'Created inventory item {name} with initial quantity {quantity}')
        return item
    
    @staticmethod
    def add_stock(item_id, quantity, reason="Restocking"):
        """
        Add stock to an inventory item.
        
        Args:
            item_id: UUID of the inventory item
            quantity: Quantity to add
            reason: Reason for addition
            
        Returns:
            InventoryItem instance
        """
        try:
            item = InventoryItem.objects.select_for_update().get(id=item_id)
            
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            item.quantity_in_stock += quantity
            item.save()
            
            # Log the transaction
            InventoryTransaction.objects.create(
                item=item,
                transaction_type='addition',
                quantity=quantity,
                reason=reason
            )
            
            log_action(None, 'UPDATE', 'InventoryItem', item.id,
                      f'Added {quantity} units to {item.name}')
            
            return item
        except InventoryItem.DoesNotExist:
            raise ValueError("Inventory item not found")
    
    @staticmethod
    def remove_stock(item_id, quantity, reason="Item used"):
        """
        Remove stock from an inventory item.
        
        Args:
            item_id: UUID of the inventory item
            quantity: Quantity to remove
            reason: Reason for removal
            
        Returns:
            InventoryItem instance
        """
        try:
            item = InventoryItem.objects.select_for_update().get(id=item_id)
            
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            if item.quantity_in_stock < quantity:
                raise ValueError(f"Insufficient stock. Available: {item.quantity_in_stock}")
            
            item.quantity_in_stock -= quantity
            item.save()
            
            # Log the transaction
            InventoryTransaction.objects.create(
                item=item,
                transaction_type='removal',
                quantity=quantity,
                reason=reason
            )
            
            log_action(None, 'UPDATE', 'InventoryItem', item.id,
                      f'Removed {quantity} units from {item.name}')
            
            return item
        except InventoryItem.DoesNotExist:
            raise ValueError("Inventory item not found")
    
    @staticmethod
    def get_low_stock_items():
        """Get all items that are below reorder level."""
        return InventoryItem.objects.filter(
            quantity_in_stock__lte=F('reorder_level'),
            is_active=True
        ).order_by('quantity_in_stock')
    
    @staticmethod
    def get_inventory_value():
        """Calculate total value of current inventory."""
        result = InventoryItem.objects.aggregate(
            total_value=Sum(
                F('quantity_in_stock') * F('unit_cost'),
                output_field=DecimalField()
            )
        )
        return result['total_value'] or Decimal('0.00')
    
    @staticmethod
    def get_inventory_by_category(category):
        """Get all items in a specific category."""
        return InventoryItem.objects.filter(category=category, is_active=True).order_by('name')
    
    @staticmethod
    def get_inventory_summary():
        """Get a summary of inventory status."""
        total_items = InventoryItem.objects.filter(is_active=True).count()
        low_stock_items = InventoryItem.objects.filter(
            quantity_in_stock__lte=F('reorder_level'),
            is_active=True
        ).count()
        
        total_value = InventoryItem.objects.aggregate(
            total_value=Sum(
                F('quantity_in_stock') * F('unit_cost'),
                output_field=DecimalField()
            )
        )['total_value'] or Decimal('0.00')
        
        return {
            'total_items': total_items,
            'low_stock_count': low_stock_items,
            'total_value': total_value,
            'categories': InventoryItem.CATEGORY_CHOICES
        }
    
    @staticmethod
    def update_item(item_id, **kwargs):
        """Update inventory item fields."""
        try:
            item = InventoryItem.objects.get(id=item_id)
            
            allowed_fields = ['name', 'description', 'reorder_level', 'unit_cost', 'supplier', 'is_active']
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(item, field, value)
            
            item.save()
            log_action(None, 'UPDATE', 'InventoryItem', item.id, f'Updated inventory item {item.name}')
            return item
        except InventoryItem.DoesNotExist:
            raise ValueError("Inventory item not found")
    
    @staticmethod
    def get_transaction_history(item_id, limit=50):
        """Get transaction history for an item."""
        try:
            item = InventoryItem.objects.get(id=item_id)
            return InventoryTransaction.objects.filter(item=item).order_by('-created_at')[:limit]
        except InventoryItem.DoesNotExist:
            return []
