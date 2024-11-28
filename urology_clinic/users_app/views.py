from datetime import datetime, timedelta

import requests
from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from .forms import DoctorSignupForm, PatientSignupForm, TimesharingForm, DevicesharingForm, AppointmentForm, \
    EditPatientProfileForm, EditDoctorProfileForm, EditTimesharingForm, EditAppointmentForm, EditDevicesharingForm
from .google_calendar_utils import get_google_calendar_service, sync_event_to_google, delete_event_from_google
from .models import Appointment, Device, Timesharing, Devicesharing, CustomUser, Doctor
from django.contrib.auth import authenticate, login, logout




def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on user role
            if user.role == 'patient':
                return redirect('patient_dashboard')  # URL name for patient dashboard
            elif user.role == 'doctor':
                return redirect('doctor_dashboard')  # URL name for doctor dashboard
            else:
                return redirect('admin:index')  # Redirect to admin dashboard for superusers
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'users_app/login.html')  # Render login template
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page
def patient_signup(request):
    if request.method == 'POST':
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = PatientSignupForm()
    return render(request, 'users_app/signup.html', {'form': form})
def doctor_signup(request):
    if request.method == 'POST':
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = DoctorSignupForm()
    return render(request, 'users_app/signup.html', {'form': form})
@login_required
def patient_dashboard(request):
    patient = request.user.patient_profile

    # Fetch the list of doctors
    doctors = Doctor.objects.select_related('user')

    return render(request, 'users_app/patient_dashboard.html', {
        'upcoming_appointments': Appointment.objects.filter(patient=patient).order_by('date', 'time'),
        'doctors': doctors,
    })
@login_required
def doctor_dashboard(request):
    doctor = request.user.doctor_profile

    # Fetch doctor's timesharing and devicesharing schedules
    current_datetime = now()
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    filtered_timesharing = Timesharing.objects.filter(
        doctor=doctor,
        date__gte=current_date).exclude(date=current_date,end_time__lt=current_time)
    filtered_devicesharing = Devicesharing.objects.filter(
        doctor=doctor,
        date__gte=current_date).exclude(date=current_date,end_time__lt=current_time)
    timesharing_schedule = filtered_timesharing
    devicesharing_schedule = filtered_devicesharing

    # Fetch appointments for the doctor
    appointments = Appointment.objects.filter(doctor=doctor,date__gte=current_date).order_by('date', 'time')

    return render(
        request,
        'users_app/doctor_dashboard.html',
        {
            'timesharing_schedule': timesharing_schedule,
            'devicesharing_schedule': devicesharing_schedule,
            'appointments': appointments,
        }
    )
@login_required
def edit_patient_profile(request):
    patient = request.user.patient_profile
    if request.method == 'POST':
        form = EditPatientProfileForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('patient_dashboard')  # Redirect to patient dashboard
    else:
        form = EditPatientProfileForm(instance=patient)
    return render(request, 'users_app/edit_profile.html', {'form': form, 'dashboard_url': 'patient_dashboard'})
@login_required
def edit_doctor_profile(request):
    doctor = request.user.doctor_profile
    if request.method == 'POST':
        form = EditDoctorProfileForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('doctor_dashboard')  # Redirect to doctor dashboard
    else:
        form = EditDoctorProfileForm(instance=doctor)
    return render(request, 'users_app/edit_profile.html', {'form': form, 'dashboard_url': 'doctor_dashboard'})
@login_required
def doctor_timesharing_booking(request):
    doctor = request.user.doctor_profile  # Assuming logged-in user is a doctor
    if request.method == 'POST':
        form = TimesharingForm(request.POST)
        if form.is_valid():
            timesharing = form.save(commit=False)
            timesharing.doctor = doctor
            timesharing.save()
            # Sync the new timesharing slot to Google Calendar
            try:
                sync_event_to_google(
                    timesharing,
                    calendar_id='5b3a5e462e5b278a71845c9665a9ac67315163f9f7f68857df482738016c1b42@group.calendar.google.com',  # Replace with your Timesharing calendar ID
                    summary=f"Booked by Dr. {timesharing.doctor.user.last_name}",
                    description="Timesharing slot",
                    start_time=f"{timesharing.date}T{timesharing.start_time}",
                    end_time=f"{timesharing.date}T{timesharing.end_time}",
                )
            except Exception as e:
                print(f"Error syncing timesharing to Google Calendar: {e}")
            return redirect('doctor_dashboard')  # Redirect to doctor dashboard
    else:
        form = TimesharingForm()
    return render(request, 'users_app/timesharing_booking.html', {'form': form})
