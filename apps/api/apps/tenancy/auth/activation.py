"""Helpers for accepting a TenantInvitation and activating a user."""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.tenancy.models import TenantInvitation, TenantMembership


class InvalidInvitationToken(Exception):
    """Raised when an invitation token is invalid, expired, or already accepted."""


@transaction.atomic
def accept_invitation(*, token: str, name: str, password: str):
    """Validate the token and create/link the user + membership.

    Returns the (user, membership) tuple.
    Raises InvalidInvitationToken on any failure.
    """
    User = get_user_model()
    now = timezone.now()

    try:
        invitation = (
            TenantInvitation.objects.select_related("tenant")
            .get(token=token, accepted_at__isnull=True, expires_at__gt=now)
        )
    except TenantInvitation.DoesNotExist:
        raise InvalidInvitationToken("Invitation token is invalid, expired, or already used.")

    user, created = User.objects.get_or_create(
        email__iexact=invitation.email,
        defaults={
            "username": invitation.email.split("@")[0],
            "email": invitation.email,
            "is_active": True,
        },
    )
    if created or not user.has_usable_password():
        user.set_password(password)
    user.save(update_fields=["password"])

    # Create the membership (idempotent — get_or_create avoids dupes if user retries)
    membership, _ = TenantMembership.objects.get_or_create(
        tenant=invitation.tenant,
        user=user,
        defaults={
            "role": invitation.role,
            "status": "active",
            "joined_at": now,
        },
    )
    if membership.status != "active":
        membership.status = "active"
        membership.joined_at = membership.joined_at or now
        membership.save(update_fields=["status", "joined_at"])

    invitation.accepted_at = now
    invitation.save(update_fields=["accepted_at"])

    return user, membership
