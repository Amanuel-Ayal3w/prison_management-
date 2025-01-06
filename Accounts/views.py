# accounts/views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from .forms import *
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.tokens import default_token_generator
from .tokens import account_activation_token
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str,force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden
from .forms import CustomUserCreationForm
from .models import CustomUser
import logging
from django.http import JsonResponse
from .models import *
from Court.models import *
from Appointment.models import Visitor, Appointment
from Court.models import Activity
from datetime import timedelta
from django.db.models import Count

@login_required
def dashboard(request):
    prisoners = Prisoner.objects.filter(prison=request.user.prison)
    officer = User.objects.filter(prison=request.user.prison)
    visitors = Visitor.objects.filter(prison=request.user.prison)
    appointments = Appointment.objects.filter(prison=request.user.prison)
    activities = Activity.objects.filter(prisoner__prison=request.user.prison)
    notfication = Notification.objects.filter(user=request.user, is_read=False)
    #prisoner by gender count
    male_prisoners_count = prisoners.filter(pri_gender='Male').count()
    female_prisoners_count = prisoners.filter(pri_gender='Female').count()
    # Discipline data
    disciplines = Discipline.objects.filter(prisoner__prison=request.user.prison)
    discipline_types = list(disciplines.values_list('discipline_type', flat=True).distinct())
    discipline_counts = [disciplines.filter(discipline_type=type).count() for type in discipline_types]
    # Visitors by day
    today = timezone.now().date()

    last_week = today - timedelta(days=7)
    visitors_by_day = Visitor.objects.filter(
    prison=request.user.prison, 
    visit_date__range=[last_week, today]
    ).values('visit_date').annotate(count=Count('id')).order_by('visit_date')
    visitor_days = [entry['visit_date'].strftime('%Y-%m-%d') for entry in visitors_by_day]
    visitor_counts = [entry['count'] for entry in visitors_by_day]

    #activity by type
    activities_by_type = activities.values('activity_type').annotate(count=Count('id')).order_by('activity_type')
    activity_types = [entry['activity_type'] for entry in activities_by_type]
    activity_counts = [entry['count'] for entry in activities_by_type]

    # Appointments by time slot
    appointments_by_time_slot = appointments.values('time_slot').annotate(count=Count('id')).order_by('time_slot')
    time_slots = [entry['time_slot'] for entry in appointments_by_time_slot]
    appointment_counts = [entry['count'] for entry in appointments_by_time_slot]

    context = {
        'prisoners': prisoners,
        'officer': officer,
        'visitors': visitors,
        'appointments': appointments,
        'activities': activities,
        'notfications': notfication,
        'male_prisoners_count': male_prisoners_count,
        'female_prisoners_count': female_prisoners_count,
        'discipline_types': discipline_types,
        'discipline_counts': discipline_counts,
        'visitor_days': visitor_days,
        'visitor_counts': visitor_counts,
        'activity_types': activity_types,
        'activity_counts': activity_counts,
        'time_slots': time_slots,
        'appointment_counts': appointment_counts,
    }

    return render(request, 'dashboard.html', context)

@login_required
def create_account(request):
    user = request.user
    officers = CustomUser.objects.filter(role__role='Officer',prison__name=user.prison)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, user=request.user)
        if form.is_valid():
            new_user = form.save(commit=False)
            selected_role = form.cleaned_data['role']

            # Set account fields based on the selected role
            if selected_role.role == 'Court':
                new_user.is_court_account = True
                new_user.is_prison_account = False
                new_user.court = form.cleaned_data['court']  # Set court
                new_user.prison = None  # No prison for court accounts
            elif selected_role.role == 'Commissioner':
                new_user.is_court_account = False
                new_user.is_prison_account = True
                new_user.court = None  # No court for commissioner accounts
                new_user.prison = form.cleaned_data['prison']  # Set prison
            elif selected_role.role == 'Inspector':
                new_user.is_court_account = False
                new_user.is_prison_account = True
                new_user.role = selected_role  # Inspector role
                new_user.prison = form.cleaned_data['prison']  # Set prison
            
            new_user.set_password(form.cleaned_data['password'])  # Set password
            new_user.save()
            messages.success(request, 'Account created successfully!')
            return redirect('create_account')  # Redirect after successful account creation
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = CustomUserCreationForm(user=request.user)  # Pass the current user to the form

    return render(request, 'create_account.html', {'form': form, 'officers': officers})

