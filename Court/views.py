from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import *
from .forms import *
from Appointment.models import Visitor, Appointment
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

def prisoner_delete(request, pk):
    prisoner = get_object_or_404(Prisoner, pk=pk)

    if request.method == 'POST':
        prisoner.delete()
        messages.success(request, 'Prisoner deleted successfully.')
        return redirect(reverse('prisoner_list'))
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

def Home(request):
    return render(request, 'index.html')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Prisoner, Activity

@login_required
def dashboard(request):
    prisoners = Prisoner.objects.filter(prison=request.user.prison)
    officer = User.objects.filter(prison=request.user.prison)
    visitors = Visitor.objects.filter(prison=request.user.prison)
    appointments = Appointment.objects.filter(prison=request.user.prison)
    activities = Activity.objects.filter(prisoner__prison=request.user.prison)

    male_prisoners_count = prisoners.filter(pri_gender='Male').count()
    female_prisoners_count = prisoners.filter(pri_gender='Female').count()
    
    context = {
        'prisoners': prisoners,
        'officer': officer,
        'visitors': visitors,
        'appointments': appointments,
        'activities': activities,
        'male_prisoners_count': male_prisoners_count,
        'female_prisoners_count': female_prisoners_count,
    }

    return render(request, 'dashboard.html', context)

@login_required
def prisoner_list(request):
    user = request.user
    
    if user.is_court_account and user.court:
        prisoners = Prisoner.objects.filter(court=user.court)
    elif user.is_prison_account and user.prison:
        prisoners = Prisoner.objects.filter(prison=user.prison)
    else:
        prisoners = Prisoner.objects.none()  # If user doesn't have a court or prison value, return empty queryset

    return render(request, 'Prisoners/prisoner_list.html', {'prisoners': prisoners})


def prisoner_detail(request, pk):
    prisoner = get_object_or_404(Prisoner, pk=pk)
    crime_details = CrimeDetail.objects.filter(cprisoner_id=prisoner)
    court = request.user.court
    context = {
        'prisoner': prisoner,
        'crime_details': crime_details,
        'court': court,
        'activities': Activity.objects.filter(prisoner=prisoner),
    }
    return render(request, 'Prisoners/prisoner_details.html', context)

def prisoner_create(request):
    if not request.user.is_authenticated or not request.user.is_court_account:
        return redirect('not_found')
    
    if request.method == "POST":
        form = PrisonerForm(request.POST, request.FILES)
        formset = CrimeDetailFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            date_arrest = form.cleaned_data['pri_date_of_arrest']
            date_depart = form.cleaned_data['pri_date_of_depart']
            sentence_date = form.cleaned_data['sentence_date']
            release_date = form.cleaned_data['release_date']
            
            if date_arrest >= date_depart or date_depart >= sentence_date or sentence_date >= release_date:
                return JsonResponse({'message': 'Invalid date order.', 'errors': {}}, status=400)
            
            prisoner = form.save(commit=False)
            prisoner.court = request.user.court  # Set the court foreign key based on the current user
            prisoner.save()
            formset.instance = prisoner
            formset.save()

            return JsonResponse({'message': 'Prisoner created successfully.', 'errors': {}}, status=200)
            
        else:
            errors = {
                'form_errors': form.errors,
                'formset_errors': [form.errors for form in formset.forms]
            }
            return JsonResponse({'message': 'Form is not valid.', 'errors': errors}, status=400)
    
    else:
        form = PrisonerForm()
        formset = CrimeDetailFormSet()
    
    return render(request, 'Prisoners/prisoner_form.html', {'form': form, 'formset': formset})

def redirect_with_toastr(request, status, message):
    if status == 'success':
        request.session['toastr_status'] = 'success'
    elif status == 'error':
        request.session['toastr_status'] = 'error'
    request.session['toastr_message'] = message
    return redirect('prisoner_create')

