from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.utils.translation import gettext_lazy as _

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

#this hides the user from django default admin site
#class CustomUserAdmin(UserAdmin):
#    model = CustomUser
#    list_display = ('username', 'is_court_account', 'is_prison_account', 'court', 'prison', 'role')
#    inlines = (ProfileInline,)

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email','must_change_password','must_add_profile','is_email_verified')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Additional info'), {'fields': ('is_court_account', 'is_prison_account','is_visitor_account', 'is_police_station', 'court', 'prison', 'role')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_court_account', 'is_prison_account', 'is_visitor_account','court', 'prison', 'role'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_visitor_account', 'is_court_account', 'is_prison_account', 'court', 'prison', 'role')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    inlines = (ProfileInline,)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Court)
admin.site.register(Prison)
admin.site.register(City)
admin.site.register(SubCity)
admin.site.register(role)
admin.site.register(Profile)
admin.site.register(Notification)

