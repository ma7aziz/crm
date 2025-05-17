from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from .forms import SignUpForm, CustomerForm, InteractionForm, LoginForm, AdminUserCreationForm
from .models import Customer, Interaction
from django.http import HttpResponseRedirect

def is_admin(user):
    return user.is_staff or user.is_superuser

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


@login_required
def dashboard_view(request):
    customers = Customer.objects.all()
    recent_interactions = Interaction.objects.order_by('-date')[:5]
    
    # Customer status counts for dashboard charts
    lead_count = Customer.objects.filter(status=Customer.LEAD).count()
    opportunity_count = Customer.objects.filter(status=Customer.OPPORTUNITY).count()
    customer_count = Customer.objects.filter(status=Customer.CUSTOMER).count()
    archived_count = Customer.objects.filter(status=Customer.ARCHIVED).count()

    # Get customers assigned to current user
    if not request.user.is_staff and not request.user.is_superuser:
        customers = customers.filter(assigned_to=request.user)
    
    context = {
        'customers': customers,
        'recent_interactions': recent_interactions,
        'lead_count': lead_count,
        'opportunity_count': opportunity_count,
        'customer_count': customer_count,
        'archived_count': archived_count,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def customer_list_view(request):
    customers = Customer.objects.all()
    return render(request, 'core/customer_list.html', {'customers': customers})


@login_required
def customer_detail_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    interactions = customer.interactions.order_by('-date')
    
    if request.method == 'POST':
        interaction_form = InteractionForm(request.POST)
        if interaction_form.is_valid():
            interaction = interaction_form.save(commit=False)
            interaction.customer = customer
            interaction.created_by = request.user
            interaction.save()
            messages.success(request, "Interaction added successfully!")
            return redirect('customer_detail', pk=customer.pk)
    else:
        interaction_form = InteractionForm(initial={'customer': customer})
    
    context = {
        'customer': customer,
        'interactions': interactions,
        'interaction_form': interaction_form,
    }
    return render(request, 'core/customer_detail.html', context)


@login_required
def customer_create_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer created successfully!")
            return redirect('customer_list')
    else:
        form = CustomerForm()
    
    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Add Customer'})


@login_required
def customer_update_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated successfully!")
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Update Customer'})


@login_required
def customer_delete_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer.delete()
        messages.success(request, "Customer deleted successfully!")
        return redirect('customer_list')
    
    return render(request, 'core/customer_confirm_delete.html', {'customer': customer})


@login_required
def interaction_list_view(request):
    """View all interactions across customers"""
    interactions = Interaction.objects.all().order_by('-date')
    context = {
        'interactions': interactions,
        'title': 'All Interactions'
    }
    return render(request, 'core/interaction_list.html', context)


@login_required
def interaction_detail_view(request, pk):
    """View details of a specific interaction"""
    interaction = get_object_or_404(Interaction, pk=pk)
    context = {
        'interaction': interaction,
        'title': f"{interaction.get_interaction_type_display()} with {interaction.customer}"
    }
    return render(request, 'core/interaction_detail.html', context)


@login_required
def interaction_create_view(request, customer_id=None):
    """Create a new interaction, optionally pre-selecting a customer"""
    customer = None
    if customer_id:
        customer = get_object_or_404(Customer, pk=customer_id)
    
    if request.method == 'POST':
        form = InteractionForm(request.POST)
        if form.is_valid():
            interaction = form.save(commit=False)
            interaction.created_by = request.user
            interaction.save()
            messages.success(request, "Interaction recorded successfully!")
            
            # Redirect to customer detail if creating from customer page
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        initial_data = {}
        if customer:
            initial_data = {'customer': customer, 'date': timezone.now()}
        form = InteractionForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': f"Record Interaction{'with ' + customer.first_name + ' ' + customer.last_name if customer else ''}",
        'customer': customer
    }
    return render(request, 'core/interaction_form.html', context)


@login_required
def interaction_update_view(request, pk):
    """Edit an existing interaction"""
    interaction = get_object_or_404(Interaction, pk=pk)
    
    if request.method == 'POST':
        form = InteractionForm(request.POST, instance=interaction)
        if form.is_valid():
            form.save()
            messages.success(request, "Interaction updated successfully!")
            return redirect('interaction_detail', pk=interaction.pk)
    else:
        form = InteractionForm(instance=interaction)
    
    context = {
        'form': form,
        'interaction': interaction,
        'title': f"Edit {interaction.get_interaction_type_display()} with {interaction.customer}"
    }
    return render(request, 'core/interaction_form.html', context)


@login_required
def interaction_delete_view(request, pk):
    """Delete an existing interaction"""
    interaction = get_object_or_404(Interaction, pk=pk)
    customer = interaction.customer
    
    if request.method == 'POST':
        interaction.delete()
        messages.success(request, "Interaction deleted successfully!")
        return redirect('customer_detail', pk=customer.id)
    
    context = {
        'interaction': interaction,
        'title': f"Delete Interaction"
    }
    return render(request, 'core/interaction_confirm_delete.html', context)

# Admin-only user management views
@login_required
@user_passes_test(is_admin)
def user_list_view(request):
    """Admin view to list all users"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'core/user_list.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def user_create_view(request):
    """Admin view to create a new user"""
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User {user.username} created successfully!")
            return redirect('user_list')
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'core/user_form.html', {'form': form, 'title': 'Create New User'})


@login_required
@user_passes_test(is_admin)
def user_detail_view(request, pk):
    """Admin view to see user details and assigned customers"""
    user = get_object_or_404(User, pk=pk)
    assigned_customers = Customer.objects.filter(assigned_to=user)
    
    context = {
        'user_profile': user,  # Renamed to avoid template confusion with the request.user
        'assigned_customers': assigned_customers,
    }
    return render(request, 'core/user_detail.html', context)


@login_required
@user_passes_test(is_admin)
def user_update_view(request, pk):
    """Admin view to update a user's details"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        # Can't use the regular AdminUserCreationForm as it requires password
        # We'd need a custom form for updates, but we'll update fields directly for simplicity
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.is_staff = 'is_staff' in request.POST
        user.is_superuser = 'is_superuser' in request.POST
        user.save()
        
        messages.success(request, f"User {user.username} updated successfully!")
        return redirect('user_detail', pk=user.pk)
    
    context = {
        'user_profile': user,
    }
    return render(request, 'core/user_update_form.html', context)
