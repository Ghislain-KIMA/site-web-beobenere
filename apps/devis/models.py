from django.db import models
from service.models import Service
from phonenumber_field.modelfields import PhoneNumberField



class Devis(models.Model):
    STATUS_CHOICES = [
        ("new", "Nouveau"),
        ("contacted", "Contacté"),
        ("converted", "Converti"),
        ("closed", "Clos"),
    ]

    TIMELINE_CHOICES = [
        ("urgent", "Urgent"),
        ("within_month", "Dans le mois"),
        ("not_urgent", "Pas pressé"),
    ]

    full_name = models.CharField(max_length=150, verbose_name="nom complet")
    email = models.EmailField(max_length=150, blank=True, verbose_name="e-mail")
    phone = PhoneNumberField(blank=True, verbose_name="téléphone")
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, blank=True, null=True, related_name="devis_requests", verbose_name="service"
    )
    message = models.TextField(verbose_name="message")
    timeline = models.CharField(max_length=20, choices=TIMELINE_CHOICES, blank=True, verbose_name="délai")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="reçu le")
    notified_at = models.DateTimeField(null=True, blank=True, verbose_name="notifié le")

    class Meta:
        db_table = "devis"
        verbose_name = "Devis"
        verbose_name_plural = "Devis"

    def __str__(self):
        return f"{self.full_name} — {self.get_status_display()}"
