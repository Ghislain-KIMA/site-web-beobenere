from django.db import models
from phonenumber_field.modelfields import PhoneNumberField



class ContactMessage(models.Model):
    full_name = models.CharField(max_length=150, verbose_name="nom complet")
    email = models.EmailField(max_length=150, blank=True, verbose_name="e-mail")
    phone = PhoneNumberField(blank=True, verbose_name="téléphone")
    message = models.TextField(verbose_name="message")
    is_read = models.BooleanField(default=False, verbose_name="lu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="reçu le")
    notified_at = models.DateTimeField(null=True, blank=True, verbose_name="notifié le")

    class Meta:
        db_table = "contact_message"
        ordering = ["-created_at"]
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"

    def __str__(self):
        return f"{self.full_name} — {self.created_at:%d/%m/%Y}"
