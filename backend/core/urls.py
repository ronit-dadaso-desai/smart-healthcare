from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("doctors/", views.doctor_list, name="doctor_list"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
]
