# forms.py
from django import forms
from .models import Temp_prisoner
from Court.models import Occupancy

class TempPrisonerForm(forms.ModelForm):
    class Meta:
        model = Temp_prisoner
        exclude = ['prison', 'status', 'created_by', 'created_at']
        widgets = {
            'pri_fname': forms.TextInput(attrs={'placeholder': 'Prisoner First Name...', 'class': 'form-control'}),
            'pri_mname': forms.TextInput(attrs={'placeholder': 'Prisoner Middle Name...', 'class': 'form-control'}),
            'pri_lname': forms.TextInput(attrs={'placeholder': 'Prisoner Last Name...', 'class': 'form-control'}),
            'pri_gender': forms.Select(attrs={'class': 'select2'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Prisoner age...', 'class': 'form-control'}),
            'pri_date_of_arrest': forms.DateInput(format='%Y-%m-%d', attrs={'placeholder': 'yyyy-mm-dd', 'class': 'form-control air-datepicker', 'data-position': 'bottom right', 'id': 'id_pri_date_of_arrest'}),
            'pri_nationality': forms.TextInput(attrs={'placeholder': 'Prisoner Nationality...', 'class': 'form-control'}),
            'pri_city': forms.TextInput(attrs={'placeholder': 'Prisoner City...', 'class': 'form-control'}),
            'pri_subcity': forms.TextInput(attrs={'placeholder': 'Prisoner SubCity...', 'class': 'form-control'}),
            'pri_woreda': forms.TextInput(attrs={'placeholder': 'Prisoner Woreda...', 'class': 'form-control'}),
            'pri_kebele': forms.TextInput(attrs={'placeholder': 'Prisoner Kebele...', 'class': 'form-control'}),
            'pri_telno': forms.TextInput(attrs={'placeholder': 'Prisoner Phone No...', 'class': 'form-control'}),
            'court': forms.Select(attrs={'class': 'select2'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description...', 'class': 'textarea form-control'}),
        }

class OccupancyForm(forms.ModelForm):
    class Meta:
        model = Occupancy
        fields = ['room_code', 'block', 'room_type', 'no_of_beds', 'remaining_bed']
        widgets = {
            'room_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room Code'}),
            'block': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Block'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}, choices=Occupancy.ROOM_TYPE_CHOICES),
        }
