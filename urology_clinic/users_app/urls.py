from django.urls import path
from . import views  # Import views from the current app
from .views import patient_signup, doctor_signup, login_view, logout_view, patient_dashboard, doctor_dashboard, \
    doctor_timesharing_booking, doctor_devicesharing_booking, patient_appointment_booking, edit_patient_profile, \
    edit_doctor_profile, edit_timesharing, delete_timesharing, edit_devicesharing, delete_devicesharing, \
    edit_appointment, delete_appointment, doctor_calendar_view, doctor_calendar_events, patient_calendar_view, \
    patient_calendar_events

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('patient/dashboard/', patient_dashboard, name='patient_dashboard'),
    path('doctor/dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('signup/patient/', patient_signup, name='patient_signup'),
    path('signup/doctor/', doctor_signup, name='doctor_signup'),
    path('doctor/timesharing/', doctor_timesharing_booking, name='timesharing_booking'),
    path('doctor/devicesharing/', doctor_devicesharing_booking, name='devicesharing_booking'),
    path('patient/appointment/', patient_appointment_booking, name='appointment_booking'),
    path('profile/edit/patient/', edit_patient_profile, name='edit_patient_profile'),
    path('profile/edit/doctor/', edit_doctor_profile, name='edit_doctor_profile'),
    # Timesharing
    path('timesharing/edit/<int:pk>/', edit_timesharing, name='edit_timesharing'),
    path('timesharing/delete/<int:pk>/', delete_timesharing, name='delete_timesharing'),
    # Devicesharing
    path('devicesharing/edit/<int:pk>/', edit_devicesharing, name='edit_devicesharing'),
    path('devicesharing/delete/<int:pk>/', delete_devicesharing, name='delete_devicesharing'),
    # Appointment
    path('appointment/edit/<int:pk>/', edit_appointment, name='edit_appointment'),
    path('appointment/delete/<int:pk>/', delete_appointment, name='delete_appointment'),
    # Dashboard URLs
    path('doctor/dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', patient_dashboard, name='patient_dashboard'),
    # Doctor Calendars
    path('calendar/doctor/timesharing/', doctor_calendar_view, {'calendar_type': 'timesharing'}, name='doctor_timesharing_calendar'),
    path('calendar/doctor/devicesharing/', doctor_calendar_view, {'calendar_type': 'devicesharing'}, name='doctor_devicesharing_calendar'),
    path('api/calendar/doctor/<str:calendar_type>/', doctor_calendar_events, name='doctor_calendar_events'),
    # Patient Calendar
    path('calendar/patient/', patient_calendar_view, name='patient_calendar'),
    path('api/calendar/patient/', patient_calendar_events, name='patient_calendar_events'),


]
