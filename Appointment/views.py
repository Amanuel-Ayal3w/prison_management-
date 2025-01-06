from django.http import JsonResponse
import random
import string
from .models import *
from Accounts.models import City, Prison
from Court.models import  Prisoner
from datetime import datetime
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
from Court.models import Prisoner
from .forms import *
from django.contrib import messages
from datetime import datetime
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.conf import settings
from .models import Prison, Prisoner, Appointment
import random
import string



def test_home(request):
    return render(request, 'tester_home.html' )

def index(request):
    return render(request, 'test_home.html' )

def get_cities(request):
    cities = City.objects.all().values('id', 'name')
    return JsonResponse({'cities': list(cities)})

def get_prisons(request):
    city_id = request.GET.get('city_id')
    prisons = Prison.objects.filter(city_id=city_id).values('id', 'name')
    return JsonResponse({'prisons': list(prisons)})

def get_prison_info(request):
    prison_id = request.GET.get('prison_id')
    prison = Prison.objects.get(id=prison_id)
    prison_info = {
        'name': prison.name,
        'level': prison.level,
        'city': prison.city.name,
        'sub_city': prison.sub_city,
        'location': prison.location,
        'phone_number': prison.phone_number,
        'email': prison.email,
    }
    return JsonResponse(prison_info)

def get_prisoner_info(request):
    prisoner_id = request.GET.get('prisoner_id')
    try:
        prisoner = Prisoner.objects.get(pri_code=prisoner_id)
        name = prisoner.pri_fname + ' ' + prisoner.pri_mname + '' + prisoner.pri_lname
        prisoner_info = {
            'name': name,
            'picture': prisoner.picture.url,
        }
        return JsonResponse(prisoner_info)
    except Prisoner.DoesNotExist:
        return JsonResponse({'error': 'Prisoner not found'}, status=404)

def get_available_time_slots(request):
    date_str = request.GET.get('date')
    prison_id = request.GET.get('prison_id')
    date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # Define all available time slots
    all_slots = ['12:00 PM-1:00 PM', '1:00 PM-2:00 PM', '2:00 PM-3:00 PM', '3:00 PM-4:00 PM', 
                 '4:00 PM-5:00 PM', '5:00 PM-6:00 PM', '6:00 PM-7:00 PM', '7:00 PM-8:00 PM', 
                 '8:00 PM-9:00 PM', '9:00 PM-10:00 PM', '10:00 PM-11:00 PM', '11:00 PM-12:00 PM']

    # Fetch existing appointments for the selected date and prison
    existing_appointments = Appointment.objects.filter(prison_id=prison_id, appointment_date=date)

    # Fetch disabled slots for the selected date and prison
    disabled_slots = DisabledSlot.objects.filter(prison_id=prison_id, date=date)

    # If the entire date is disabled, return an empty list
    if disabled_slots.exists():
        return JsonResponse({'available_slots': []})

    # Count the number of appointments per time slot
    slot_count = {}
    for appt in existing_appointments:
        if appt.time_slot in slot_count:
            slot_count[appt.time_slot] += 1
        else:
            slot_count[appt.time_slot] = 1

    # Get the current time and filter past time slots if the selected date is today
    now = datetime.now()
    available_slots = []

    for slot in all_slots:
        start_time_str, _ = slot.split('-')  # Get the start time of the slot
        slot_start_time = datetime.strptime(start_time_str.strip(), "%I:%M %p").time()  # Parse time in 12-hour format

        # If the selected date is today and the time slot is in the past, skip it
        if date == now.date() and slot_start_time <= now.time():
            continue

        # Add slot if it's not fully booked
        if slot_count.get(slot, 0) < 2:
            available_slots.append(slot)

    return JsonResponse({'available_slots': available_slots})
    
def disable_slot(request):
    if request.method == 'POST':
        form = DisabledSlotForm(request.POST)
        if form.is_valid():
            disabled_slot = form.save(commit=False)
            disabled_slot.prison = request.user.prison  # Assuming the user model has a prison field
            disabled_slot.save()
            messages.success(request, 'Slot disabled successfully.')
            return redirect('disabled_slots_list')
        else:
            messages.error(request, 'There was an error disabling the slot. Please check the form for errors.')
    else:
        form = DisabledSlotForm()
    return render(request, 'SuspendDate/disable_slot.html', {'form': form})

def disabled_slots_list(request):
    disabled_slots = DisabledSlot.objects.filter(prison=request.user.prison)
    return render(request, 'SuspendDate/disabled_slots_list.html', {'disabled_slots': disabled_slots})