@login_required
def doctor_devicesharing_booking(request):
    doctor = request.user.doctor_profile
    if request.method == 'POST':
        form = DevicesharingForm(request.POST)
        if form.is_valid():
            devicesharing = form.save(commit=False)
            devicesharing.doctor = doctor
            devicesharing.save()
            # Sync the new devicesharing slot to Google Calendar
            try:
                sync_event_to_google(
                    devicesharing,
                    calendar_id='5c6cc5ad80bba7d88ffcc5236a04035749282c8a1ddb324d23d7aca14455b05a@group.calendar.google.com',
                    # Replace with your Timesharing calendar ID
                    summary=f"Device {devicesharing.device.name} booked by Dr. {devicesharing.doctor.user.last_name}",
                    description="Devicesharing slot",
                    start_time=f"{devicesharing.date}T{devicesharing.start_time}",
                    end_time=f"{devicesharing.date}T{devicesharing.end_time}",
                )
            except Exception as e:
                print(f"Error syncing timesharing to Google Calendar: {e}")
            return redirect('doctor_dashboard')
    else:
        form = DevicesharingForm()
    return render(request, 'users_app/devicesharing_booking.html', {'form': form})
@login_required
def patient_appointment_booking(request):
    patient = request.user.patient_profile
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.save()
            # Sync the new devicesharing slot to Google Calendar
            try:
                sync_event_to_google(
                    appointment,
                    calendar_id='e89a1aac0c51f7e209b469ac42709b4fa1124ab5e4218f31637d5c48d0d8f306@group.calendar.google.com',
                    # Replace with your Timesharing calendar ID
                    summary=f"Appointment {appointment.patient.last_name} booked with Dr. {appointment.doctor.user.last_name}",
                    description="Timesharing slot",
                    start_time=f"{appointment.date}T{appointment.start_time}",
                    end_time=f"{appointment.date}T{appointment.end_time}",
                )
            except Exception as e:
                print(f"Error syncing timesharing to Google Calendar: {e}")
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm()
    return render(request, 'users_app/appointment_booking.html', {'form': form})
@login_required
def edit_timesharing(request, pk):
    timesharing = get_object_or_404(Timesharing, pk=pk, doctor=request.user.doctor_profile)
    if request.method == 'POST':
        form = EditTimesharingForm(request.POST, instance=timesharing)
        if form.is_valid():
            form.save()
            # Sync the updated event to Google Calendar
            sync_event_to_google(
                timesharing,
                calendar_id='5b3a5e462e5b278a71845c9665a9ac67315163f9f7f68857df482738016c1b42@group.calendar.google.com',
                summary=f"Booked by Dr. {timesharing.doctor.user.last_name}",
                description="Timesharing slot",
                start_time=f"{timesharing.date}T{timesharing.start_time}",
                end_time=f"{timesharing.date}T{timesharing.end_time}",
            )
            return redirect('doctor_dashboard')
    else:
        form = EditTimesharingForm(instance=timesharing)
    return render(request, 'users_app/edit_item.html', {'form': form, 'item_type': 'Timesharing', 'cancel_url': 'doctor_dashboard'})
@login_required
def edit_devicesharing(request, pk):
    devicesharing = get_object_or_404(Devicesharing, pk=pk, doctor=request.user.doctor_profile)
    if request.method == 'POST':
        form = EditDevicesharingForm(request.POST, instance=devicesharing)
        if form.is_valid():
            form.save()
            # Sync the updated event to Google Calendar

            sync_event_to_google(
                devicesharing,
                calendar_id='5c6cc5ad80bba7d88ffcc5236a04035749282c8a1ddb324d23d7aca14455b05a@group.calendar.google.com',
                # Replace with your Timesharing calendar ID
                summary=f"Device {devicesharing.device.name} booked by Dr. {devicesharing.doctor.user.last_name}",
                description="Timesharing slot",
                start_time=f"{devicesharing.date}T{devicesharing.start_time}",
                end_time=f"{devicesharing.date}T{devicesharing.end_time}",
            )
            return redirect('doctor_dashboard')
    else:
        form = EditDevicesharingForm(instance=devicesharing)
    return render(request, 'users_app/edit_item.html', {'form': form, 'item_type': 'Devicesharing', 'cancel_url': 'doctor_dashboard'})
@login_required
def edit_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user.patient_profile)
    if request.method == 'POST':
        form = EditAppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            # Sync the new devicesharing slot to Google Calendar
            try:
                sync_event_to_google(
                    appointment,
                    calendar_id='e89a1aac0c51f7e209b469ac42709b4fa1124ab5e4218f31637d5c48d0d8f306@group.calendar.google.com',
                    # Replace with your Timesharing calendar ID
                    summary=f"Appointment {appointment.patient.last_name} booked with Dr. {appointment.doctor.user.last_name}",
                    description="Devicesharing slot",
                    start_time=f"{appointment.date}T{appointment.start_time}",
                    end_time=f"{appointment.date}T{appointment.end_time}",
                )
            except Exception as e:
                print(f"Error syncing timesharing to Google Calendar: {e}")
            return redirect('patient_dashboard')
    else:
        form = EditAppointmentForm(instance=appointment)
    return render(request, 'users_app/edit_item.html', {'form': form, 'item_type': 'Appointment', 'cancel_url': 'patient_dashboard'})
