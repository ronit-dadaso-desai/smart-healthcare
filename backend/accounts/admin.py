

from django.contrib import admin
from .models import Appointment, MedicalRecord


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "patient",
        "doctor_name",
        "appointment_date",
        "appointment_time",
        "status",
        "created_at",
    )

    list_filter = ("status", "appointment_date")
    search_fields = ("patient__username", "doctor_name")


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "patient",
        "record_type",
        "report_date",
        "created_at",
    )

    list_filter = ("record_type", "report_date")
    search_fields = ("title", "patient__username")
    date_hierarchy = "report_date"


