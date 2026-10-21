from pathlib import Path

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404

from .models import Appointment, MedicalRecord
from .forms import AppointmentForm


# Registration
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            messages.error(request, "Please fill in all required fields.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            messages.success(request, "Registration successful. Please log in.")
            return redirect("login")

    return render(request, "accounts/register.html")


# Login
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


# Logout
@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")

    return redirect("dashboard")


# Dashboard
@login_required
def dashboard_view(request):
    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by("-appointment_date")

    records = MedicalRecord.objects.filter(
        patient=request.user
    ).order_by("-report_date", "-created_at")

    return render(
        request,
        "accounts/dashboard.html",
        {
            "appointments": appointments,
            "records": records,
        },
    )


# Book appointment
@login_required
def book_appointment_view(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)

        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()

            messages.success(request, "Appointment booked successfully!")
            return redirect("my_appointments")
    else:
        form = AppointmentForm()

    return render(
        request,
        "accounts/book_appointment.html",
        {"form": form},
    )


# My appointments
@login_required
def my_appointments_view(request):
    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by("-appointment_date", "-appointment_time")

    return render(
        request,
        "accounts/my_appointments.html",
        {"appointments": appointments},
    )


# Cancel appointment
@login_required
def cancel_appointment_view(request, appointment_id):
    if request.method != "POST":
        return redirect("my_appointments")

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=request.user,
    )

    appointment.status = "Cancelled"
    appointment.save(update_fields=["status"])

    messages.success(request, "Appointment cancelled successfully.")
    return redirect("my_appointments")


# Medical record form
class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = [
            "title",
            "record_type",
            "report_date",
            "description",
            "file",
        ]
        widgets = {
            "report_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "description": forms.Textarea(
                attrs={"rows": 3}
            ),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")

        if uploaded_file:
            allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png"}
            extension = Path(uploaded_file.name).suffix.lower()

            if extension not in allowed_extensions:
                raise forms.ValidationError(
                    "Only PDF, JPG, JPEG, and PNG files are allowed."
                )

            if uploaded_file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "File size must not exceed 5 MB."
                )

        return uploaded_file


# View medical records
@login_required
def medical_records_view(request):
    records = MedicalRecord.objects.filter(
        patient=request.user
    ).order_by("-report_date", "-created_at")

    return render(
        request,
        "accounts/medical_records.html",
        {"records": records},
    )


# Upload medical record
@login_required
def upload_medical_record_view(request):
    if request.method == "POST":
        form = MedicalRecordForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            record = form.save(commit=False)
            record.patient = request.user
            record.save()

            messages.success(
                request,
                "Medical record uploaded successfully!",
            )
            return redirect("medical_records")
    else:
        form = MedicalRecordForm()

    return render(
        request,
        "accounts/upload_medical_record.html",
        {"form": form},
    )


# Download medical record
@login_required
def download_medical_record_view(request, record_id):
    record = get_object_or_404(
        MedicalRecord,
        id=record_id,
        patient=request.user,
    )

    if not record.file:
        raise Http404("File not found.")

    try:
        file_handle = record.file.open("rb")
    except (FileNotFoundError, OSError):
        raise Http404("File not found.")

    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=Path(record.file.name).name,
    )

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        user_obj = User.objects.filter(email__iexact=email).first()

        user = None
        if user_obj:
            user = authenticate(
                request,
                username=user_obj.username,
                password=password,
            )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid email or password.")

    return render(request, "accounts/login.html")
