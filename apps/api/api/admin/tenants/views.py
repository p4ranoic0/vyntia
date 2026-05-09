"""Admin tenant CRUD views."""

import secrets
from datetime import timedelta

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.admin.permissions import IsVyntiaStaff
from api.admin.tenants.serializers import (
    TenantAdminSerializer,
    TenantCreateSerializer,
    TenantUpdateSerializer,
)
from apps.core.responses import APIResponse
from apps.tenancy.admin_helpers.seed import setup_tenant_seed
from apps.tenancy.models import Tenant, TenantInvitation


class TenantsListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def get(self, request):
        """List all tenants. Pagination via ?page=N&page_size=N (defaults 1, 25)."""
        page = max(int(request.query_params.get("page", 1)), 1)
        page_size = min(max(int(request.query_params.get("page_size", 25)), 1), 100)
        offset = (page - 1) * page_size

        qs = Tenant.objects.all().order_by("-created_at")
        total = qs.count()
        items = qs[offset : offset + page_size]
        return APIResponse.success(
            data={
                "results": TenantAdminSerializer(items, many=True).data,
                "pagination": {
                    "total_items": total,
                    "current_page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size,
                },
            },
        )

    @transaction.atomic
    def post(self, request):
        """Create a new tenant + first invitation + minimal seed."""
        serializer = TenantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        trial_ends_at = timezone.now() + timedelta(days=validated["trial_days"])

        tenant = Tenant.objects.create(
            slug=validated["slug"],
            name=validated["name"],
            ruc=validated["ruc"],
            plan=validated["plan"],
            status="trial",
            trial_ends_at=trial_ends_at,
            created_by=request.user,
        )

        # Seed company config
        setup_tenant_seed(tenant)

        # Create first-admin invitation
        invitation_token = secrets.token_urlsafe(48)
        invitation = TenantInvitation.objects.create(
            tenant=tenant,
            email=validated["admin_email"],
            token=invitation_token,
            role="owner",
            expires_at=timezone.now() + timedelta(days=7),
            created_by=request.user,
        )

        activation_url = (
            f"https://{tenant.slug}.vyntia.pe/activate?token={invitation_token}"
        )

        return APIResponse.success(
            data={
                "tenant": TenantAdminSerializer(tenant).data,
                "invitation": {
                    "id": str(invitation.id),
                    "email": invitation.email,
                    "expires_at": invitation.expires_at.isoformat(),
                    "activation_url": activation_url,
                },
            },
            message="Tenant creado.",
            status_code=http_status.HTTP_201_CREATED,
        )


class TenantDetailView(APIView):
    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def get(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        return APIResponse.success(data=TenantAdminSerializer(tenant).data)

    def patch(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        serializer = TenantUpdateSerializer(tenant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(
            data=TenantAdminSerializer(tenant).data,
            message="Tenant actualizado.",
        )


class TenantSuspendView(APIView):
    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def post(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        if tenant.status == "cancelled":
            return APIResponse.error(message="No se puede suspender un tenant cancelado.", status_code=400)
        tenant.status = "suspended"
        tenant.save(update_fields=["status", "updated_at"])
        return APIResponse.success(
            data=TenantAdminSerializer(tenant).data,
            message="Tenant suspendido.",
        )


class TenantCancelView(APIView):
    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def post(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        tenant.status = "cancelled"
        tenant.cancelled_at = timezone.now()
        tenant.save(update_fields=["status", "cancelled_at", "updated_at"])
        return APIResponse.success(
            data=TenantAdminSerializer(tenant).data,
            message="Tenant cancelado.",
        )


class TenantReinviteView(APIView):
    """Re-issue an invitation if the original one expired or was lost."""

    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def post(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        email = request.data.get("email")
        role = request.data.get("role", "owner")
        if not email:
            return APIResponse.error(message="email is required.", status_code=400)

        token = secrets.token_urlsafe(48)
        invitation = TenantInvitation.objects.create(
            tenant=tenant,
            email=email,
            token=token,
            role=role,
            expires_at=timezone.now() + timedelta(days=7),
            created_by=request.user,
        )
        return APIResponse.success(
            data={
                "id": str(invitation.id),
                "email": invitation.email,
                "expires_at": invitation.expires_at.isoformat(),
                "activation_url": f"https://{tenant.slug}.vyntia.pe/activate?token={token}",
            },
            message="Invitación re-enviada.",
            status_code=http_status.HTTP_201_CREATED,
        )
