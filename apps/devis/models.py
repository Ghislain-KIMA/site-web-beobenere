from django.db import models
from service.models import Service



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

    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, blank=True, null=True, related_name="devis_requests"
    )
    message = models.TextField()
    timeline = models.CharField(max_length=20, choices=TIMELINE_CHOICES, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "devis"
        verbose_name = "Devis"
        verbose_name_plural = "Devis"

    def __str__(self):
        return f"{self.full_name} — {self.get_status_display()}"
