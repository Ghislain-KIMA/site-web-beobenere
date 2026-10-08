from django.urls import path

from . import views



app_name = 'homepage'
urlpatterns = [
    path("", views.homepage, name='homepage'),
    path("a-propos/", views.about, name="about"),
    path("mentions-legales/", views.legal, name="legal"),
]
