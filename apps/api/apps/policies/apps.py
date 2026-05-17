"""AppConfig for the `apps.policies` Django app — VYNTIA Module 01 governance.

Owns the policy / governance domain:
- Policy (header): RIT, Código de Ética, Reglamento SST, Política de Datos,
  Manual de Funciones, Procedimientos, etc.
- PolicyVersion (immutable versioned content with PDF attachment).
- PolicyApprovalFlow + PolicyApprovalStep (multi-step approval workflow).
- PolicyPublication (org-wide release with target audience scoping).
- PolicyAcknowledgment (per-employee acuse with audit trail per Ley 29733).

Bounded context boundary: policies own governance documents and their
publication/acknowledgment lifecycle. Storage uses `apps.core.storage.TenantStorage`
(ADR-B.4). E-signature integration with `documents.DocumentSignature` is
caller-elected — the policy manager has its own canvas/typed/checkbox capture.

B.15b will extend this app with HRStrategicPlan, WorkforcePlan, and
ComplianceMatrix entities (Module 01 § 2-4).
"""

from django.apps import AppConfig


class PoliciesConfig(AppConfig):
    name = "apps.policies"
    label = "policies"
    verbose_name = "VYNTIA Policies"
