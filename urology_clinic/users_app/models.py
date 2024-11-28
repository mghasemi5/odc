from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username

class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Patient"

    # Dashboard items for patient
    def get_dashboard_data(self):
        from .models import Appointment  # Avoid circular imports
        return {
            "upcoming_appointments": Appointment.objects.filter(patient=self, date__gte=datetime.today()),
        }
class Doctor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"

    # Dashboard items for doctor
    def get_dashboard_data(self):
        from .models import Timesharing, Devicesharing  # Avoid circular imports
        # Get the current date and time

        return {
            "timesharing_schedule": Timesharing.objects.filter(doctor=self),
            "devicesharing_schedule": Devicesharing.objects.filter(doctor=self, date__gte=datetime.today()),
        }


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)  # Link to Patient
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)  # Link to Doctor
    date = models.DateField()  # Appointment date
    time = models.TimeField()  # Appointment time
    notes = models.TextField(blank=True, null=True)  # Optional notes
    event_id = models.CharField(max_length=256, blank=True, null=True)  # Store Google Calendar event ID


class Timesharing(models.Model):
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)  # Link to Doctor
    date = models.DateField()  # Date the doctor is available
    start_time = models.TimeField()  # Start of availability
    end_time = models.TimeField()  # End of availability
    event_id = models.CharField(max_length=256, blank=True, null=True)  # Store Google Calendar event ID

    def __str__(self):
        # Access the doctor's name via the related CustomUser instance
        return f"{self.doctor.user.username}'s timesharing on {self.date}"




class Device(models.Model):
    name = models.CharField(max_length=100)  # Device name
    description = models.TextField(blank=True, null=True)  # Optional device description

    def __str__(self):
        return self.name

class Devicesharing(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)  # Link to Device
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)  # Link to Doctor
    date = models.DateField()  # Date of use
    start_time = models.TimeField()  # Start time
    end_time = models.TimeField()  # End time
    event_id = models.CharField(max_length=256, blank=True, null=True)  # Store Google Calendar event ID

    def __str__(self):
        return f"{self.device.name} booked by Dr. {self.doctor.user.username} on {self.date}"



