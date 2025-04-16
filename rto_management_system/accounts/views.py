from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import (CustomAuthenticationForm, CitizenRegistrationForm, 
                    OfficerRegistrationForm, UserProfileUpdateForm, 
                    CitizenProfileUpdateForm)
from .models import User


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # This is email in our case
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.email}!")
                
                # Redirect based on user type
                if user.user_type == 'CITIZEN':
                    return redirect('citizen_dashboard')
                elif user.user_type == 'OFFICER':
                    return redirect('officer_dashboard')
                elif user.user_type == 'ADMIN':
                    return redirect('admin_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def register_citizen(request):
    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CitizenRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')
def register_officer(request):
    if request.method == 'POST':
        form = OfficerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Officer account for {user.email} created successfully!")
            return redirect('admin_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = OfficerRegistrationForm()
    
    return render(request, 'accounts/register_officer.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')


@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        
        if request.user.user_type == 'CITIZEN':
            profile_form = CitizenProfileUpdateForm(request.POST, instance=request.user.citizen_profile)
        else:
            profile_form = None
        
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    else:
        user_form = UserProfileUpdateForm(instance=request.user)
        
        if request.user.user_type == 'CITIZEN':
            try:
                profile_form = CitizenProfileUpdateForm(instance=request.user.citizen_profile)
            except:
                profile_form = None
        else:
            profile_form = None
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'accounts/update_profile.html', context)
