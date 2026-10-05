from django.db import models
from phonenumber_field.modelfields import PhoneNumberField



class ContactMessage(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, blank=True)
    phone = PhoneNumberField(blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "contact_message"
        ordering = ["-created_at"]
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"

    def __str__(self):
        return f"{self.full_name} — {self.created_at:%d/%m/%Y}"
