"""AppConfig for the `apps.organization` Django app — VYNTIA organizational structure.

Owns the structural entities of a tenant organization:
- Department (departments / org units)
- LocationHistory (employee location/area movement history)
- Company (company-level configuration / branding)

Bounded context boundary: organization defines WHERE work happens (which
department, which physical location). It does not define employees themselves
(that's `apps.employees` in L3.4) nor identity (that's `apps.identity`).
"""

from django.apps import AppConfig


class OrganizationConfig(AppConfig):
    name = "apps.organization"
    label = "organization"
    verbose_name = "VYNTIA Organization"
