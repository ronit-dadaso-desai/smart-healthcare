from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Prescription


@login_required
def my_prescriptions(request):
    prescriptions = Prescription.objects.filter(
        patient=request.user
    ).select_related(
        "doctor", "appointment"
    ).order_by("-created_at")

    return render(
        request,
        "prescriptions/my_prescriptions.html",
        {"prescriptions": prescriptions}
    )
