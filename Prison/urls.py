from django.urls import path
from .views import *

urlpatterns = [
    #Add Room
    path('room/list/', room_list, name='room_list'),
    path('room/add/', add_room, name='add_room'),
    path('room/update/<int:pk>/', room_update, name='room_update'),
    path('room/delete/<int:pk>/', room_delete, name='room_delete'),

    path('temp_prisoner/create/', temp_prisoner_create, name='temp_prisoner_create'),
    path('temp_prisoner/<int:pk>/', temp_prisoner_detail, name='temp_prisoner_detail'),
    path('temp_prisoner/list/', temp_prisoner_list, name='temp_prisoner_list'),
    path('temp_prisoner/requested/list/', temp_prisoner_requested_list, name='temp_prisoner_requested_list'),
    path('temp_prisoner/update/<int:temp_prisoner_id>/', temp_prisoner_update, name='temp_prisoner_update'),
    #path('temp_prisoner/delete/<int:temp_prisoner_id>/', temp_prisoner_delete, name='temp_prisoner_delete'),
    # Notifications URLs
    path('notifications/', list_notifications, name='notifications_list'),
    path('notifications/mark_as_read/<int:pk>/', mark_notification_as_read, name='notifications_mark_as_read'),

]

    
