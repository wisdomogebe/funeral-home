"""
Role-based access control (RBAC) decorators and utilities.
Implements access control for different user roles.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from fhms.utils.audit import log_access_denied


def role_required(*allowed_roles):
    """
    Decorator to restrict view access to specific user roles.
    
    Usage:
        @role_required('admin', 'director')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Please log in to access this page.')
                return redirect('login')
            
            if request.user.role not in allowed_roles:
                log_access_denied(request.user, view_func.__name__)
                messages.error(request, 'You do not have permission to access this page.')
                return HttpResponseForbidden('Access Denied')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator to restrict view to administrators only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            log_access_denied(request.user, view_func.__name__)
            messages.error(request, 'Admin access required.')
            return HttpResponseForbidden('Admin access required')
        return view_func(request, *args, **kwargs)
    return wrapper


def director_required(view_func):
    """Decorator to restrict view to funeral directors."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_director:
            log_access_denied(request.user, view_func.__name__)
            messages.error(request, 'Funeral Director access required.')
            return HttpResponseForbidden('Access Denied')
        return view_func(request, *args, **kwargs)
    return wrapper


def accountant_required(view_func):
    """Decorator to restrict view to accountants."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_accountant:
            log_access_denied(request.user, view_func.__name__)
            messages.error(request, 'Accountant access required.')
            return HttpResponseForbidden('Access Denied')
        return view_func(request, *args, **kwargs)
    return wrapper


def inventory_manager_required(view_func):
    """Decorator to restrict view to inventory managers."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_inventory_manager:
            log_access_denied(request.user, view_func.__name__)
            messages.error(request, 'Inventory Manager access required.')
            return HttpResponseForbidden('Access Denied')
        return view_func(request, *args, **kwargs)
    return wrapper


def authenticated_required(view_func):
    """Decorator to require authentication."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to continue.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
