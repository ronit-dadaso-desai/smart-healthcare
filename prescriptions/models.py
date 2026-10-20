
from django.db import models
from django.contrib.auth.models import User
from clinic_app.models import Doctor
from accounts.models import Appointment


class Prescription(models.Model):
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        related_name="prescriptions"
    )

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prescriptions"
    )

    diagnosis = models.CharField(max_length=255)
    medicines = models.TextField()
    instructions = models.TextField(blank=True)
    prescribed_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient.username} - {self.diagnosis}"
