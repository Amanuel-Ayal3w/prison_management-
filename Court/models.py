from django.contrib.auth import get_user_model
from django.utils import timezone
from Accounts.models import *
from django.db import models
import random
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class Occupancy(models.Model):
 
    ROOM_TYPE_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    room_code = models.CharField(max_length=10, unique=True)
    block = models.CharField(max_length=25)
    room_type = models.CharField(max_length=25, choices=ROOM_TYPE_CHOICES)
    no_of_beds = models.PositiveIntegerField(null=True, blank=True)
    remaining_bed = models.PositiveIntegerField(null=True, blank=True)
    no_of_pri = models.PositiveIntegerField(default=0,null=True, blank=True)
    def __str__(self):
        return f"{self.block} - {self.room_code}"

class Prisoner(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    STATUS_CHOICES = [
        ('Prisoned', 'Prisoned'),
        ('Released','Released'),
    ]
     
    pri_id = models.AutoField(primary_key=True)
    national_id = models.CharField(max_length=50, null=True, blank=True)
    pri_code = models.CharField(max_length=50, null=True, blank=True)
    pri_fname = models.CharField(max_length=50)
    pri_mname = models.CharField(max_length=50, null=True, blank=True)
    pri_lname = models.CharField(max_length=50)
    picture = models.ImageField(upload_to='prisoner_pictures/', null=True, blank=True)
    pri_gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    pri_dob = models.DateField()
    pri_nationality = models.CharField(max_length=50)
    pri_city = models.CharField(max_length=50)
    pri_subcity = models.CharField(max_length=50)
    pri_woreda = models.PositiveIntegerField()
    kebele = models.PositiveIntegerField(null=True, blank=True)
    pri_facecolor = models.CharField(max_length=50)
    pri_haircolor = models.CharField(max_length=50)
    pri_telno = models.CharField(max_length=20)
    pri_bodyweight_kg = models.FloatField()
    pri_height_m = models.FloatField()
    pri_date_of_arrest = models.DateField()
    pri_date_of_depart = models.DateField( null=True, blank=True)
    room_code = models.ForeignKey(Occupancy, on_delete=models.SET_NULL, null=True, blank=True)
    officer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    sentence_date = models.DateField()
    release_date = models.DateField()
    eligible_for_parole = models.BooleanField(default=False)
    rehabilitation_program_enrolled = models.BooleanField(default=False)
    prison = models.ForeignKey(Prison, on_delete=models.CASCADE)
    court = models.ForeignKey(Court, on_delete=models.CASCADE,null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Prisoned',null=True, blank=True)
    
    def __str__(self):
        return f'{self.pri_fname} {self.pri_lname}'
    
class CrimeDetail(models.Model):
    crime_code = models.AutoField(primary_key=True)
    crime_type = models.CharField(max_length=50)
    crime_description = models.TextField()
    cprisoner_id = models.ForeignKey(Prisoner, on_delete=models.CASCADE)

    def __str__(self):
        return self.crime_type

User = get_user_model()

class TempPrisoner(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    COURT_DECISION_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    pri_fname = models.CharField(max_length=50)
    pri_mname = models.CharField(max_length=50, null=True, blank=True)
    pri_lname = models.CharField(max_length=50)
    pri_gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    pri_nationality = models.CharField(max_length=50)
    pri_telno = models.CharField(max_length=20)
    pri_date_of_arrest = models.DateField()
    officer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    prison = models.ForeignKey(Prison, on_delete=models.CASCADE)
    court = models.ForeignKey(Court, on_delete=models.CASCADE, null=True, blank=True)
    court_decision = models.CharField(max_length=10, choices=COURT_DECISION_CHOICES, default='Pending')

    def __str__(self):
        return f'{self.pri_fname} {self.pri_lname}'

class Activity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('exercise', 'Exercise'),
        ('education', 'Education'),
        ('work', 'Work'),
        ('medical', 'Medical'),
        ('recreation', 'Recreation'),
        ('visitation', 'Visitation'),
        # Add more activity types as needed
    ]

    prisoner = models.ForeignKey(Prisoner, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)  # Optional detailed description
    start_time = models.DateTimeField()  # When the activity starts
    end_time = models.DateTimeField()  # When the activity ends
    location = models.CharField(max_length=100, blank=True, null=True)  # Where the activity takes place
    assigned_staff = models.CharField(max_length=100, blank=True, null=True) 
    status = models.CharField(max_length=20, default='scheduled', choices=[
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)  # When the activity was recorded
    updated_at = models.DateTimeField(auto_now=True)  # When the activity was last updated
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_activities')

    def __str__(self):
        return f"{self.prisoner.pri_fname} {self.prisoner.pri_lname} - {self.activity_type}"
    
class Discipline(models.Model):
    DISCIPLINE_TYPE_CHOICES = [
        ('minor', 'Minor'),
        ('major', 'Major'),
    ]

    prisoner = models.ForeignKey(Prisoner, on_delete=models.CASCADE, related_name='disciplines')
    discipline_type = models.CharField(max_length=20, choices=DISCIPLINE_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)  # Optional detailed description
    date = models.DateTimeField()  # When the discipline occurred
    assigned_staff = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_disciplines')
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)  # When the discipline was recorded
    updated_at = models.DateTimeField(auto_now=True)  # When the discipline was last updated
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_disciplines')

    def __str__(self):
        return f"{self.prisoner.pri_fname} {self.prisoner.pri_lname} - {self.discipline_type}"
    

class Transfer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('denied', 'Denied'),
    ]
    prison = models.ForeignKey(Prison, on_delete=models.CASCADE, null=True, blank=True, related_name='transfersfrom')
    prisoner = models.ForeignKey(Prisoner, on_delete=models.CASCADE, related_name='transfers')
    to_prison = models.ForeignKey(Prison, on_delete=models.CASCADE, related_name='transfers')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='requested_transfers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transfer {self.prisoner.pri_fname} {self.prisoner.pri_lname} to {self.to_prison.name}"
    
class Parole(models.Model):
    prisoner = models.ForeignKey(Prisoner, on_delete=models.CASCADE)
    month = models.PositiveIntegerField()
    description = models.TextField()
    new_release_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Parole for {self.prisoner} by {self.created_by}"

@receiver(pre_save, sender=Parole)
def calculate_new_release_date(sender, instance, **kwargs):
    if instance.prisoner and instance.month:
        instance.new_release_date = instance.prisoner.release_date - relativedelta(months=instance.month)