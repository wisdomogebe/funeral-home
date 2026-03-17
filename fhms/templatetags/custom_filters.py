"""Custom template filters for inventory and other features."""
from django import template

register = template.Library()


@register.filter
def as_percentage(value):
    """Convert a number to a percentage (0-100 scale)."""
    try:
        return int(value * 100) if 0 <= value <= 1 else int(value)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage_of(value, max_value):
    """Calculate value as a percentage of max_value."""
    try:
        if max_value == 0:
            return 0
        return int((float(value) / float(max_value)) * 100)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
