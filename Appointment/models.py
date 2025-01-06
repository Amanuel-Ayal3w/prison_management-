from django.db import models
from Accounts.models import Prison
from Court.models import Prisoner
from django.contrib.auth import get_user_model
import random
import string

User = get_user_model()

def generate_confirmation_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class Appointment(models.Model):
    status_choices = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('expired', 'Expired'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    prison = models.ForeignKey(Prison, on_delete=models.CASCADE, null=True, blank=True)
    prisoner = models.ForeignKey(Prisoner, on_delete=models.CASCADE, null=True, blank=True)
    appointment_date = models.DateField(null=True, blank=True)
    time_slot = models.CharField(max_length=10, null=True, blank=True)
    confirmation_number = models.CharField(max_length=100, unique=True, default=generate_confirmation_number, null=True, blank=True)
    is_assigned = models.BooleanField(default=False)
    for_self = models.BooleanField(default=False)  # New attribute
    appointment_type = models.CharField(max_length=10, null=True, blank=True) 
    status = models.CharField(max_length=10, choices=status_choices, default='pending')
    def __str__(self):
        return f"{self.prison.name} - {self.appointment_date} at {self.time_slot} (Confirmation: {self.confirmation_number})"

class DisabledSlot(models.Model):
    prison = models.ForeignKey(Prison, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)  
    
    def __str__(self):
        return f"{self.prison.name} - {self.date} - {self.time_slot}"
    
class Visitor(models.Model):
    GENDER = {
        ('M','Male'),
        ('F', 'Female')
    }
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, related_name='visitors', null=True, blank=True)
    Fan_ID = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    age = models.CharField(max_length=10, null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER, null=True, blank=True)
    relationship_to_prisoner = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    national_id_image = models.ImageField(upload_to='national_id_image/', null=True, blank=True)
    
    # Optional fields for physical visits
    prison = models.ForeignKey(Prison, on_delete=models.CASCADE, null=True, blank=True)
    prisoner = models.ForeignKey(Prisoner, on_delete=models.CASCADE, null=True, blank=True)
    visit_date = models.DateField(null=True, blank=True)
    time_slot = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
            return f"{self.name} visiting {self.prisoner.pri_fname} at {self.prison.name} on {self.visit_date} at {self.time_slot}"