class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        if user.must_change_password:
            return redirect('password_change')
        elif user.must_add_profile:
            return redirect('add_profile')
        else:
            return redirect('Dashboard')#profile for now only

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def password_change(request):
    if request.method == 'POST':
        form = CustomSetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            user.must_change_password = False
            user.save()
            update_session_auth_hash(request, user)
            
            request.session['password_change_success'] = 'Your password has been changed successfully.'

            if user.must_add_profile:
                return redirect('add_profile')
            else:
                return redirect('profile')
    else:
        form = CustomSetPasswordForm(user=request.user)
    return render(request, 'password_change_form.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def add_profile(request):
    user = request.user
    success_message = request.session.pop('password_change_success', None)

    if request.method == 'POST':
        if not user.must_add_profile:
            return redirect('profile')

        form = AddProfileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Check if the user already has a profile
                profile = user.profile
                profile.first_name = form.cleaned_data['first_name']
                profile.last_name = form.cleaned_data['last_name']
                profile.email = form.cleaned_data['email']
                profile.gender = form.cleaned_data['gender']
                profile.date_of_birth = form.cleaned_data['date_of_birth']
                profile.phone = form.cleaned_data['phone']
                profile.address = form.cleaned_data['address']
                if 'picture' in form.cleaned_data and form.cleaned_data['picture']:
                    profile.picture = form.cleaned_data['picture']
                profile.save()

                # Update user information if needed
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']
                user.must_add_profile = False
                user.save()

                messages.success(request, 'Profile updated successfully.')
            except Profile.DoesNotExist:
                # Create a new profile if it doesn't exist
                profile = form.save(commit=False)
                profile.user = user
                profile.save()

                messages.success(request, 'Profile created successfully.')

            return redirect('profile')
        else:
            # If form is invalid, handle error messages
            error_message = "There was an error updating/creating the profile."
            for field, errors in form.errors.items():
                error_message += f" {field}: {', '.join(errors)}"
            messages.error(request, error_message)  # Add error message to Django messages
    else:
        form = AddProfileForm()

    return render(request, 'add_profile.html', {'form': form, 'success_message': success_message})

@login_required
def profile(request):
    # Check if the user is a visitor
    if request.user.is_visitor_account:
        # For visitor users
        # You can handle visitor-specific logic here if needed
        profile_instance = request.user.profile
        if request.method == 'POST':
            form = ProfileForm(request.POST, request.FILES, instance=profile_instance)  # Use a specific form for visitors if needed
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('profile-v')  # Redirect to visitor-specific profile page
            else:
                messages.error(request, 'There was an error updating the profile.')
        else:
            form = ProfileForm(instance=profile_instance)  # Use a visitor-specific form if needed

        return render(request, 'profile-v.html', {'form': form, 'user': request.user})

    else:
        # For regular users
        profile_instance = request.user.profile
        if request.method == 'POST':
            form = ProfileForm(request.POST, request.FILES, instance=profile_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('profile')  # Redirect to regular profile page
            else:
                messages.error(request, 'There was an error updating the profile.')
        else:
            form = ProfileForm(instance=profile_instance)
        
        return render(request, 'profile.html', {'form': form, 'user': request.user})

#Visitor CRUD
def register_view(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            # Check if the email or username already exists
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'errors': {'email': ['Email already exists.']}})
            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'errors': {'username': ['Username already exists.']}})
            
            user = form.save(commit=False)
            user.is_visitor_account = True
            user.must_change_password = False
            user.save()

            # Email verification
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
            full_activation_link = f"http://{current_site.domain}{activation_link}"

            message = render_to_string('activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'activation_link': full_activation_link,
            })
            plain_message = strip_tags(message)
            send_mail(mail_subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email])

            return JsonResponse({'success': True})
        else:
            # Extract form errors
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'errors': errors})

    else:
        form = CustomRegistrationForm()
    
    return render(request, 'register.html', {'form': form})
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.save()
        context = {
            'message': 'Your account has been activated successfully!',
            'message_type': 'success'
        }
    else:
        context = {
            'message': 'The activation link is invalid or has expired.',
            'message_type': 'error'
        }

    return render(request, 'email_status.html', context)

