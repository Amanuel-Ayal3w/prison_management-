from datetime import datetime
from .models import Appointment

def update_appointment_status(request):
    now = datetime.now()
    
    # Update appointments where the date is in the past
    expired_appointments = Appointment.objects.filter(appointment_date__lt=now.date(), status='pending')
    expired_appointments.update(status='expired')
    
    # Update appointments where the date is today but the time slot has passed
    today_appointments = Appointment.objects.filter(appointment_date=now.date(), status='pending')
    for appointment in today_appointments:
        # Assuming time_slot is stored as 'HH:MM AM/PM-HH:MM AM/PM'
        slot_end_time_str = appointment.time_slot.split('-')[1].strip()  # Get the end time of the slot
        slot_end_time = datetime.strptime(slot_end_time_str, "%I:%M %p").time()  # Parse time in 12-hour format
        
        if slot_end_time <= now.time():
            appointment.status = 'expired'
            appointment.save()
    
    return {}