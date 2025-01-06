from django.urls import path
from Appointment.views import *

urlpatterns = [
    path('', index, name='index'),
    path('test_home/',test_home, name='test_home'),

    path('get_cities/', get_cities, name='get_cities'),
    path('get_prisons/', get_prisons, name='get_prisons'),
    path('get_prison_info/', get_prison_info, name='get_prison_info'),
    path('get_prisoner_info/', get_prisoner_info, name='get_prisoner_info'),
    path('get_time_slots/', get_available_time_slots, name='get_time_slots'),
    path('submit_appointment/', submit_appointment, name='submit_appointment'),
    path('find_appointment/', find_appointment, name='find_appointment'),
    path('disable_slot/', disable_slot, name='disable_slot'),
    path('disabled_slots_list/', disabled_slots_list, name='disabled_slots_list'),


    path('create_visitor/', create_visitor, name='create_visitor'),
    path('visitor_list/', visitor_list, name='visitor_list'),
    path('visitor_detail/<int:pk>/', visitor_detail, name='visitor_detail'),
    path('update_visitor/<int:pk>/', update_visitor, name='update_visitor'),
    path('delete_visitor/<int:pk>/', delete_visitor, name='delete_visitor'),

]
    

