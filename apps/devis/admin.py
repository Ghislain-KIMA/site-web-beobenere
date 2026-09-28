from django.contrib import admin
from .models import Devis



@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "service", "timeline", "status", "created_at")
    list_filter = ("status", "timeline", "service")
    readonly_fields = ("created_at",)