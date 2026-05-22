"""access_service — DigitalDocument permission gating + audit logging (B.12).

Implements the maestro § 6.3 "control de acceso granular por tipo de documento"
requirement. Each DigitalDocument carries a numeric `permission_level` (1-9).
A user's effective level is derived from their `nivel_acceso` string (per
`apps.identity.User.NIVEL_ACCESO_CHOICES`):

  total=9 (Acceso Total — RRHH gerencia, sin restricción)
  departamental=5 (Acceso Departamental — jefes pueden ver lo sensible de su área)
  personal=3 (Acceso Personal — default, lo propio + lo no sensible)
  limitado=2 (Acceso Limitado — consulta)
  lectura=1 (Solo Lectura — auditor/invitado)

Access is granted iff effective_level >= required_level. Every check produces
an entry in DocumentAccessLog (action='view' / 'download' / ... / 'denied').
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from apps.documents.models import DocumentAccessLog

if TYPE_CHECKING:  # pragma: no cover
    from apps.documents.models import DigitalDocument
    from apps.identity.models import User


# Maps User.nivel_acceso string → numeric level 1..9.
# MUST stay in sync with User.NIVEL_ACCESO_CHOICES — drift caused the lockout
# bug surfaced by the 2026-05-22 BD-poblada audit (#14 in PM report).
_NIVEL_ACCESO_TO_LEVEL = {
    'total': 9,
    'departamental': 5,
    'personal': 3,
    'limitado': 2,
    'lectura': 1,
}


def user_permission_level(user) -> int:
    """Map a User.nivel_acceso string into a numeric level (0-9)."""
    if user is None or not getattr(user, 'is_authenticated', False):
        return 0
    nivel = getattr(user, 'nivel_acceso', '') or ''
    return _NIVEL_ACCESO_TO_LEVEL.get(nivel, 1)


def can_access(user, document) -> bool:
    """Return True iff user's effective permission level >= document's required level."""
    return user_permission_level(user) >= int(document.permission_level or 0)


def log_access(
    *,
    document,
    user,
    action: str = 'view',
    ip: str = '',
    user_agent: str = '',
    notes: str = '',
) -> DocumentAccessLog:
    """Persist a DocumentAccessLog entry."""
    tenant = getattr(document, 'tenant', None)
    return DocumentAccessLog.objects.create(
        tenant=tenant,
        document=document,
        user=user if getattr(user, 'is_authenticated', False) else None,
        action=action,
        ip=ip or None,
        user_agent=user_agent[:400],
        required_permission_level=int(document.permission_level or 0),
        user_permission_level=user_permission_level(user),
        notes=notes[:300],
    )


def check_and_log(
    *,
    document,
    user,
    action: str = 'view',
    ip: str = '',
    user_agent: str = '',
) -> bool:
    """Check permission, log either 'denied' or the requested action."""
    allowed = can_access(user, document)
    log_action = action if allowed else 'denied'
    log_access(
        document=document, user=user, action=log_action,
        ip=ip, user_agent=user_agent,
        notes='' if allowed else 'insufficient_permission',
    )
    return allowed
