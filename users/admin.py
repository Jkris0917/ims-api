from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username','email','full_name', 'role','is_active')
    list_filter = ('role','is_active')
    search_fields = ('username','email','full_name')
    ordering = ('username',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Info', {
            'fields': ('full_name','role','email'),
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role & Info', {
           'fields': ('full_name','role','email'),
        }),
    )