from django.contrib import admin
from django.utils import timezone
from django.utils.text import Truncator

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "contact", "short_message", "is_read", "received", "notified")
    list_editable = ("is_read",)
    list_filter = ("is_read",)
    search_fields = ("full_name", "email", "phone", "message")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = ("full_name", "email", "phone", "message", "created_at", "notified_at")
    actions = ["mark_as_read", "mark_as_unread"]

    fieldsets = (
        ("Client", {"fields": ("full_name", ("email", "phone"))}),
        ("Message", {"fields": ("message",)}),
        ("Suivi", {"fields": ("is_read", ("created_at", "notified_at"))}),
    )

    def has_add_permission(self, request):
        """Les messages viennent uniquement du site ; un client qui appelle = un devis."""
        return False

    @admin.display(description="Contact")
    def contact(self, obj):
        """L'e-mail et le téléphone dans une seule colonne."""
        parts = [obj.email, str(obj.phone) if obj.phone else ""]
        return " / ".join(part for part in parts if part) or "—"

    @admin.display(description="Message")
    def short_message(self, obj):
        return Truncator(obj.message).chars(60)

    @admin.display(description="Reçu le", ordering="created_at")
    def received(self, obj):
        return timezone.localtime(obj.created_at).strftime("%d/%m/%y %H:%M")

    @admin.display(boolean=True, description="Notifié")
    def notified(self, obj):
        return obj.notified_at is not None

    @admin.action(description="Marquer comme lu")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Marquer comme non lu")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)