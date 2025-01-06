from django.urls import path
from .views import *

urlpatterns = [
    #path('', Home, name='index'),
    #Prisoner CRUD
    path('Prisoner/list/', prisoner_list, name='prisoner_list'),
    path('prisoner/<int:pk>/', prisoner_detail, name='prisoner_detail'),
    path('prisoner/new/', prisoner_create, name='prisoner_create'),
    path('prisoner/<int:pk>/edit/', prisoner_update, name='prisoner_update'),
    path('prisoner/<int:pk>/delete/', prisoner_delete, name='prisoner_delete'),
    path('Prisoner/room/assign/<int:prisoner_id>/', prisoner_room_assign, name='prisoner_room_assign'),
    path('Prisoner/room/list', prisoner_room_list, name='prisoner_room_list'),

    #Prisoner Transfer
    #path('transfers/', transfer_list, name='transfer_list'),
    #path('transfer/<int:pk>/', transfer_detail, name='transfer_detail'),
    #path('transfer/new/', transfer_create, name='transfer_create'),
    #path('transfer/<int:pk>/edit/', transfer_update, name='transfer_update'),
    #path('transfer/<int:pk>/delete/', transfer_delete, name='transfer_delete'),

    #Add Room
    path('room/list/', room_list, name='room_list'),
    path('room/add/', add_room, name='add_room'),
    path('room/update/<int:pk>/', room_update, name='room_update'),
    path('room/delete/<int:pk>/', room_delete, name='room_delete'),

    #Add Activity
    path('prisoner/<int:prisoner_id>/create-activity/', save_activity, name='create_activity'),
    path('prisoner/activity/create/<int:prisoner_id>/', activity_form, name='activity_form'),
    path('Prisoner/activity/list', prisoner_activity_list, name='prisoner_activity_list'),
    path('prisoner/<int:prisoner_id>/activities/', activity_list, name='activity_list'),
    path('prisoner/<int:prisoner_id>/activity/<int:activity_id>/', activity_detail, name='activity_detail'),
    path('prisoner/<int:prisoner_id>/activity/<int:activity_id>/update/form/', activity_form, name='activity_update'),
    path('prisoner/<int:prisoner_id>/activity/<int:activity_id>/update/', save_activity, name='update_activity'),
    path('activity/<int:activity_id>/delete/', activity_delete, name='activity_delete'),
    
    #Descipline
    path('prisoner/<int:prisoner_id>/disciplines/', discipline_list, name='discipline_list'),
    path('discipline/<int:discipline_id>/', discipline_detail, name='discipline_detail'),
    path('discipline/create/<int:prisoner_id>/', discipline_create, name='discipline_create'),
    path('discipline/update/<int:discipline_id>/', discipline_update, name='discipline_update'),
    path('discipline/delete/<int:discipline_id>/', discipline_delete, name='discipline_delete'),
    path('prisoner/activity/add/list/', discipline_add_list, name='discipline_add_list'),

    #Transfer Request
    path('transger/add/list/', transfer_add_list, name='transfer_add_list'),
    path('transfers/', transfer_list, name='transfer_list'),
    path('transfer/<int:pk>/', transfer_detail, name='transfer_detail'),
    path('transfer/create/<int:prisoner_id>/', transfer_create, name='transfer_create'),
    path('transfer/update/<int:transfer_id>/', transfer_update, name='transfer_update'),
    path('transfer/delete/<int:transfer_id>/', transfer_delete, name='transfer_delete'),
    path('transfer/accept/<int:transfer_id>/', transfer_accept, name='transfer_accept'),
    path('transfer/reject/<int:transfer_id>/', transfer_reject, name='transfer_reject'),
    path('transfer/requested/list/', transfer_requested_list, name='transfer_requested_list'),

    #Paroel
    path('parole/add/list', parole_add_list, name='parole_add_list'),
    path('parole/create/<int:pk>/', create_parole, name='create_parole'),
    path('parole/update/<int:pk>/', update_parole, name='update_parole'),
    path('parole/delete/<int:pk>/', delete_parole, name='delete_parole'),
    path('parole/list/', parole_list, name='parole_list'),
    #404 Not-Found
    path('404/',not_found,name='not_found'),
]

