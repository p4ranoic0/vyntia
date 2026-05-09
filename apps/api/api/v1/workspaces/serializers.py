from rest_framework import serializers


class WorkspaceSerializer(serializers.Serializer):
    """Compact tenant + role pair for the workspace switcher."""

    tenant_id = serializers.UUIDField()
    slug = serializers.CharField()
    name = serializers.CharField()
    plan = serializers.CharField()
    role = serializers.CharField()
