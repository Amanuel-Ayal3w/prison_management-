from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Temp_prisoner
from .forms import *
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from Court.models import Occupancy
from django.contrib.auth.decorators import login_required
from Court.models import TempPrisoner
from .forms import TempPrisonerForm
from Accounts.models import Notification
from django.contrib.auth import get_user_model
import json
from django.views.decorators.http import require_POST
from django.contrib import messages

#Notification 
@login_required
def list_notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    num_unread_notifications = notifications.filter(is_read=False).count()
    context = {
        'notifications': notifications,
        'num_unread_notifications': num_unread_notifications,
    }
    return render(request, 'notifications/notification_list.html', context)
    
def mark_notification_as_read(request, pk):
    notification = Notification.objects.get(pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect(request.META.get('HTTP_REFERER', 'notifications_list'))

#Temp_Prisoner
User = get_user_model()

@login_required
def temp_prisoner_create(request):
    if not request.user.is_authenticated or not request.user.is_prison_account:
        return redirect('not_found')

    if request.method == "POST":
        form = TempPrisonerForm(request.POST)

        if form.is_valid():
            temp_prisoner = form.save(commit=False)
            user_full_name = f"{request.user.first_name} {request.user.last_name}"
            user_role = f"{request.user.role}"  

            # Serialize the full name and role into a JSON string
            temp_prisoner.created_by = f"{user_role}, {user_full_name}"

            temp_prisoner.prison = request.user.prison
            temp_prisoner.status = 'pending'

            temp_prisoner.save()  # Save the temp_prisoner instance

            # Notify court users
            court_users = User.objects.filter(court=temp_prisoner.court)
            for user in court_users:
                Notification.objects.create(
                    user=user,
                    message=f'New TempPrisoner request from {temp_prisoner.prison}'
                )

            return JsonResponse({'message': 'Temp Prisoner request sent successfully.'}, status=200)
        else:
            return JsonResponse({'message': 'Form is not valid.', 'errors': form.errors}, status=400)

    else:
        form = TempPrisonerForm()

    return render(request, 'temp_Prisoners/temp_prisoner_form.html', {'form': form})
    
@login_required
def temp_prisoner_list(request):
    temp_prisoners = Temp_prisoner.objects.filter(prison=request.user.prison)
    return render(request, 'temp_Prisoners/temp_prisoner_list.html', {'temp_prisoners': temp_prisoners})

@login_required
def temp_prisoner_requested_list(request):
    temp_prisoners = Temp_prisoner.objects.filter(court=request.user.court)
    return render(request, 'temp_Prisoners/temp_prisoner_requested_list.html', {'temp_prisoners': temp_prisoners})

@login_required
def temp_prisoner_detail(request, pk):
    temp_prisoner = Temp_prisoner.objects.get(pk=pk)
    if request.method == "POST":
        decision = request.POST.get('decision')
        if decision == 'accept':
            temp_prisoner.status = 'accepted'
            messages.success(request, 'The requested prisoner is accepted.')
        elif decision == 'reject':
            temp_prisoner.status = 'rejected'
            messages.error(request, 'The requested prisoner is rejected.')
        temp_prisoner.save()

        # Notify all officers in the prison
        officers = User.objects.filter(prison=temp_prisoner.prison)
        for officer in officers:
            Notification.objects.create(
                user=officer,
                message=f'Your request for {temp_prisoner.pri_fname} {temp_prisoner.pri_lname} has been {temp_prisoner.status}.'
            )

    return render(request, 'temp_Prisoners/temp_prisoner_detail.html', {'temp_prisoner': temp_prisoner})

def temp_prisoner_update(request, temp_prisoner_id):
    temp_prisoner = get_object_or_404(Temp_prisoner, pk=temp_prisoner_id)
    if request.method == 'POST':
        form = TempPrisonerForm(request.POST, instance=temp_prisoner)
        if form.is_valid():
            temp_prisoner = form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Temporary prisoner updated successfully.',
                'temp_prisoner_html': render_to_string('temp_prisoner_row.html', {'temp_prisoner': temp_prisoner})
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Form is not valid.'}, status=400)
    else:
        form = TempPrisonerForm(instance=temp_prisoner)
    return render(request, 'temp_prisoner_form.html', {'form': form, 'temp_prisoner_id': temp_prisoner_id})

def temp_prisoner_delete(request, temp_prisoner_id):
    temp_prisoner = get_object_or_404(Temp_prisoner, pk=temp_prisoner_id)
    if request.method == 'POST':
        temp_prisoner.delete()
        return JsonResponse({'status': 'success', 'message': 'Temporary prisoner deleted successfully.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

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
