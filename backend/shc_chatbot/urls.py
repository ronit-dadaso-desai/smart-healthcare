from django.urls import path
from . import views

app_name = "shc_chatbot"

urlpatterns = [
    path("", views.health_assistant_view, name="assistant"),
]
