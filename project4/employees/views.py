from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Employee
from .forms import EmployeeForm
from django.utils import timezone

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome back! You have successfully logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    
    return render(request, 'login.html')

@login_required
def dashboard(request):
    # Get dashboard statistics
    total_employees = Employee.objects.count()
    positions = Employee.objects.values('position').distinct().count()
    recent_hires = Employee.objects.filter(hire_date__month=timezone.now().month).count()
    
    context = {
        'total_employees': total_employees,
        'positions': positions,
        'recent_hires': recent_hires,
    }
    return render(request, 'dashboard.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

@login_required
def employee_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        employees = Employee.objects.filter(
            Q(name__icontains=search_query) |
            Q(position__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    else:
        employees = Employee.objects.all()
    return render(request, 'employees/employee_list.html', {'employees': employees})

@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee created successfully!')
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employees/employee_form.html', {'form': form, 'action': 'Create'})

@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/employee_form.html', {'form': form, 'action': 'Update'})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})
