from django.db import models
from phonenumber_field.modelfields import PhoneNumberField



class Company(models.Model):
    name = models.CharField(max_length=150)
    slogan = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    sector = models.CharField(max_length=100, blank=True)
    logo_url = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=150, unique=True, blank=True, null=True)
    phone = PhoneNumberField(unique=True)
    address = models.TextField(blank=True)
    whatsapp = PhoneNumberField(blank=True)
    facebook_url = models.URLField(max_length=255, blank=True)
    business_hours = models.CharField(max_length=255, blank=True)
    service_area = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "company"
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name
