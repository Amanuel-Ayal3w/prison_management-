from django.forms import ValidationError, inlineformset_factory
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import *
from Accounts.models import CustomUser

class PrisonerForm(forms.ModelForm):
    class Meta:
        model = Prisoner
        fields = '__all__'
        widgets = {
            'pri_fname': forms.TextInput(attrs={'placeholder': 'Prisoner First Name...', 'class': 'form-control'}),
            'pri_mname': forms.TextInput(attrs={'placeholder': 'Prisoner Middle Name...', 'class': 'form-control'}),
            'pri_lname': forms.TextInput(attrs={'placeholder': 'Prisoner Last Name...', 'class': 'form-control'}),
            'pri_gender': forms.Select(attrs={'class': 'select2'}),
            'national_id': forms.TextInput(attrs={'placeholder': 'National ID Number...', 'class': 'form-control'}),
            'pri_dob': forms.DateInput(format='%Y-%m-%d', attrs={'placeholder': 'yyyy-mm-dd', 'class': 'form-control air-datepicker', 'data-position': 'bottom right', 'id': 'id_pri_dob'}),
            'pri_nationality': forms.TextInput(attrs={'placeholder': 'Prisoner Nationality...', 'class': 'form-control'}),
            'pri_city': forms.TextInput(attrs={'placeholder': 'Prisoner City...', 'class': 'form-control'}),
            'pri_subcity': forms.TextInput(attrs={'placeholder': 'Prisoner SubCity...', 'class': 'form-control'}),
            'pri_woreda': forms.TextInput(attrs={'placeholder': 'Prisoner Woreda...', 'class': 'form-control'}),
            'pri_facecolor': forms.TextInput(attrs={'placeholder': 'Prisoner Face Color...', 'class': 'form-control'}),
            'pri_haircolor': forms.TextInput(attrs={'placeholder': 'Prisoner Hair Color...', 'class': 'form-control'}),
            'pri_telno': forms.TextInput(attrs={'placeholder': 'Prisoner Phone No...', 'class': 'form-control'}),
            'pri_bodyweight_kg': forms.NumberInput(attrs={'placeholder': 'Prisoner Weight...', 'class': 'form-control'}),
            'pri_height_m': forms.NumberInput(attrs={'placeholder': 'Prisoner Height...', 'class': 'form-control'}),
            'pri_date_of_arrest': forms.DateInput(format='%Y-%m-%d', attrs={'placeholder': 'yyyy-mm-dd', 'class': 'form-control air-datepicker', 'data-position': 'bottom right', 'id': 'id_pri_date_of_arrest'}),
            'pri_date_of_depart': forms.DateInput(format='%Y-%m-%d', attrs={'placeholder': 'yyyy-mm-dd', 'class': 'form-control air-datepicker', 'data-position': 'bottom right', 'id': 'id_pri_date_of_depart'}),
            'room_code': forms.Select(attrs={'class': 'select2'}),
            'sentence_date': forms.DateInput(format='%Y-%m-%d', attrs={'placeholder': 'yyyy-mm-dd', 'class': 'form-control air-datepicker', 'data-position': 'bottom right', 'id': 'id_sentence_date'}),
            'release_date': forms.DateInput(format='%Y-%m-%d', attrs={'placeholder': 'yyyy-mm-dd', 'class': 'form-control air-datepicker', 'data-position': 'bottom right', 'id': 'id_release_date'}),
            'eligible_for_parole': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'flexSwitchCheckDefault'}),
            'rehabilitation_program_enrolled': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'flexSwitchCheckRehabilitation'}),
            'prison': forms.Select(attrs={'class': 'select2'}),
            'picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PrisonerForm, self).__init__(*args, **kwargs)
        self.fields['room_code'].required = False

class CrimeDetailForm(forms.ModelForm):
    class Meta:
        model = CrimeDetail
        fields = ['crime_type', 'crime_description']
        widgets = {
            'crime_type': forms.TextInput(attrs={'placeholder': 'Crime Type...', 'class': 'form-control'}),
            'crime_description': forms.Textarea(attrs={'placeholder': 'Crime Description...', 'class': 'textarea form-control'}),
        }