#def generate_confirmation_number():
#    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def generate_confirmation_number(length=8):
    """ Generate a random alphanumeric confirmation number. """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def submit_appointment(request):
    if request.method == 'POST':
        # Extract form data
        user = request.user
        try:
            prison_id = int(request.POST.get('prison'))
            prisoner_id = request.POST.get('prisoner_id')
            appointment_date = request.POST.get('appointment_date')
            time_slot = request.POST.get('time_slot')
            appointment_type = request.POST.get('appointment_type')  # 'self' or 'others'
            if appointment_type == 'self':
                appointment_types = True
            # Check if prison and prisoner exist
            prison = Prison.objects.get(id=prison_id)
            prisoner = Prisoner.objects.get(pri_code=prisoner_id)

            # Generate an 8-digit alphanumeric confirmation number
            confirmation_number = generate_confirmation_number()

            # Create and save the appointment
            appointment = Appointment(
                user=user,
                prison=prison,
                prisoner=prisoner,
                appointment_date=appointment_date,
                time_slot=time_slot,
                confirmation_number=confirmation_number,
                appointment_type=appointment_type , # Save the appointment type
                for_self = appointment_types
            )
            appointment.save()

            # Prepare email content
            subject = 'Appointment Confirmation'
            message = render_to_string('appointment_confirmation_email.html', {
                'user': user,
                'prison': prison,
                'prisoner': prisoner,
                'appointment_date': appointment_date,
                'time_slot': time_slot,
                'confirmation_number': confirmation_number
            })
            plain_message = strip_tags(message)
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = user.email

            # Send email
            send_mail(subject, plain_message, from_email, [to_email], html_message=message)

            # Return a JSON response with the confirmation number
            return JsonResponse({
                'status': 'success',
                'confirmation_number': confirmation_number
            })

        except (ValueError, Prison.DoesNotExist, Prisoner.DoesNotExist) as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

def find_appointment(request):
    if request.method == 'GET':
        confirmation_number = request.GET.get('confirmation_number', None)
        
        if confirmation_number:
            if not confirmation_number.isalnum():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Confirmation number must be alphanumeric'
                }, status=400)
            
            try:
                # Filter the appointments by the provided confirmation number
                appointments = Appointment.objects.filter(confirmation_number=confirmation_number)
            except Appointment.DoesNotExist:
                appointments = []
        else:
            # If no confirmation number is provided, list all appointments
            appointments = Appointment.objects.all()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            appointments_list = [
                {
                    'id': appointment.id,
                    'user': appointment.user.username if appointment.user else None,
                    'prison': appointment.prison.name if appointment.prison else None,
                    'prisoner': appointment.prisoner.name if appointment.prisoner else None,
                    'appointment_date': str(appointment.appointment_date),
                    'time_slot': appointment.time_slot,
                    'confirmation_number': appointment.confirmation_number,
                }
                for appointment in appointments
            ]
            return JsonResponse({'appointments': appointments_list})
        
        context = {'appointments': appointments}
        return render(request, 'find_appointment.html', context)

    return render(request, 'find_appointment.html')


#CRUDE FOR VISITOR
def create_visitor(request):
    confirmation_number = request.GET.get('confirmation_number', None)
    appointment = None

    if confirmation_number:
        try:
            appointment = Appointment.objects.get(confirmation_number=confirmation_number)
        except Appointment.DoesNotExist:
            pass

    if request.method == 'POST':
        form = VisitorForm(request.POST)
        if form.is_valid():
            visitor = form.save(commit=False)
            if appointment:
                visitor.appointment = appointment
                visitor.prison = appointment.prison
                visitor.prisoner = appointment.prisoner
                visitor.visit_date = appointment.appointment_date
                visitor.time_slot = appointment.time_slot
                appointment.is_assigned = True
                appointment.save()
            else:
                # Set the prison from the user if not provided
                if not visitor.prison:
                    visitor.prison = request.user.prison
                
                # Validate and find the prisoner by ID using get_prisoner_info
                prisoner_id = request.POST.get('prisoner_id')
                if prisoner_id:
                    response = get_prisoner_info(request)
                    if response.status_code == 200:
                        prisoner_data = response.json()
                        visitor.prisoner = get_object_or_404(Prisoner, pri_code=prisoner_id)
                    else:
                        return JsonResponse({'error': 'Prisoner not found'}, status=404)
                
            visitor.save()

            # Add success message
            messages.success(request, 'Visitor created successfully!')

            # Redirect to the visitor list page with the success message
            return redirect('visitor_list')
    else:
        form = VisitorForm()
        if appointment:
            # Populate form fields based on appointment type
            if appointment.for_self:
                form.fields['name'].initial = f"{appointment.user.first_name} {appointment.user.last_name}"
                form.fields['gender'].initial = appointment.user.profile.gender  # Assuming you have a profile model with gender
                form.fields['contact_number'].initial = appointment.user.profile.phone  # Assuming you have a profile model with phone
                form.fields['visit_date'].initial = appointment.appointment_date
                form.fields['prisoner'].initial = appointment.prisoner
                form.fields['time_slot'].initial = appointment.time_slot

    return render(request, 'add_visitor.html', {'form': form, 'appointment': appointment})

def visitor_list(request):
    visitors = Visitor.objects.all()
    return render(request, 'visitor_list.html', {'visitors': visitors})

def visitor_detail(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    return render(request, 'visitor_detail.html', {'visitor': visitor})

def update_visitor(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    if request.method == 'POST':
        form = VisitorForm(request.POST, instance=visitor)
        if form.is_valid():
            form.save()
            return redirect('visitor_list')
    else:
        form = VisitorForm(instance=visitor)
    return render(request, 'update_visitor.html', {'form': form})

def delete_visitor(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    if request.method == 'POST':
        visitor.delete()
        return redirect('visitor_list')
    return render(request, 'delete_visitor.html', {'visitor': visitor})
