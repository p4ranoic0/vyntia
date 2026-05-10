"""Read-only admin for AuditEvent — operators inspect via Django admin only."""

from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "action",
        "target_model",
        "target_id",
        "actor_user",
        "tenant",
    )
    list_filter = ("action", "target_model", "tenant")
    search_fields = ("action", "target_model", "target_id")
    date_hierarchy = "created_at"
    readonly_fields = (
        "id",
        "tenant",
        "actor_user",
        "action",
        "target_model",
        "target_id",
        "payload_json",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
