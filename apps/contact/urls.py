from django.urls import path
from . import views

app_name = "contact"

urlpatterns = [
    path("", views.contact_page, name="page"),
    path("merci/", views.contact_success, name="success"),
]