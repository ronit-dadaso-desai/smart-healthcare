

from django.shortcuts import render
from clinic_app.models import Doctor


def home(request):
    return render(request, "home.html")


def doctor_list(request):
    doctors = Doctor.objects.filter(available=True)

    return render(
        request,
        "doctors/doctor_list.html",
        {"doctors": doctors}
    )


from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from accounts.models import Appointment
from prescriptions.models import Prescription


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    context = {
        "total_patients": User.objects.filter(
            is_staff=False,
            is_superuser=False
        ).count(),
        "total_doctors": Doctor.objects.count(),
        "total_appointments": Appointment.objects.count(),
        "total_prescriptions": Prescription.objects.count(),
        "recent_appointments": Appointment.objects.select_related(
            "patient", "doctor"
        ).order_by("-created_at")[:5],
    }

    return render(request, "core/admin_dashboard.html", context)
