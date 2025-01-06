from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth import get_user_model

class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class SubCity(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.city.name})"

class Prison(models.Model):
    LOW_LEVEL = 'Low'
    MID_LEVEL = 'Mid'
    HIGH_LEVEL = 'High'

    PRISON_TYPE_CHOICES = [
        (LOW_LEVEL, 'Low Level'),
        (MID_LEVEL, 'Mid Level'),
        (HIGH_LEVEL, 'High Level'),
    ]

    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    sub_city = models.ForeignKey(SubCity, on_delete=models.CASCADE)
    prison_type = models.CharField(max_length=10, choices=PRISON_TYPE_CHOICES)
    location = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.name

class Court(models.Model):
    LOW_LEVEL = 'Low'
    MID_LEVEL = 'Mid'
    HIGH_LEVEL = 'High'

    COURT_TYPE_CHOICES = [
        (LOW_LEVEL, 'Low Level'),
        (MID_LEVEL, 'Mid Level'),
        (HIGH_LEVEL, 'High Level'),
    ]

    name = models.CharField(max_length=300)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    sub_city = models.ForeignKey(SubCity, on_delete=models.CASCADE)
    court_type = models.CharField(max_length=10, choices=COURT_TYPE_CHOICES)
    location = models.CharField(max_length=300)
    judge_name = models.CharField(max_length=300,null=True, blank=True)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name
    
class role(models.Model):
    role = models.CharField(max_length=100)

    def __str__(self):
        return self.role
    
class CustomUser(AbstractUser):
    is_court_account = models.BooleanField(default=False)
    is_prison_account = models.BooleanField(default=False)
    is_visitor_account = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_police_station = models.BooleanField(default=False)
    court = models.ForeignKey('Court', on_delete=models.SET_NULL, null=True, blank=True)
    prison = models.ForeignKey('Prison', on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey('role', on_delete=models.SET_NULL, null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)
    must_change_password = models.BooleanField(default=True)
    must_add_profile = models.BooleanField(default=True)

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    RELATION_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Brother', 'Brother'),
        ('Sister', 'Sister'),
        ('Spouse', 'Spouse'),
        ('Child', 'Child'),
        ('Friend', 'Friend'),
        ('Other', 'Other'),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    national_id_image = models.ImageField(upload_to='national_id_image/', null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    relation = models.CharField(max_length=10,choices=RELATION_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.user.username
    
User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.message
