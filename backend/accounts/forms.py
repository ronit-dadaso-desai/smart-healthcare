
from django import forms
from .models import Appointment
from clinic_app.models import Doctor


class AppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(available=True),
        empty_label="Select a doctor",
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label="Doctor"
    )

    class Meta:
        model = Appointment
        fields = [
            'doctor',
            'appointment_date',
            'appointment_time',
            'reason',
        ]

        widgets = {
            'appointment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'appointment_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your reason'
            }),
        }

    def save(self, commit=True):
        appointment = super().save(commit=False)
        doctor = self.cleaned_data['doctor']

        appointment.doctor = doctor
        appointment.doctor_name = doctor.name

        if commit:
            appointment.save()

        return appointment

    
    def clean(self):
        cleaned_data = super().clean()

        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')

        if doctor and appointment_date and appointment_time:
            existing_appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
            ).exclude(status='Cancelled')

            if self.instance.pk:
                existing_appointments = existing_appointments.exclude(
                    pk=self.instance.pk
                )

            if existing_appointments.exists():
                raise forms.ValidationError(
                    "This doctor already has an appointment "
                    "at the selected date and time. "
                    "Please choose another time."
                )

        return cleaned_data

