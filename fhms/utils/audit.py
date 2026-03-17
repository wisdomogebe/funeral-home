"""
Audit logging utilities for tracking system actions.
"""
from fhms.models import AuditLog


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_action(user, action, model_name, object_id, description, request=None):
    """
    Log a user action to the audit trail.
    
    Args:
        user: The user performing the action
        action: Type of action (CREATE, UPDATE, DELETE, etc.)
        model_name: Name of the model affected
        object_id: ID of the affected object
        description: Detailed description of the action
        request: The HTTP request (optional, for IP logging)
    """
    ip_address = None
    if request:
        ip_address = get_client_ip(request)
    
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=str(object_id),
        description=description,
        ip_address=ip_address
    )


def log_access_denied(user, view_name, request=None):
    """Log unauthorized access attempts."""
    ip_address = None
    if request:
        ip_address = get_client_ip(request)
    
    AuditLog.objects.create(
        user=user,
        action='ACCESS_DENIED',
        model_name='View',
        object_id=view_name,
        description=f'Unauthorized access attempt to {view_name}',
        ip_address=ip_address
    )


def log_login(user, request):
    """Log user login."""
    log_action(user, 'LOGIN', 'User', user.id, f'User logged in', request)


def log_logout(user, request):
    """Log user logout."""
    log_action(user, 'LOGOUT', 'User', user.id, f'User logged out', request)
