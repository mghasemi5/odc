from datetime import datetime, timedelta
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, Patient, Doctor, Devicesharing, Timesharing, Appointment

class PatientSignupForm(UserCreationForm):
    phone = forms.CharField(max_length=15)
    age = forms.IntegerField(max_value=100)
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','age','username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        if commit:
            user.save()
            Patient.objects.create(user=user, phone=self.cleaned_data['phone'])
        return user
class DoctorSignupForm(UserCreationForm):
    specialization = forms.CharField(max_length=100)

    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'doctor'
        if commit:
            user.save()
            Doctor.objects.create(user=user, specialization=self.cleaned_data['specialization'])
        return user
class TimesharingForm(forms.ModelForm):
    class Meta:
        model = Timesharing
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time >= end_time:
            raise forms.ValidationError('Start time must be earlier than end time.')

        # Check for overlaps with existing bookings (by any doctor)
        if Timesharing.objects.filter(
            date=date,
            start_time__lt=end_time,  # End time of existing booking is after requested start time
            end_time__gt=start_time   # Start time of existing booking is before requested end time
        ).exists():
            raise forms.ValidationError('The selected time slot is already booked by another doctor.')

        return cleaned_data
class DevicesharingForm(forms.ModelForm):
    class Meta:
        model = Devicesharing
        fields = ['device', 'date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        device = cleaned_data.get('device')
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time >= end_time:
            raise forms.ValidationError('Start time must be earlier than end time.')

        # Check for overlaps with existing bookings for the same device
        if Devicesharing.objects.filter(
            device=device,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists():
            raise forms.ValidationError(f'The selected device is already booked during this time.')

        return cleaned_data
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generate 15-minute intervals for the time field
        time_choices = [
            (f"{hour:02}:{minute:02}", f"{hour:02}:{minute:02}")
            for hour in range(0, 24)
            for minute in range(0, 60, 15)
        ]
        self.fields['time'] = forms.ChoiceField(choices=time_choices)

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        # Convert `time` to `datetime.time` if it is a string
        if isinstance(time, str):
            time = datetime.strptime(time, "%H:%M").time()

        # Ensure the doctor has timesharing booked for the selected time
        end_time = (datetime.combine(date, time) + timedelta(minutes=15)).time()  # Calculate end time
        if not Timesharing.objects.filter(
            doctor=doctor,
            date=date,
            start_time__lte=time,
            end_time__gte=end_time
        ).exists():
            raise ValidationError("The doctor is not available for this time slot.")

        # Ensure the selected time slot is not already booked for the doctor
        if Appointment.objects.filter(doctor=doctor, date=date, time=time).exists():
            raise ValidationError("The selected time slot is already booked.")

        return cleaned_data
class EditPatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['phone', 'address', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
class EditDoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialization', 'bio']
class EditTimesharingForm(forms.ModelForm):
    class Meta:
        model = Timesharing
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time >= end_time:
            raise forms.ValidationError('Start time must be earlier than end time.')

        # Exclude the current instance from overlap checks
        current_instance_id = self.instance.id

        # Check for overlaps with existing bookings (by any doctor, excluding the current instance)
        if Timesharing.objects.filter(
                date=date,
                start_time__lt=end_time,  # End time of existing booking is after requested start time
                end_time__gt=start_time  # Start time of existing booking is before requested end time
        ).exclude(id=current_instance_id).exists():
            raise forms.ValidationError('The selected time slot is already booked by another doctor.')

        return cleaned_data
class EditDevicesharingForm(forms.ModelForm):
    class Meta:
        model = Devicesharing
        fields = ['device', 'date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time >= end_time:
            raise forms.ValidationError('Start time must be earlier than end time.')

        # Exclude the current instance from overlap checks
        current_instance_id = self.instance.id

        # Check for overlaps with existing bookings (by any doctor, excluding the current instance)
        if Timesharing.objects.filter(
                date=date,
                start_time__lt=end_time,  # End time of existing booking is after requested start time
                end_time__gt=start_time  # Start time of existing booking is before requested end time
        ).exclude(id=current_instance_id).exists():
            raise forms.ValidationError('The selected time slot is already booked by another doctor.')

        return cleaned_data
class EditAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generate 15-minute intervals for the time field
        time_choices = [
            (f"{hour:02}:{minute:02}", f"{hour:02}:{minute:02}")
            for hour in range(0, 24)
            for minute in range(0, 60, 15)
        ]
        self.fields['time'] = forms.ChoiceField(choices=time_choices)

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        # Convert `time` to `datetime.time` if it is a string
        if isinstance(time, str):
            time = datetime.strptime(time, "%H:%M").time()

        # Ensure the doctor has timesharing booked for the selected time
        end_time = (datetime.combine(date, time) + timedelta(minutes=15)).time()  # Calculate end time
        current_instane = self.instance.id
        if not Timesharing.objects.filter(
                doctor=doctor,
                date=date,
                start_time__lte=time,
                end_time__gte=end_time
        ).exists():
            raise ValidationError("The doctor is not available for this time slot.")

        # Ensure the selected time slot is not already booked for the doctor
        if Appointment.objects.filter(doctor=doctor, date=date, time=time).exclude(id=current_instane).exists():
            raise ValidationError("The selected time slot is already booked.")

        return cleaned_data