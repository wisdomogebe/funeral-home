"""
Authentication views for login, logout, registration, and profile management.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from fhms.forms import LoginForm, CustomUserCreationForm, CustomUserUpdateForm
from fhms.models import CustomUser
from fhms.utils.audit import log_login, log_logout


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Try to authenticate
            try:
                user = CustomUser.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None and user.is_active_user:
                    login(request, user)
                    log_login(user, request)
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid credentials or account is inactive.')
            except CustomUser.DoesNotExist:
                messages.error(request, 'Invalid credentials.')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


@require_http_methods(['GET'])
@login_required(login_url='login')
def logout_view(request):
    """Handle user logout."""
    log_logout(request.user, request)
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@require_http_methods(['GET', 'POST'])
def register_view(request):
    """Handle user registration (family clients only initially)."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Family clients can self-register
            user = form.save(commit=False)
            user.role = 'family_client'  # Only family clients can self-register
            user.save()
            
            # Auto-login after registration
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to MemorialCare.')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})


@login_required(login_url='login')
def profile_view(request):
    """Display user profile."""
    user = request.user
    context = {
        'user': user,
        'role_display': user.get_role_display()
    }
    return render(request, 'auth/profile.html', context)


@require_http_methods(['GET', 'POST'])
@login_required(login_url='login')
def profile_edit_view(request):
    """Edit user profile."""
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)
    
    return render(request, 'auth/profile_edit.html', {'form': form})


def home_view(request):
    """Landing page view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    return render(request, 'home.html')