def prisoner_update(request, pk):
    if not request.user.is_authenticated or not request.user.is_court_account:
        return redirect('not_found')

    prisoner = get_object_or_404(Prisoner, pk=pk)

    if request.method == "POST":
        form = PrisonerForm(request.POST, request.FILES, instance=prisoner)
        formset = CrimeDetailFormSet(request.POST, instance=prisoner)

        if form.is_valid() and formset.is_valid():
            date_arrest = form.cleaned_data['pri_date_of_arrest']
            date_depart = form.cleaned_data['pri_date_of_depart']
            sentence_date = form.cleaned_data['sentence_date']
            release_date = form.cleaned_data['release_date']

            if date_arrest >= date_depart or date_depart >= sentence_date or sentence_date >= release_date:
                return JsonResponse({'message': 'Invalid date order.', 'errors': {}}, status=400)

            prisoner = form.save(commit=False)
            prisoner.court = request.user.court  # Ensure the court remains consistent
            prisoner.save()
            formset.save()

            return JsonResponse({'message': 'Prisoner updated successfully.', 'errors': {}}, status=200)
        else:
            errors = {
                'form_errors': form.errors,
                'formset_errors': [form.errors for form in formset.forms]
            }
            return JsonResponse({'message': 'Form is not valid.', 'errors': errors}, status=400)

    else:
        form = PrisonerForm(instance=prisoner)
        formset = CrimeDetailFormSet(instance=prisoner)

    return render(request, 'Prisoners/prisoner_form.html', {'form': form, 'formset': formset})

@csrf_exempt
def prisoner_delete(request, pk):
    prisoner = get_object_or_404(Prisoner, pk=pk)

    if request.method == 'POST':
        # Delete associated CrimeDetail instances first
        prisoner.crime_detail_set.all().delete()
        
        # Now delete the prisoner instance
        prisoner.delete()
        
        messages.success(request, 'Prisoner and associated crime details deleted successfully.')
        return JsonResponse({'status': 'success', 'message': 'Prisoner and associated crime details deleted successfully.'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

@login_required
def prisoner_room_list(request):
    user = request.user
    if user.is_prison_account and user.prison:
        prisoners = Prisoner.objects.filter(prison=user.prison)
    else:
        prisoners = Prisoner.objects.none()  # If user doesn't have a court or prison value, return empty queryset

    return render(request, 'Prisoners/assign_room_list.html', {'prisoners': prisoners})

def prisoner_room_assign(request, prisoner_id):
    temp_prisoner = get_object_or_404(Prisoner, pk=prisoner_id)
    if request.method == 'POST':
        room_code = request.POST.get('room_code')
        if room_code:
            try:
                occupancy = Occupancy.objects.get(room_code=room_code)
                if (occupancy.room_type ==  temp_prisoner.pri_gender):
                    temp_prisoner.room_code = occupancy
                    occupancy.no_of_pri +=1
                    temp_prisoner.save()
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Prisoner Room Assigned successfully.',
                    })
                
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Room type or gender mismatch.',
                    }, status=400)
            except Occupancy.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invalid room code.'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'Room code is required.'}, status=400)
    else:
        form = TempPrisonerForm(instance=temp_prisoner)
        crime_details = CrimeDetail.objects.filter(cprisoner_id=temp_prisoner)
        court = request.user.court
        context = {
            'prisoner': temp_prisoner,
            'crime_details': crime_details,
            'court': court,
            'form': form,
            'occupancies': Occupancy.objects.all(),
        }
        return render(request, 'Prisoners/assign_room.html', context)

def transfer_list(request):
    transfers = Transfer.objects.all()
    return render(request, 'Transfers/transfer_list.html', {'transfers': transfers})

def transfer_detail(request, pk):
    transfer = get_object_or_404(Transfer, pk=pk)
    return render(request, 'Transfers/transfer_detail.html', {'transfer': transfer})


@login_required
def transfer_create(request, prisoner_id):
    prisoner = get_object_or_404(Prisoner, pk=prisoner_id)
    
    # Check if the prisoner already has an active transfer request
    existing_transfer = Transfer.objects.filter(prisoner=prisoner, status='pending').first()
    if existing_transfer:
        messages.error(request, 'This prisoner already has an active transfer request.')
        return redirect('transfer_list')

    if request.method == 'POST':
        form = TransferForm(request.POST, user=request.user)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.prisoner = prisoner
            transfer.requested_by = request.user
            transfer.priosn = request.user.prison
            transfer.status = 'pending'  # Set status to pending by default
            transfer.save()
            
            # Send notification to the inspector of the selected prison
            inspectors = User.objects.filter(prison=transfer.to_prison, role__role='Inspector')
            for user in inspectors:
                Notification.objects.create(
                    user=user,
                    message=f'Prisoner Transfer request from {transfer.prison}'
                )
                
            messages.success(request, 'Transfer request sent successfully.')
            return redirect('transfer_list')
    else:
        form = TransferForm(user=request.user)
    
    return render(request, 'Transfers/transfer_form.html', {'form': form, 'prisoner': prisoner})

