from django.urls import path
from . import views



app_name = "service"



urlpatterns = [
    path("", views.service_list, name="list"),
]