"""AppConfig for the `apps.identity` Django app — VYNTIA identity & access management.

Owns the User model (custom AUTH_USER_MODEL), Roles, Permissions and the
RBAC junction tables. Also hosts the custom authentication backend.

Bounded context boundary: identity defines WHO can access the system; it does
not define WHAT they can do in business processes (that's per-domain via
service-layer permission checks).
"""

from django.apps import AppConfig


class IdentityConfig(AppConfig):
    name = "apps.identity"
    label = "identity"
    verbose_name = "VYNTIA Identity & Access"
