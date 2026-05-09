"""Django admin registrations for tenancy models.

Used by Vyntia staff at /admin/ for emergency operations. The full-featured
provisioning UI lives at admin.vyntia.pe (built in C.7).
"""

from django.contrib import admin

from apps.tenancy.models import (
    SupportSession,
    Tenant,
    TenantInvitation,
    TenantMembership,
)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "ruc", "plan", "status", "created_at")
    list_filter = ("plan", "status")
    search_fields = ("slug", "name", "ruc")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "tenant", "role", "status", "invited_at", "joined_at")
    list_filter = ("role", "status")
    search_fields = ("user__username", "user__email", "tenant__slug", "tenant__name")
    readonly_fields = ("id", "invited_at")
    ordering = ("-invited_at",)


@admin.register(TenantInvitation)
class TenantInvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "tenant", "role", "expires_at", "accepted_at", "created_at")
    list_filter = ("role",)
    search_fields = ("email", "tenant__slug", "tenant__name")
    readonly_fields = ("id", "token", "created_at")
    ordering = ("-created_at",)


@admin.register(SupportSession)
class SupportSessionAdmin(admin.ModelAdmin):
    list_display = (
        "staff_user",
        "target_user",
        "tenant",
        "started_at",
        "expires_at",
        "ended_at",
        "actions_count",
    )
    search_fields = (
        "staff_user__username",
        "target_user__username",
        "tenant__slug",
        "reason",
    )
    readonly_fields = ("id", "started_at", "actions_count")
    ordering = ("-started_at",)
