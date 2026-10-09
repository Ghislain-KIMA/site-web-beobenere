from django.contrib import admin
from django.utils import timezone

from .models import Devis


# Ce que le client a écrit : verrouillé quand la demande vient du site.
CLIENT_FIELDS = ("full_name", "email", "phone", "service", "timeline", "message", "source", "created_at")

@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    list_display = ("full_name", "contact", "service", "source", "status", "received", "notified")
    list_editable = ("status",)
    list_filter = ("status", "source", "timeline", "service")
    search_fields = ("full_name", "email", "phone", "message")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = ("notified_at",)
    fieldsets = (
        ("Client", {"fields": ("full_name", ("email", "phone"))}),
        ("Demande", {"fields": (("service", "timeline"), "message")}),
        ("Suivi", {"fields": (("status", "source"), ("created_at", "notified_at"))}),
    )

    def get_readonly_fields(self, request, obj=None):
        """Une demande venue du site garde le texte du client tel quel."""
        fields = super().get_readonly_fields(request, obj)
        if obj is not None and obj.source == "site":
            return CLIENT_FIELDS + tuple(fields)
        return fields

    def get_form(self, request, obj=None, **kwargs):
        """Une saisie manuelle ne peut pas se faire passer pour une demande du site."""
        form = super().get_form(request, obj, **kwargs)
        if "source" in form.base_fields:
            field = form.base_fields["source"]
            field.choices = [c for c in field.choices if c[0] != "site"]
            field.initial = "phone"
        return form

    def save_model(self, request, obj, form, change):
        """Pas d'alerte e-mail pour une demande que l'on vient de saisir soi-même."""
        if not change:
            obj.notified_at = timezone.now()
        super().save_model(request, obj, form, change)

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
