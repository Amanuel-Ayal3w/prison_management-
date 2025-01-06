from django import forms
from .models import Profile, CustomUser
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm, UserCreationForm
from django.forms.widgets import TextInput
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from .models import *

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'is_court_account', 'is_prison_account', 'court', 'prison', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_court_account'].label = 'Is Court Account'
        self.fields['is_prison_account'].label = 'Is Prison Account'
        self.fields['court'].label = 'Court'
        self.fields['prison'].label = 'Prison'
        self.fields['role'].label = 'Role'

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'type':'username', 'name':'email' ,'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=TextInput(attrs={'type':'password', 'name':'password','class': 'form-control', 'placeholder': 'Password'}))

    
CustomUser = get_user_model()

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Profile
        fields = ['picture', 'gender', 'date_of_birth', 'phone', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs.get('instance').user if kwargs.get('instance') else None
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile.save()
        return profile

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['new_password1'].help_text = None
        self.fields['new_password2'].help_text = None
        self.fields['new_password1'].widget = forms.TextInput(attrs={'type': 'password', 'class': 'form-control', 'placeholder': 'New Password'})
        self.fields['new_password2'].widget = forms.TextInput(attrs={'type': 'password', 'class': 'form-control', 'placeholder': 'Confirm New Password'})

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if check_password(new_password1, self.user.password):
            raise forms.ValidationError("The new password cannot be the same as the old password.")
        return new_password1

class AddProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'picture', 'gender', 'date_of_birth', 'phone', 'address']
        widgets = {
            'picture': forms.FileInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(format='%Y-%m-%d',attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
        }

#Visitor Form
class CustomRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'name':'password1', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','name':'password2', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = CustomUser
        fields = ('username','email', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

class CustomUserCreationForm(forms.ModelForm):
    role = forms.ModelChoiceField(queryset=role.objects.none(), required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'role', 'court', 'prison']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control select2'}),
            'court': forms.Select(attrs={'class': 'form-control'}),
            'prison': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the currently logged-in user
        super().__init__(*args, **kwargs)

        # Dynamically adjust role choices based on the current user's role
        if user.role.role == 'admin':
            self.fields['role'].queryset = role.objects.filter(role__in=['Court', 'Commissioner'])
            self.fields['court'].queryset = Court.objects.all()  # Admin can select any court
            self.fields['prison'].queryset = Prison.objects.all()  # No prison for admin when creating courts or commissioners
        elif user.role.role == 'Commissioner':
            self.fields['role'].queryset = role.objects.filter(role='Inspector')
            self.fields['court'].queryset = Court.objects.none()  # No court selection for commissioners
            self.fields['prison'].queryset = Prison.objects.all()  # Commissioner can select any prison
        elif user.role.role == 'Inspector':
            self.fields['role'].queryset = role.objects.filter(role='Officer')
            self.fields['court'].queryset = Court.objects.none()  # No court selection for inspectors
            self.fields['prison'].queryset = Prison.objects.filter(id=user.prison.id)  # Inspector selects their own prison
        elif user.role.role == 'Court'| user.is_court_account == True:
            self.fields['role'].queryset = role.objects.none()
            self.fields['court'].queryset = Court.objects.filter(id=user.court.id)  # No court selection for inspectors
            self.fields['prison'].queryset = Prison.objects.none() # Inspector selects their own prison
