from django.urls import path
from .views import *

urlpatterns = [
    path('register-acc/', register, name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),
    path('login/admin/', CustomLoginView.as_view(), name='login'),
    path('password_change/', password_change, name='password_change'),
    path('logout/', logout_view, name='logout'),
    #path('court/<int:court_id>/', views.court_detail, name='court_detail'),
    path('add_profile/', add_profile, name='add_profile'),

    #Manage Accounts
    path('create-account/', create_account, name='create_account'),
    path('officer-details/', get_officer_details, name='get_officer_details'),
    #Visitor CRUD
    path('register/', register_view, name='registerv'),
    path('login/', login_view, name='loginv'),
    path('logout/', logout_view_v, name='logoutv'),
    path('forget-password/', CustomPasswordResetView.as_view(), name='forget_password'),
    #path('reset-password/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='reset_password'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('resend-activation-email/', resend_activation_email, name='resend_activation_email'),

    #Appointment
    path('get_cities/', get_cities, name='get_cities'),
    path('get_prisons/', get_prisons, name='get_prisons'),
    path('get_prison_info/', get_prison_info, name='get_prison_info'),
    path('find_prisoner/', find_prisoner, name='find_prisoner'),
    path('appointment/create/', create_appointment, name='appointment_create'),
]

