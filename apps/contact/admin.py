from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "is_read", "created_at")
    list_filter = ("is_read",)
    readonly_fields = ("created_at",)
    actions = ["mark_as_read"]

    @admin.action(description="Marquer comme lu")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
