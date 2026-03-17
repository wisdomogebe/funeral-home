"""
Deceased and Funeral Case management views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from fhms.utils.rbac import role_required, director_required
from fhms.models import Deceased, FuneralCase, NextOfKin, CaseService
from fhms.forms import DeceasedForm, NextOfKinForm, FuneralCaseForm, CaseServiceForm
from fhms.services.case_service import CaseService as CaseServiceLogic
from fhms.utils.audit import log_action


# ============ DECEASED MANAGEMENT ============

@login_required(login_url='login')
@role_required('admin', 'director')
@require_http_methods(['GET'])
def deceased_list(request):
    """List all deceased records."""
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '')
    
    queryset = Deceased.objects.all()
    
    if search:
        queryset = queryset.filter(
            first_name__icontains=search
        ) | queryset.filter(
            last_name__icontains=search
        ) | queryset.filter(
            identity_number__icontains=search
        )
    
    queryset = queryset.order_by('-created_at')
    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(page)
    
    context = {
        'deceased_list': page_obj,
        'search': search,
        'paginator': paginator
    }
    return render(request, 'deceased/list.html', context)


@login_required(login_url='login')
@role_required('admin', 'director')
@require_http_methods(['GET', 'POST'])
def deceased_create(request):
    """Create a new deceased record."""
    if request.method == 'POST':
        form = DeceasedForm(request.POST, request.FILES)
        if form.is_valid():
            deceased = form.save()
            log_action(request.user, 'CREATE', 'Deceased', deceased.id,
                      f'Created deceased record for {deceased.full_name}', request)
            messages.success(request, f'Deceased record created for {deceased.full_name}.')
            return redirect('deceased_detail', pk=deceased.id)
    else:
        form = DeceasedForm()
    
    return render(request, 'deceased/form.html', {'form': form, 'action': 'Create'})


@login_required(login_url='login')
@role_required('admin', 'director')
@require_http_methods(['GET'])
def deceased_detail(request, pk):
    """View deceased details."""
    deceased = get_object_or_404(Deceased, id=pk)
    next_of_kin = deceased.next_of_kin if hasattr(deceased, 'next_of_kin') else None
    funeral_case = deceased.funeral_case if hasattr(deceased, 'funeral_case') else None
    
    context = {
        'deceased': deceased,
        'next_of_kin': next_of_kin,
        'funeral_case': funeral_case
    }
    return render(request, 'deceased/detail.html', context)


@login_required(login_url='login')
@role_required('admin', 'director')
@require_http_methods(['GET', 'POST'])
def deceased_update(request, pk):
    """Update deceased record."""
    deceased = get_object_or_404(Deceased, id=pk)
    
    if request.method == 'POST':
        form = DeceasedForm(request.POST, request.FILES, instance=deceased)
        if form.is_valid():
            deceased = form.save()
            log_action(request.user, 'UPDATE', 'Deceased', deceased.id,
                      f'Updated deceased record for {deceased.full_name}', request)
            messages.success(request, 'Deceased record updated.')
            return redirect('fhms:deceased_detail', pk=deceased.id)
    else:
        form = DeceasedForm(instance=deceased)
    
    return render(request, 'deceased/form.html', {'form': form, 'action': 'Update'})


# ============ NEXT OF KIN MANAGEMENT ============

@login_required(login_url='login')
@role_required('admin', 'director')
@require_http_methods(['GET', 'POST'])
def next_of_kin_create(request, deceased_id):
    """Create next-of-kin record."""
    deceased = get_object_or_404(Deceased, id=deceased_id)
    
    if request.method == 'POST':
        form = NextOfKinForm(request.POST)
        if form.is_valid():
            kin = form.save(commit=False)
            kin.deceased = deceased
            kin.save()
            log_action(request.user, 'CREATE', 'NextOfKin', kin.id,
                      f'Added next-of-kin {kin.full_name} for {deceased.full_name}', request)
            messages.success(request, 'Next of kin record created.')
            return redirect('deceased_detail', pk=deceased.id)
    else:
        form = NextOfKinForm()
    
    context = {'form': form, 'deceased': deceased, 'action': 'Create'}
    return render(request, 'next_of_kin/form.html', context)


@login_required(login_url='login')
@role_required('admin', 'director')
@require_http_methods(['GET', 'POST'])
def next_of_kin_update(request, pk):
    """Update next-of-kin record."""
    kin = get_object_or_404(NextOfKin, id=pk)
    
    if request.method == 'POST':
        form = NextOfKinForm(request.POST, instance=kin)
        if form.is_valid():
            kin = form.save()
            log_action(request.user, 'UPDATE', 'NextOfKin', kin.id,
                      f'Updated next-of-kin {kin.full_name}', request)
            messages.success(request, 'Next of kin record updated.')
            return redirect('deceased_detail', pk=kin.deceased.id)
    else:
        form = NextOfKinForm(instance=kin)
    
    context = {'form': form, 'kin': kin, 'action': 'Update'}
    return render(request, 'next_of_kin/form.html', context)


# ============ FUNERAL CASE MANAGEMENT ============

@login_required(login_url='login')
@role_required('admin', 'director', 'family_client')
@require_http_methods(['GET'])
def case_list(request):
    """List funeral cases with filters."""
    page = request.GET.get('page', 1)
    status_filter = request.GET.get('status', '')
    
    queryset = FuneralCase.objects.all()
    
    # Family clients see only their cases
    if request.user.is_family_client:
        queryset = queryset.filter(client_family=request.user)
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    queryset = queryset.order_by('-created_at')
    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(page)
    
    context = {
        'case_list': page_obj,
        'status_filter': status_filter,
        'status_choices': FuneralCase.STATUS_CHOICES
    }
    return render(request, 'case/list.html', context)


@login_required(login_url='login')
@role_required('admin', 'director')
@require_http_methods(['GET', 'POST'])
def case_create(request):
    """Create a new funeral case."""
    if request.method == 'POST':
        form = FuneralCaseForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            case.case_number = CaseServiceLogic.generate_case_number()
            case.save()
            form.save_m2m()
            
            log_action(request.user, 'CREATE', 'FuneralCase', case.id,
                      f'Created case {case.case_number}', request)
            messages.success(request, f'Funeral case {case.case_number} created.')
            return redirect('case_detail', pk=case.id)
    else:
        form = FuneralCaseForm()
    
    return render(request, 'case/form.html', {'form': form, 'action': 'Create'})


@login_required(login_url='login')
@role_required('admin', 'director', 'family_client')
@require_http_methods(['GET'])
def case_detail(request, pk):
    """View funeral case details."""
    case = get_object_or_404(FuneralCase, id=pk)
    
    # Check access
    if request.user.is_family_client and case.client_family != request.user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    services = case.caseservice_set.all()
    invoice = case.invoice if hasattr(case, 'invoice') else None
    
    context = {
        'case': case,
        'deceased': case.deceased,
        'services': services,
        'invoice': invoice,
        'total_cost': case.total_cost
    }
    return render(request, 'case/detail.html', context)


@login_required(login_url='login')
@role_required('admin', 'director')
@require_http_methods(['GET', 'POST'])
def case_update(request, pk):
    """Update funeral case."""
    case = get_object_or_404(FuneralCase, id=pk)
    
    if request.method == 'POST':
        form = FuneralCaseForm(request.POST, instance=case)
        if form.is_valid():
            case = form.save()
            log_action(request.user, 'UPDATE', 'FuneralCase', case.id,
                      f'Updated case {case.case_number}', request)
            messages.success(request, 'Case updated.')
            return redirect('fhms:case_detail', pk=case.id)
    else:
        form = FuneralCaseForm(instance=case)
    
    return render(request, 'case/form.html', {'form': form, 'action': 'Update', 'case': case})


@login_required(login_url='login')
@role_required('admin', 'director')
@require_http_methods(['POST'])
def case_add_service(request, pk):
    """Add a service to a funeral case."""
    case = get_object_or_404(FuneralCase, id=pk)
    
    if request.method == 'POST':
        form = CaseServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.case = case
            service.save()
            log_action(request.user, 'CREATE', 'CaseService', service.id,
                      f'Added service to case {case.case_number}', request)
            messages.success(request, 'Service added to case.')
            return redirect('case_detail', pk=case.id)
    
    return redirect('case_detail', pk=case.id)
