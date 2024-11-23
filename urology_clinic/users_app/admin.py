from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Patient, Doctor, Appointment, Timesharing, Device, Devicesharing

# Customize CustomUser Admin Panel
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': ('role',),  # Add 'role' to the admin panel
        }),
    )
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')

# Patient Admin
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address', 'date_of_birth')
    search_fields = ('user__username', 'phone')
    list_filter = ('user__is_active',)

# Doctor Admin
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'bio')
    search_fields = ('user__username', 'specialization')
    list_filter = ('user__is_active',)

# Appointment Admin
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'notes')
    search_fields = ('patient__user__username', 'doctor__user__username', 'date')
    list_filter = ('date', 'doctor')

# Timesharing Admin
class TimesharingAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time')
    search_fields = ('doctor__user__username', 'date')
    list_filter = ('date',)

# Device Admin
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)

# Devicesharing Admin
class DevicesharingAdmin(admin.ModelAdmin):
    list_display = ('device', 'doctor', 'date', 'start_time', 'end_time')
    search_fields = ('device__name', 'doctor__user__username', 'date')
    list_filter = ('date', 'device')

# Register Models with Admin Site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Timesharing, TimesharingAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Devicesharing, DevicesharingAdmin)
