from django.contrib import admin
from django.utils import timezone

from .models import Devis


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    list_display = ("full_name", "contact", "service", "status", "received", "notified")
    list_editable = ("status",)
    list_filter = ("status", "timeline", "service")
    search_fields = ("full_name", "email", "phone", "message")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "notified_at")

    @admin.display(description="Contact")
    def contact(self, obj):
        """L'e-mail et le téléphone dans une seule colonne."""
        parts = [obj.email, str(obj.phone) if obj.phone else ""]
        return " / ".join(part for part in parts if part) or "—"

    @admin.display(boolean=True, description="Notifié")
    def notified(self, obj):
        return obj.notified_at is not None

    @admin.display(description="Reçu le", ordering="created_at")
    def received(self, obj):
        return timezone.localtime(obj.created_at).strftime("%d/%m/%y %H:%M")