@login_required
def delete_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user.patient_profile)
    if request.method == 'POST':
        appointment.delete()
        delete_event_from_google(appointment, calendar_id='e89a1aac0c51f7e209b469ac42709b4fa1124ab5e4218f31637d5c48d0d8f306@group.calendar.google.com')
        return redirect('patient_dashboard')
    return render(request, 'users_app/confirm_delete.html', {'item_type': 'Appointment'})
@login_required
def delete_timesharing(request, pk):
    timesharing = get_object_or_404(Timesharing, pk=pk, doctor=request.user.doctor_profile)
    if request.method == 'POST':
        timesharing.delete()
        delete_event_from_google(timesharing, calendar_id='5b3a5e462e5b278a71845c9665a9ac67315163f9f7f68857df482738016c1b42@group.calendar.google.com')
        return redirect('doctor_dashboard')
    return render(request, 'users_app/confirm_delete.html', {'item_type': 'Timesharing', 'cancel_url': 'doctor_dashboard'})
@login_required
def delete_devicesharing(request, pk):
    devicesharing = get_object_or_404(Devicesharing, pk=pk, doctor=request.user.doctor_profile)
    if request.method == 'POST':
        devicesharing.delete()
        delete_event_from_google(devicesharing, calendar_id='5c6cc5ad80bba7d88ffcc5236a04035749282c8a1ddb324d23d7aca14455b05a@group.calendar.google.com')
        return redirect('doctor_dashboard')
    return render(request, 'users_app/confirm_delete.html', {'item_type': 'Devicesharing', 'cancel_url': 'doctor_dashboard'})
@login_required
def doctor_calendar_events(request, calendar_type):
    doctor = request.user.doctor_profile
    events = []

    if calendar_type == 'timesharing':
        # Fetch timesharing slots
        timesharing_slots = Timesharing.objects.filter(doctor=doctor)
        for slot in timesharing_slots:
            events.append({
                'title': f"Booked Timeslot by Dr. {slot.doctor.user.last_name}",
                'start': f"{slot.date}T{slot.start_time}",
                'end': f"{slot.date}T{slot.end_time}",
                'color': 'red',
            })

    elif calendar_type == 'devicesharing':
        # Fetch devicesharing slots
        devicesharing_slots = Devicesharing.objects.filter(doctor=doctor)
        for slot in devicesharing_slots:
            events.append({
                'title': f"Device: {slot.device.name} booked by Dr. {slot.doctor.user.last_name}",
                'start': f"{slot.date}T{slot.start_time}",
                'end': f"{slot.date}T{slot.end_time}",
                'color': 'blue',
            })

    return JsonResponse(events, safe=False)
@login_required
def patient_calendar_events(request):
    doctor_id = request.GET.get('doctor_id')  # Retrieve doctor ID from query string
    events = []

    if doctor_id:
        # Fetch doctor's timesharing slots
        timesharing_slots = Timesharing.objects.filter(doctor__id=doctor_id)

        for slot in timesharing_slots:
            # Fetch all appointments within this timesharing slot
            appointments = Appointment.objects.filter(
                doctor__id=doctor_id,
                date=slot.date,
                time__gte=slot.start_time,
                time__lt=slot.end_time
            ).order_by('time')

            # Track free time within the timesharing slot
            current_time = slot.start_time
            for appointment in appointments:
                # Add a free slot before the appointment if any exists
                if current_time < appointment.time:
                    events.append({
                        'title': 'Free Slot',
                        'start': f"{slot.date}T{current_time}",
                        'end': f"{slot.date}T{appointment.time}",
                        'color': 'green',
                    })
                # Add the booked appointment
                events.append({
                    'title': "Booked",
                    'start': f"{slot.date}T{appointment.time}",
                    'end': f"{slot.date}T{(datetime.combine(slot.date, appointment.time) + timedelta(minutes=15)).time()}",
                    'color': 'red',
                })
                # Update current time to the end of the booked slot
                current_time = (datetime.combine(slot.date, appointment.time) + timedelta(minutes=15)).time()

            # Add any remaining free time after the last appointment
            if current_time < slot.end_time:
                events.append({
                    'start': f"{slot.date}T{current_time}",
                    'end': f"{slot.date}T{slot.end_time}",
                    'color': 'green',
                })

    return JsonResponse(events, safe=False)
@login_required
def doctor_calendar_view(request, calendar_type):
    events_url = f"/api/calendar/doctor/{calendar_type}/"
    doctor = request.user.doctor_profile
    return render(request, 'users_app/calendar_view.html', {'events_url': events_url, 'doctor':doctor})
@login_required
def patient_calendar_view(request):
    doctor_id = request.GET.get('doctor_id')  # Retrieve doctor ID from query string
    doctor = get_object_or_404(Doctor,id=doctor_id)
    if not doctor_id:
        return render(request, 'users_app/error.html', {'message': 'No doctor selected.'})

    events_url = f"/api/calendar/patient/?doctor_id={doctor_id}"
    return render(request, 'users_app/calendar_view.html', {'events_url': events_url,'doctor': doctor})


