from django.urls import path, include
from . import views



app_name = "devis"



urlpatterns = [
    path("", views.devis_create, name="create"),
    path("merci/", views.devis_success, name="success"),
]
