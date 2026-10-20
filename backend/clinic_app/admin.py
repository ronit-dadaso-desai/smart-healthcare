
from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "specialization",
        "qualification",
        "experience_years",
        "consultation_fee",
        "clinic_name",
        "available",
    )

    list_filter = ("specialization", "available")

    search_fields = (
        "name",
        "specialization",
        "qualification",
        "clinic_name",
        "clinic_address",
    )

    fields = (
        "name",
        "specialization",
        "qualification",
        "experience_years",
        "consultation_fee",
        "phone",
        "email",
        "clinic_name",
        "clinic_address",
        "photo",
        "available",
        "about",
    )