@csrf_exempt
def resend_activation_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        User = get_user_model()
        try:
            user = User.objects.get(email=email, is_email_verified=False)
        except User.DoesNotExist:
            return JsonResponse({'message': 'No user found with this email or user is already activated.'}, status=400)

        current_site = get_current_site(request)
        mail_subject = 'Activate your account'
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        full_activation_link = f"http://{current_site.domain}{activation_link}"
        
        message = render_to_string('activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'activation_link': full_activation_link,
        })
        plain_message = strip_tags(message)
        send_mail(mail_subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return JsonResponse({'message': 'Activation email has been resent.'})

    return JsonResponse({'message': 'Invalid request method.'}, status=400)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Basic validation
        errors = {}
        if not username:
            errors['username'] = ["Username is required."]
        if not password:
            errors['password'] = ["Password is required."]

        if errors:
            return JsonResponse({'success': False, 'errors': errors})

        # Attempt to authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'message': f'Welcome back, {username}!'})
        else:
            # Additional error messages
            if not request.user.is_active:
                errors['non_field_errors'] = ["Your account has been deactivated."]
            else:
                errors['non_field_errors'] = ["Invalid username or password."]
                
            return JsonResponse({'success': False, 'errors': errors})
    
    return render(request, 'login-v.html')

class CustomPasswordResetView(PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'forget_password.html'
    email_template_name = 'password_reset_email.html'
    success_url = '/login/'

def logout_view_v(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('loginv')
# Appointment views.py

def get_cities(request):
    cities = City.objects.all()
    city_list = list(cities.values('id', 'name'))  # Modify as needed
    return JsonResponse({'cities': city_list})

def get_prisons(request):
    city_id = request.GET.get('city_id')
    prisons = Prison.objects.filter(city_id=city_id)
    prison_list = list(prisons.values('id', 'name'))  # Modify as needed
    return JsonResponse({'prisons': prison_list})

def get_prison_info(request):
    prison_id = request.GET.get('prison_id')
    try:
        prison = Prison.objects.get(id=prison_id)
        data = {
            'name': prison.name,
            'level': prison.prison_type,
            'city': prison.city.name,
            'sub_city': prison.sub_city.name,
            'location': prison.location,
            'phone_number': prison.phone_number,
            'email': prison.email,
        }
        return JsonResponse(data)
    except Prison.DoesNotExist:
        return JsonResponse({'error': 'Prison not found'}, status=404)

def get_officer_details(request):
    User = get_user_model()
    officer_id = request.GET.get('officer_id')
    officer = User.objects.get(id=officer_id)
    data = {
        'picture': officer.profile.picture.url,
        'first_name': officer.first_name,
        'last_name': officer.last_name,
        'gender': officer.profile.gender,
        'date_of_birth': officer.profile.date_of_birth,
        'email': officer.email,
        'phone': officer.profile.phone,
        'address': officer.profile.address,
        'date_joined': officer.date_joined,
    }
    return JsonResponse(data)

def find_prisoner(request):
    prisoner_id = request.GET.get('prisoner_id')
    found = Prisoner.objects.filter(id=prisoner_id).exists()
    return JsonResponse({'found': found})

def get_time_slots(request):
    date = request.GET.get('date')
    time_slots = TimeSlot.objects.filter(date=date).values('id', 'time')
    return JsonResponse({'time_slots': list(time_slots)})

def create_appointment(request):
    
    return JsonResponse('Hi')