"""Short-lived signed tokens for cross-subdomain workspace exchange.

The flow is:
1. User on app.vyntia.pe selects a workspace → backend issues exchange token (5 min)
2. Frontend redirects to <slug>.vyntia.pe/auth/exchange?token=<exchange_token>
3. <slug>.vyntia.pe consumes the token via POST /api/v1/auth/exchange/ and gets a session JWT

The token is a signed JWT (HMAC-SHA256, same SECRET_KEY) with claims:
- sub: user_id
- tenant_id: target tenant
- token_type: "exchange"
- exp: now + 5 minutes
"""

from datetime import timedelta
from uuid import UUID

import jwt
from django.conf import settings
from django.utils import timezone


EXCHANGE_TOKEN_TTL_SECONDS = 5 * 60  # 5 minutes


class InvalidExchangeToken(Exception):
    """Raised when an exchange token is invalid, expired, or for the wrong tenant."""


def issue_exchange_token(*, user_id: UUID, tenant_id: UUID) -> str:
    """Mint a short-lived exchange token for a (user, tenant) pair."""
    now = timezone.now()
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "token_type": "exchange",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=EXCHANGE_TOKEN_TTL_SECONDS)).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def verify_exchange_token(token: str, *, expected_tenant_id: UUID) -> UUID:
    """Validate an exchange token. Returns the user_id on success.

    Raises InvalidExchangeToken on signature/expiry/tenant mismatch.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise InvalidExchangeToken("Exchange token has expired.")
    except jwt.InvalidTokenError as exc:
        raise InvalidExchangeToken(f"Invalid exchange token: {exc}")

    if payload.get("token_type") != "exchange":
        raise InvalidExchangeToken("Token is not an exchange token.")
    if str(payload.get("tenant_id")) != str(expected_tenant_id):
        raise InvalidExchangeToken("Token tenant_id does not match target workspace.")

    return UUID(payload["sub"])
