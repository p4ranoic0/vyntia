"""Serializers for /api/admin/tenants/*."""

from rest_framework import serializers

from apps.tenancy.models import Tenant

RESERVED_SLUGS = {
    "admin", "app", "www", "api", "docs", "status", "blog",
    "mail", "support", "help", "vyntia",
}


class TenantAdminSerializer(serializers.ModelSerializer):
    """Read serializer — full tenant detail for the admin panel."""

    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            "id", "slug", "name", "ruc", "plan", "status",
            "trial_ends_at", "max_users", "cancelled_at",
            "created_at", "updated_at", "member_count",
        ]
        read_only_fields = fields

    def get_member_count(self, obj):
        from apps.tenancy.models import TenantMembership
        return TenantMembership.objects.filter(tenant=obj, status="active").count()


class TenantCreateSerializer(serializers.Serializer):
    """Create serializer — input only. Backed by view that wraps in atomic txn."""

    slug = serializers.SlugField(max_length=63, required=True)
    name = serializers.CharField(max_length=200, required=True)
    ruc = serializers.RegexField(regex=r"^\d{11}$", required=True)
    plan = serializers.ChoiceField(choices=[
        "starter", "pro", "enterprise", "govtech",
    ], required=True)
    trial_days = serializers.IntegerField(min_value=0, max_value=90, default=30)
    admin_email = serializers.EmailField(required=True)
    admin_name = serializers.CharField(max_length=200, required=True)

    def validate_slug(self, value):
        value = value.lower()
        if value in RESERVED_SLUGS:
            raise serializers.ValidationError(f"'{value}' is a reserved subdomain.")
        if Tenant.objects.filter(slug=value).exists():
            raise serializers.ValidationError(f"Slug '{value}' is already in use.")
        return value

    def validate_ruc(self, value):
        if Tenant.objects.filter(
            ruc=value, status__in=["trial", "active"]
        ).exists():
            raise serializers.ValidationError(
                f"RUC {value} is already linked to an active tenant."
            )
        return value


class TenantUpdateSerializer(serializers.ModelSerializer):
    """Patch serializer — only allow editing safe fields."""

    class Meta:
        model = Tenant
        fields = ["plan", "max_users", "trial_ends_at"]
