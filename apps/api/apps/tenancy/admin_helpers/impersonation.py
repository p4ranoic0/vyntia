"""Impersonation helper — issues a session JWT with audit claims."""

from datetime import timedelta

from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.tenancy.context import tenant_context
from apps.tenancy.models import SupportSession


def issue_impersonation_session(*, staff_user, target_user, tenant, reason, ttl_hours=2):
    """Create a SupportSession and mint an impersonation JWT.

    Returns (support_session, access_token_str, refresh_token_str).
    The JWT carries `impersonated_by` and `support_session_id` claims that
    the C.6 frontend uses to render a banner.
    """
    expires_at = timezone.now() + timedelta(hours=ttl_hours)

    session = SupportSession.objects.create(
        staff_user=staff_user,
        target_user=target_user,
        tenant=tenant,
        reason=reason,
        expires_at=expires_at,
    )

    # Issue tokens in the target tenant's context so they have tenant claims
    with tenant_context(tenant):
        refresh = RefreshToken.for_user(target_user)
        refresh["tenant_id"] = str(tenant.id)
        refresh["tenant_slug"] = tenant.slug
        refresh["impersonated_by"] = str(staff_user.id)
        refresh["support_session_id"] = str(session.id)

        access = refresh.access_token
        # Copy impersonation claims onto the access token too (it's what the API uses)
        access["tenant_id"] = str(tenant.id)
        access["tenant_slug"] = tenant.slug
        access["impersonated_by"] = str(staff_user.id)
        access["support_session_id"] = str(session.id)

    return session, str(access), str(refresh)
