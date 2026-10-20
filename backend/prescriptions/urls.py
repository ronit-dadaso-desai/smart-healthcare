
from django.urls import path
from . import views

app_name = "prescriptions"

urlpatterns = [
    path("my/", views.my_prescriptions, name="my_prescriptions"),
]
