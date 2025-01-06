from django.contrib import admin
from .models import *

class PrisonerAdmin(admin.ModelAdmin):
    list_display = ('pri_id', 'pri_fname', 'pri_lname', 'pri_gender', 'pri_nationality', 'status')
    search_fields = ('pri_fname', 'pri_lname', 'pri_nationality', 'status')
    list_filter = ('pri_gender', 'pri_nationality', 'status')

admin.site.register(Prisoner, PrisonerAdmin)
admin.site.register(CrimeDetail)  
admin.site.register(Occupancy)  
admin.site.register(Activity)
admin.site.register(Transfer)
admin.site.register(Discipline)


@admin.register(Parole)
class ParoleAdmin(admin.ModelAdmin):
    list_display = ('prisoner', 'month', 'new_release_date', 'created_by', 'created_at')
    search_fields = ('prisoner__name', 'description')
    list_filter = ('created_at', 'new_release_date')