from django.db import models
from django.contrib.auth.models import User
from Court.models import Prison, Court
from Accounts.models import *

class Temp_prisoner(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    pri_id = models.AutoField(primary_key=True)
    pri_fname = models.CharField(max_length=50)
    pri_mname = models.CharField(max_length=50, null=True, blank=True)
    pri_lname = models.CharField(max_length=50)
    pri_gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.CharField(max_length=50)
    pri_nationality = models.CharField(max_length=50)
    pri_city = models.CharField(max_length=50)
    pri_subcity = models.CharField(max_length=50)
    pri_woreda = models.CharField(max_length=50)
    pri_kebele = models.CharField(max_length=50)
    pri_telno = models.CharField(max_length=20)
    pri_date_of_arrest = models.DateTimeField()
    prison = models.ForeignKey(Prison, on_delete=models.CASCADE,null=True, blank=True)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=700, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.pri_fname} {self.pri_lname}'

