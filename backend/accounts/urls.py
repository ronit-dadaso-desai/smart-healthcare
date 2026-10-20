
from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("book-appointment/", views.book_appointment_view, name="book_appointment"),
    path("my-appointments/", views.my_appointments_view, name="my_appointments"),
    path(
        "cancel-appointment/<int:appointment_id>/",
        views.cancel_appointment_view,
        name="cancel_appointment",
    ),

    # Medical Records
    path(
        "medical-records/",
        views.medical_records_view,
        name="medical_records",
    ),
    path(
        "medical-records/upload/",
        views.upload_medical_record_view,
        name="upload_medical_record",
    ),
    path("medical-records/<int:record_id>/download/", views.download_medical_record_view, name="download_medical_record"),
]
