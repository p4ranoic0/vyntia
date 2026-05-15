"""Serializers for B.12 documents — DigitalDossier + DossierSection + DocumentAccessLog."""
from rest_framework import serializers

from apps.documents.models import (
    DigitalDossier,
    DocumentAccessLog,
    DossierSection,
)


class DossierSectionSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)

    class Meta:
        model = DossierSection
        fields = [
            'id', 'dossier', 'kind', 'kind_display', 'label',
            'permission_level', 'order', 'notes',
        ]
        read_only_fields = ['id', 'kind_display']


class DigitalDossierSerializer(serializers.ModelSerializer):
    sections = DossierSectionSerializer(many=True, read_only=True)

    class Meta:
        model = DigitalDossier
        fields = [
            'id', 'tenant', 'employee',
            'is_closed', 'closed_at', 'retention_until',
            'created_at', 'updated_at',
            'sections',
        ]
        read_only_fields = [
            'id', 'is_closed', 'closed_at', 'retention_until',
            'created_at', 'updated_at', 'sections',
        ]


class DocumentAccessLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = DocumentAccessLog
        fields = [
            'id', 'tenant', 'document', 'user',
            'action', 'action_display',
            'ip', 'user_agent',
            'required_permission_level', 'user_permission_level',
            'notes', 'occurred_at',
        ]
        read_only_fields = [
            'id', 'action_display', 'occurred_at',
            'required_permission_level', 'user_permission_level',
        ]
