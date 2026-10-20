from django.contrib import admin
from .models import Prescription


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "doctor",
        "diagnosis",
        "prescribed_date",
    )
    search_fields = (
        "patient__username",
        "diagnosis",
    )
    list_filter = ("prescribed_date",)