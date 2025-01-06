from django import forms
from django.core.exceptions import ValidationError
from .models import *
from datetime import date
from Accounts.models import Prison

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['full_name', 'prisoner_id', 'prison', 'appointment_date', 'time_slot', 'email','for_self']

    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "ሙሉ ስም *"}),
    )
    prisoner_id = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "የእስረኛ መለያ ቁጥር * PR-001"}),
    )
    prison = forms.ModelChoiceField(
        queryset=Prison.objects.all(),
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    appointment_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control", "placeholder": "date"}),
    )
    time_slot = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Your Email Address *"}),
    )
    for_self = forms.HiddenInput()

    # Ensure time slot is not overbooked and prisoner is not double-booked
    def clean_time_slot(self):
        appointment_date = self.cleaned_data.get("appointment_date")
        time_slot = self.cleaned_data.get("time_slot")
        prisoner_id = self.cleaned_data.get("prisoner_id")
        prison = self.cleaned_data.get("prison")

        max_appointments_per_slot = 5  # Define maximum appointments per slot
        
        # Check if this time slot has reached the maximum number of appointments
        existing_appointments = Appointment.objects.filter(
            appointment_date=appointment_date,
            time_slot=time_slot,
            prison=prison,  # Filter by the selected prison
        ).count()

        if existing_appointments >= max_appointments_per_slot:
            raise ValidationError(f"The selected time slot '{time_slot}' is fully booked. Please choose another time.")

        # Check if the same prisoner is already appointed at this time slot and date
        prisoner_appointments = Appointment.objects.filter(
            appointment_date=appointment_date,
            time_slot=time_slot,
            prisoner_id=prisoner_id,
            prison=prison,  # Ensure the check is specific to the selected prison
        ).count()

        if prisoner_appointments > 0:
            raise ValidationError(f"The prisoner with ID '{prisoner_id}' is already booked at this time slot. Please select a different time or day.")

        return time_slot

class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['Fan_ID', 'name', 'age', 'gender', 'relationship_to_prisoner', 'contact_number', 'prison', 'prisoner', 'visit_date', 'time_slot','national_id_image']
        widgets = { 'prison': forms.HiddenInput(), 
                   'prisoner': forms.HiddenInput(),
                   'Fan_ID': forms.TextInput(attrs={"class": "form-control", "placeholder": "Fan ID"}),
                   'name': forms.TextInput(attrs={"class": "form-control", "placeholder": "Full Name"}),
                   'age': forms.TextInput(attrs={"class": "form-control", "placeholder": "Age"}),
                   'gender': forms.Select(attrs={"class": "form-control"}),
                   'relationship_to_prisoner': forms.TextInput(attrs={"class": "form-control", "placeholder": "Relationship to Prisoner"}),
                   'contact_number': forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone"}),
                   'visit_date': forms.DateInput(attrs={"type": "date", "class": "form-control", "placeholder": "date"}),
                   'time_slot': forms.Select(attrs={"class": "form-control", "value":'', "placeholder":'Select a time slot',"id":'time_slot',"name":'time_slot'}),
                   'national_id_image': forms.FileInput(attrs={'class': 'form-control'}),}
        
class DisabledSlotForm(forms.ModelForm):
    class Meta:
        model = DisabledSlot
        fields = ['prison', 'date', 'description']
        widgets = {
            'prison': forms.HiddenInput(),
            'date': forms.DateInput(attrs={"type": "date", "class": "form-control", "placeholder": "date"}),
            'description': forms.Textarea(attrs={"class": "form-control", "placeholder": "Description (optional)"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")

        if not date:
            raise forms.ValidationError("A date must be provided.")

        return cleaned_data