@login_required
def transfer_update(request, transfer_id):
    transfer = get_object_or_404(Transfer, pk=transfer_id)
    if request.method == 'POST':
        form = TransferForm(request.POST, instance=transfer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transfer request updated successfully.')
            return redirect('transfer_list')
    else:
        form = TransferForm(instance=transfer)
    return render(request, 'transfers/transfer_form.html', {'form': form})


def transfer_delete(request, pk):
    transfer = get_object_or_404(Transfer, pk=pk)
    if request.method == "POST":
        transfer.delete()
        return redirect('transfer_list')
    return render(request, 'transfer_confirm_delete.html', {'transfer': transfer})

@login_required
def transfer_accept(request, transfer_id):
    prisoner = get_object_or_404(Prisoner, pk=transfer.prisoner_id)
    prisoner.prison = transfer.to_prison
    transfer = get_object_or_404(Transfer, pk=transfer_id)
    transfer.status = 'accepted'
    transfer.save()
    prisoner.save()
    messages.success(request, 'Transfer request accepted successfully.')
    # Additional logic for handling accepted transfer
    return redirect('transfer_list')

@login_required
def transfer_reject(request, transfer_id):
    transfer = get_object_or_404(Transfer, pk=transfer_id)
    transfer.status = 'rejected'
    transfer.save()
    messages.error(request, 'Transfer request rejected.')
    # Additional logic for handling rejected transfer
    return redirect('transfer_list')

@login_required
def transfer_requested_list(request):
    user = request.user
    # Ensure that the user has a prison and role assigned
    if user.prison and user.role and user.role.role == 'Inspector':
        # Filter transfers where the destination prison is the user's prison
        transfers = Transfer.objects.filter(to_prison=user.prison)
    else:
        transfers = Transfer.objects.none()  # Return an empty queryset if the conditions are not met

    return render(request, 'Transfers/transfer_requested_list.html', {'transfers': transfers})

def add_room(request):
    if request.method == 'POST':
        form = OccupancyForm(request.POST)
        if form.is_valid():
            room = form.save()
            room_html = render_to_string('partials/room_row.html', {'room': room})
            return JsonResponse({'status': 'success', 'message': 'Room added successfully!', 'room_html': room_html})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to add room. Please check the form for errors.'})
    else:
        form = OccupancyForm()
    rooms = Occupancy.objects.all()
    return render(request, 'room.html', {'form': form, 'rooms': rooms})

def room_list(request):
    # Update the prisoner count before listing rooms
    
    rooms = Occupancy.objects.all()
    form = OccupancyForm()  # Create an instance of the form
    
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        room_list_html = render_to_string('partials/room_list.html', {'rooms': rooms})
        return JsonResponse({'room_list_html': room_list_html})
    
    return render(request, 'room.html', {'rooms': rooms, 'form': form})

def room_update(request, pk):
    room = get_object_or_404(Occupancy, pk=pk)
    if request.method == 'POST':
        form = OccupancyForm(request.POST, instance=room)
        if form.is_valid():
            room = form.save()
            room_html = render_to_string('partials/room_row.html', {'room': room})
            return JsonResponse({'status': 'success', 'message': 'Room updated successfully!', 'room_html': room_html})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to update room. Please check the form for errors.'})
    else:
        room_data = {
            'id': room.id,
            'room_code': room.room_code,
            'block': room.block,
            'room_type': room.room_type,
            'no_of_beds': room.no_of_beds,
            'remaining_bed': room.remaining_bed,
        }
        return JsonResponse({'room': room_data})

@csrf_exempt
def room_delete(request, pk):
    room = get_object_or_404(Occupancy, pk=pk)
    if request.method == 'POST':
        room.delete()
        return JsonResponse({'status': 'success', 'message': 'Room deleted successfully!'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Failed to delete room.'})

def get_sub_cities(request):
    city_id = request.GET.get('city_id')
    sub_cities = SubCity.objects.filter(city_id=city_id).values('id', 'name')
    return JsonResponse(list(sub_cities), safe=False)

def add_prison(request):
    if request.method == 'POST':
        form = PrisonForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Prison added successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data'})
    else:
        form = PrisonForm()
    return render(request, 'add_prison.html', {'form': form})

def update_prison(request, pk):
    prison = get_object_or_404(Prison, pk=pk)
    if request.method == 'POST':
        form = PrisonForm(request.POST, instance=prison)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Prison updated successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data'})
    else:
        form = PrisonForm(instance=prison)
    return render(request, 'update_prison.html', {'form': form})

def delete_prison(request, pk):
    prison = get_object_or_404(Prison, pk=pk)
    if request.method == 'POST':
        prison.delete()
        return JsonResponse({'status': 'success', 'message': 'Prison deleted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def prison_list(request):
    prisons = Prison.objects.all()
    return render(request, 'Prisons/all-prison.html', {'prisons': prisons})

def not_found(request):
    return render(request, '404.html')

#@login_required
#@require_POST
#def create_activity(request, prisoner_id):
#    try:
#        prisoner = get_object_or_404(Prisoner, pk=prisoner_id)
#        form = ActivityForm(request.POST)
#
#        if form.is_valid():
#            activity = form.save(commit=False)
#            activity.prisoner = prisoner
#            activity.created_by = request.user
#            activity.save()
#            return JsonResponse({'status': 'success', 'message': _('Activity created successfully.')})
#        else:
#            errors = form.errors.as_json()
#            return JsonResponse({'status': 'error', 'message': _('Please correct the errors below.'), 'errors': errors}, status=400)
#
#    except Prisoner.DoesNotExist:
#        return JsonResponse({'status': 'error', 'message': _('Prisoner not found.')}, status=404)
#
#    except ValidationError as e:
#        return JsonResponse({'status': 'error', 'message': _('Invalid data: ') + str(e)}, status=400)
#
#    except Exception as e:
#        # Log the error for debugging (optional)
#        print(f"Unexpected error: {str(e)}")
#        return JsonResponse({'status': 'error', 'message': _('An unexpected error occurred. Please try again.')}, status=500)
@login_required
@require_POST
def save_activity(request, prisoner_id, activity_id=None):
    try:
        prisoner = get_object_or_404(Prisoner, pk=prisoner_id)
        print("Prisoner found:", prisoner)

        # Check if activity_id is provided for update
        if activity_id:
            activity = get_object_or_404(Activity, pk=activity_id)
            print("Activity found for update:", activity)
            if activity.prisoner != prisoner:
                return JsonResponse({'status': 'error', 'message': _('Activity does not belong to the specified prisoner.')}, status=400)
            form = ActivityForm(request.POST, instance=activity)
        else:
            form = ActivityForm(request.POST)

        if form.is_valid():
            print("Form is valid")
            activity = form.save(commit=False)
            activity.prisoner = prisoner
            if not activity_id:  # Only set created_by on creation
                activity.created_by = request.user
            activity.save()

            if activity_id:
                return JsonResponse({'status': 'success', 'message': _('Activity updated successfully.')})
            else:
                return JsonResponse({'status': 'success', 'message': _('Activity created successfully.')})
        else:
            errors = form.errors.as_json()
            print("Form errors:", errors)
            return JsonResponse({'status': 'error', 'message': _('Please correct the errors below.'), 'errors': errors}, status=400)

    except Prisoner.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': _('Prisoner not found.')}, status=404)

    except ValidationError as e:
        print("Validation error:", str(e))
        return JsonResponse({'status': 'error', 'message': _('Invalid data: ') + str(e)}, status=400)

    except Exception as e:
        # Log the error for debugging (optional)
        print(f"Unexpected error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': _('An unexpected error occurred. Please try again.')}, status=500)

def activity_form(request, prisoner_id, activity_id=None):
    prisoner = get_object_or_404(Prisoner, pk=prisoner_id)
    
    # Check if activity_id is provided for update
    if activity_id:
        activity = get_object_or_404(Activity, pk=activity_id)
        if activity.prisoner != prisoner:
            # Handle the case where the activity doesn't belong to the prisoner
            return render(request, 'Activities/activity_create.html', {
                'prisoner': prisoner,
                'form': None,
                'error_message': _('Activity does not belong to the specified prisoner.')
            })
        form = ActivityForm(instance=activity)
    else:
        form = ActivityForm()

    return render(request, 'Activities/activity_create.html', {
        'prisoner': prisoner,
        'form': form,
        'activity': activity if activity_id else None  # Pass the activity only if updating
    })

@login_required
def prisoner_activity_list(request):
    user = request.user
    
    if user.is_prison_account and user.prison:
        prisoners = Prisoner.objects.filter(prison=user.prison)
    else:
        prisoners = Prisoner.objects.none()  # If user doesn't have a court or prison value, return empty queryset

    return render(request, 'Activities/activity_create_list.html', {'prisoners': prisoners})

@login_required
def activity_list(request, prisoner_id):
    prisoner = get_object_or_404(Prisoner, pk=prisoner_id)

    activities = Activity.objects.filter(prisoner=prisoner)
    return render(request, 'Activities/activity_list.html', {'prisoner': prisoner, 'activities': activities})

@login_required
def activity_detail(request, activity_id, prisoner_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    prisoner = get_object_or_404(Prisoner, pk=prisoner_id)
    return render(request, 'Activities/activity_detail.html', {'activity': activity, 'prisoner': prisoner})

#@login_required
#def activity_create(request, prisoner_id):
#    prisoner = get_object_or_404(Prisoner, pk=prisoner_id)
#    if request.method == 'POST':
#        form = ActivityForm(request.POST)
#        if form.is_valid():
#            activity = form.save(commit=False)
#            activity.prisoner = prisoner
#            activity.created_by = request.user
#            activity.save()
#            return redirect('activity_list', prisoner_id=prisoner.pk)
#    else:
#        form = ActivityForm()
#    return render(request, 'activities/activity_form.html', {'form': form, 'prisoner': prisoner})

@login_required
def activity_update(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect('activity_list', prisoner_id=activity.prisoner.pk)
    else:
        form = ActivityForm(instance=activity)
    return render(request, 'Activities/activity_create.html', {'form': form, 'prisoner': activity.prisoner})


@login_required
@require_POST
def activity_delete(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    prisoner_id = activity.prisoner.pk
    activity.delete()
    # Return a JSON response with a success status and redirect URL
    return JsonResponse({
        'status': 'success',
        'message': 'Activity deleted successfully!',
        'redirect_url': reverse('activity_list', kwargs={'prisoner_id': prisoner_id})
    })

@login_required
def discipline_delete(request, discipline_id):
    discipline = get_object_or_404(Discipline, pk=discipline_id)
    prisoner_id = discipline.prisoner.pk
    discipline.delete()

    return JsonResponse({
        'status': 'success',
        'message': 'Discipline record deleted successfully!',
        'redirect_url': reverse('discipline_list', kwargs={'prisoner_id': prisoner_id})
    })

@login_required
def discipline_list(request, prisoner_id):
    prisoner = get_object_or_404(Prisoner, pk=prisoner_id)
    disciplines = Discipline.objects.filter(prisoner=prisoner)
    return render(request, 'disciplines/discipline_list.html', {'prisoner': prisoner, 'disciplines': disciplines})

@login_required
def discipline_detail(request, discipline_id):
    discipline = get_object_or_404(Discipline, pk=discipline_id)
    return render(request, 'disciplines/discipline_detail.html', {'discipline': discipline})

@login_required
def discipline_create(request, prisoner_id):
    prisoner = get_object_or_404(Prisoner, pk=prisoner_id)
    if request.method == 'POST':
        form = DisciplineForm(request.POST, prisoner=prisoner)
        if form.is_valid():
            discipline = form.save(commit=False)
            discipline.prisoner = prisoner
            discipline.save()
            messages.success(request, 'Discipline record created successfully.')
            return redirect('discipline_list', prisoner_id=prisoner.pk)
        else:
            messages.error(request, 'There was an error creating the discipline record. Please check the form and try again.')
    else:
        form = DisciplineForm(prisoner=prisoner)
    return render(request, 'disciplines/discipline_form.html', {'form': form, 'prisoner': prisoner})

@login_required
def discipline_update(request, discipline_id):
    discipline = get_object_or_404(Discipline, pk=discipline_id)
    if request.method == 'POST':
        form = DisciplineForm(request.POST, instance=discipline)
        if form.is_valid():
            form.save()
            messages.success(request, 'Discipline record updated successfully.')
            return redirect('discipline_list', prisoner_id=discipline.prisoner.pk)
        else:
            messages.error(request, 'There was an error updating the discipline record. Please check the form and try again.')
    else:
        form = DisciplineForm(instance=discipline)
    return render(request, 'disciplines/discipline_form.html', {'form': form, 'prisoner': discipline.prisoner})


@login_required
def discipline_add_list(request):
    user = request.user
    
    if user.is_prison_account and user.prison:
        prisoners = Prisoner.objects.filter(prison=user.prison)
    else:
        prisoners = Prisoner.objects.none()  # If user doesn't have a court or prison value, return empty queryset

    return render(request, 'disciplines/discipline_add_list.html', {'prisoners': prisoners})

@login_required
def transfer_add_list(request):
    user = request.user
    
    if user.is_prison_account and user.prison:
        prisoners = Prisoner.objects.filter(prison=user.prison)
        for prisoner in prisoners:
            is_transfer = prisoner.transfers.filter(status='pending').exists()
            if is_transfer:
                transfer = prisoner.transfers.get(status='pending')
            else:
                transfer = Transfer.objects.none()
    else:
        prisoners = Prisoner.objects.none()  # If user doesn't have a court or prison value, return empty queryset
        transfer = prisoner.objects.none()  
    return render(request, 'Transfers/transfer_add_list.html', {'prisoners': prisoners, 'transfer': transfer, 'is_transfer': is_transfer})

@login_required
def parole_add_list(request):
    user = request.user

    if user.is_prison_account and user.prison:
        # Get all prisoners for the user's prison
        prisoners = Prisoner.objects.filter(prison=user.prison)
        
        # Create a dictionary of prisoners with their parole record
        prisoner_parole_map = {}
        for prisoner in prisoners:
            # Get the parole record for the prisoner, if it exists
            parole = Parole.objects.filter(prisoner=prisoner).first()
            prisoner_parole_map[prisoner] = parole
    else:
        prisoners = Prisoner.objects.none()
        prisoner_parole_map = {}

    return render(request, 'Paroles/parole_add_list.html', {'prisoner_parole_map': prisoner_parole_map})

@login_required
def create_parole(request, pk):
    prisoner = get_object_or_404(Prisoner, pk=pk)
    
    if request.method == 'POST':
        form = ParoleForm(request.POST)
        if form.is_valid():
            parole = form.save(commit=False)
            parole.prisoner = prisoner
            parole.created_by = request.user
            prisoner.rehabilitation_program_enrolled = True
            parole.save()
            prisoner.save()
            messages.success(request, 'Parole created successfully')
            return redirect('parole_list')
    else:
        form = ParoleForm()
    
    context = {
        'form': form,
        'prisoner': prisoner
    }
    return render(request, 'Paroles/create_parole.html', context)

@login_required
def update_parole(request, pk):
    parole = get_object_or_404(Parole, pk=pk)
    
    if request.method == 'POST':
        form = ParoleForm(request.POST, instance=parole)
        if form.is_valid():
            form.save()
            messages.success(request, 'Parole updated successfully')
            return redirect('parole_list')
    else:
        form = ParoleForm(instance=parole)
    
    context = {
        'form': form,
        'prisoner': parole.prisoner
    }
    return render(request, 'Paroles/create_parole.html', context)

@login_required
def delete_parole(request, pk):
    parole = get_object_or_404(Parole, pk=pk)
    if request.method == 'POST':
        parole.delete()
        messages.success(request, 'Parole deleted successfully')
        return redirect('parole_list')
    return redirect('parole_list')

@login_required
def parole_list(request):
    paroles = Parole.objects.all()
    return render(request, 'Paroles/parole_list.html', {'paroles': paroles})