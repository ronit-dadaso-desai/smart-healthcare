
from django.db import models


class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ("General Physician", "General Physician"),
        ("Cardiologist", "Cardiologist"),
        ("Dermatologist", "Dermatologist"),
        ("Neurologist", "Neurologist"),
        ("Orthopedic", "Orthopedic"),
        ("Pediatrician", "Pediatrician"),
        ("Gynecologist", "Gynecologist"),
        ("Dentist", "Dentist"),
    ]

    name = models.CharField(max_length=100)
    specialization = models.CharField(
        max_length=100,
        choices=SPECIALIZATION_CHOICES
    )
    qualification = models.CharField(max_length=150)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    clinic_name = models.CharField(max_length=150, blank=True)
    clinic_address = models.TextField(blank=True)
    photo = models.ImageField(
    upload_to="doctors/",
    blank=True,
    null=True
    )
    available = models.BooleanField(default=True)
    about = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"
