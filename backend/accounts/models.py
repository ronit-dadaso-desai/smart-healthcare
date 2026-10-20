
from django.db import models
from django.contrib.auth.models import User
from clinic_app.models import Doctor


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Cancelled", "Cancelled"),
        ("Completed", "Completed"),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
    )
    doctor_name = models.CharField(max_length=100)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
    )
    doctor = models.ForeignKey(
    Doctor,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="appointments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} - {self.doctor_name} - {self.appointment_date}"

class MedicalRecord(models.Model):
    RECORD_TYPES = [
        ("Blood Test", "Blood Test"),
        ("X-Ray", "X-Ray"),
        ("MRI", "MRI"),
        ("Prescription", "Prescription"),
        ("Other", "Other"),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="medical_records",
    )
    title = models.CharField(max_length=200)
    record_type = models.CharField(
        max_length=30,
        choices=RECORD_TYPES,
        default="Other",
    )
    report_date = models.DateField()
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="medical_records/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.patient.username}"