CrimeDetailFormSet = inlineformset_factory(Prisoner, CrimeDetail, form=CrimeDetailForm, extra=1)

class OccupancyForm(forms.ModelForm):
    class Meta:
        model = Occupancy
        fields = '__all__'
        widgets = {
            'room_code': forms.TextInput(attrs={'class': 'form-control'}),
            'room_type': forms.Select(attrs={'class': 'select2'}),
            'room_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'prisoner': forms.Select(attrs={'class': 'select2'}),
            'prison': forms.Select(attrs={'class': 'select2'}),
        }

class TempPrisonerForm(forms.ModelForm):
    class Meta:
        model = TempPrisoner
        fields = [
            'pri_fname', 'pri_mname', 'pri_lname', 'pri_gender',
            'pri_nationality', 'pri_telno', 'pri_date_of_arrest',
            'court'
        ]
        widgets = {
            'pri_fname': forms.TextInput(attrs={'placeholder': 'Prisoner First Name...', 'class': 'form-control'}),
            'pri_mname': forms.TextInput(attrs={'placeholder': 'Prisoner Middle Name...', 'class': 'form-control'}),
            'pri_lname': forms.TextInput(attrs={'placeholder': 'Prisoner Last Name...', 'class': 'form-control'}),
            'pri_gender': forms.Select(attrs={'class': 'select2'}),
            'pri_nationality': forms.TextInput(attrs={'placeholder': 'Prisoner Nationality...', 'class': 'form-control'}),
            'pri_telno': forms.TextInput(attrs={'placeholder': 'Prisoner Phone No...', 'class': 'form-control'}),
            'pri_date_of_arrest': forms.DateInput(format='%Y-%m-%d', attrs={'placeholder': 'yyyy-mm-dd', 'class': 'form-control air-datepicker', 'data-position': 'bottom right', 'id': 'id_pri_date_of_arrest'}),
            'court': forms.Select(attrs={'class': 'select2'}),
        }


class PrisonForm(forms.ModelForm):
    class Meta:
        model = Prison
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'select2'}),
            'sub_city': forms.Select(attrs={'class': 'select2'}),
            'prison_type': forms.Select(attrs={'class': 'select2'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['activity_type', 'description', 'start_time', 'end_time', 'location', 'assigned_staff', 'status']
        widgets = {
            'activity_type': forms.Select(attrs={'class': 'form-control select2'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'assigned_staff': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'select2'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise ValidationError(_('End time must be after start time.'))
        return cleaned_data

class DisciplineForm(forms.ModelForm):
    class Meta:
        model = Discipline
        fields = ['discipline_type', 'description', 'date', 'assigned_staff', 'status']
        widgets = {
            'discipline_type': forms.Select(attrs={'class': 'form-control select2'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'assigned_staff': forms.Select(attrs={'class': 'form-control select2'}),  # Changed to Select widget
            'status': forms.Select(attrs={'class': 'form-control select2'}),
        }

    def __init__(self, *args, **kwargs):
        prisoner = kwargs.pop('prisoner', None)  # Pop the prisoner object passed during form initialization
        super().__init__(*args, **kwargs)

        if prisoner:
            # Filter users by the same prison and role 'Officer'
            self.fields['assigned_staff'].queryset = CustomUser.objects.filter(
                prison=prisoner.prison,  # Adjust according to the actual relationship between User and Prison
                role__role='Officer'  # Ensure this matches the role field and its value correctly
            )

class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['to_prison', 'description']
        widgets = {
            'to_prison': forms.Select(attrs={'class': 'form-control select2'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pop the user object passed during form initialization
        super().__init__(*args, **kwargs)
        if user:
            # Exclude the user's prison from the queryset
            self.fields['to_prison'].queryset = Prison.objects.exclude(id=user.prison.id)
        else:
            self.fields['to_prison'].queryset = Prison.objects.all()  # Adjust queryset if needed

class ParoleForm(forms.ModelForm):
    class Meta:
        model = Parole
        fields = ['month', 'description']
        widgets = {
            'month': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }