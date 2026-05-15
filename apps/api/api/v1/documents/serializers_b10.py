"""Serializers for B.10 documents — DocumentSignature + HiringDocumentBundle."""
from rest_framework import serializers

from apps.documents.models import (
    DocumentSignature,
    HiringBundleItem,
    HiringDocumentBundle,
)


# ----------------------------- DocumentSignature -------------------------------

class DocumentSignatureSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    kind_display = serializers.CharField(
        source='get_kind_display', read_only=True,
    )

    class Meta:
        model = DocumentSignature
        fields = [
            'id', 'tenant',
            'document', 'signer_user',
            'signer_name', 'signer_doc_number', 'signer_email',
            'kind', 'kind_display',
            'status', 'status_display',
            'canvas_base64', 'typed_name', 'checkbox_text',
            'requested_at', 'expires_at', 'signed_at',
            'rejection_reason',
            'signer_ip', 'signer_user_agent',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'status_display', 'kind_display',
            'canvas_base64', 'typed_name', 'checkbox_text',
            'signed_at', 'rejection_reason',
            'signer_ip', 'signer_user_agent',
            'requested_at', 'updated_at',
        ]


class CaptureSignatureInputSerializer(serializers.Serializer):
    canvas_base64 = serializers.CharField(required=False, allow_blank=True, default='')
    typed_name = serializers.CharField(required=False, allow_blank=True, default='')
    checkbox_text = serializers.CharField(required=False, allow_blank=True, default='')


class RejectSignatureInputSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, allow_blank=False)


# ----------------------------- HiringDocumentBundle ----------------------------

class HiringBundleItemSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(
        source='get_kind_display', read_only=True,
    )

    class Meta:
        model = HiringBundleItem
        fields = [
            'id', 'bundle', 'kind', 'kind_display',
            'document', 'signature', 'required', 'order',
        ]
        read_only_fields = ['id', 'kind_display']


class HiringDocumentBundleSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    items = HiringBundleItemSerializer(many=True, read_only=True)
    item_kinds = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True,
        help_text='List of HiringBundleItem.kind values to scaffold on create',
    )

    class Meta:
        model = HiringDocumentBundle
        fields = [
            'id', 'tenant',
            'employee', 'contract',
            'title', 'status', 'status_display',
            'sent_at', 'acknowledged_at',
            'created_by', 'created_at', 'updated_at',
            'items', 'item_kinds',
        ]
        read_only_fields = [
            'id', 'status', 'status_display',
            'sent_at', 'acknowledged_at',
            'created_by', 'created_at', 'updated_at',
        ]


class AttachDocumentInputSerializer(serializers.Serializer):
    document_id = serializers.UUIDField(required=True)


class AttachAcuseInputSerializer(serializers.Serializer):
    signature_id = serializers.UUIDField(required=True)
