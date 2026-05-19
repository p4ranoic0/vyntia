# VYNTIA — Sub-Projects Roadmap

> Source of truth for the post-Foundation build plan. Derived from Foundation Design Spec § 6 (2026-04-25).
> **Sub-projects A (Foundation), C (Multi-tenancy + RLS), and B (Vyntia Core Functional) are complete** — tagged `foundation-complete`, `c-multitenancy-complete`, and `b-vyntia-core-complete`. **Next: D (Vyntia Pay).**
> **Sub-projects E (Extensión Organización) and F (Policies) were absorbed into B** per the B-spec (2026-05-09) — closed when B closed (2026-05-19).

| # | Code | Sub-project | Needs before | Tier unlocked |
|---|------|-------------|--------------|---------------|
| 1 | **A** ✅ | Foundation (rebrand + restructure + cleanup) — *complete 2026-05-07, tag `foundation-complete`* | — | — |
| 2 | **C** ✅ | Multi-tenancy + Row-Level Security — *complete 2026-05-09, tag `c-multitenancy-complete`* | A | Enables SaaS sales |
| 3 | **B** ✅ | Migración funcional Vyntia Core — *complete 2026-05-19, tag `b-vyntia-core-complete`* | A, C | Vyntia Core with tenant |
| 4 | **D** | Vyntia Pay (planilla peruana real — PLAME, T-Registro, AFPnet, CTS, gratificaciones) — **NEXT** | B | **Starter tier** |
| 5 | **N** | Asistencia + turnos | D | Starter + Attendance |
| 6 | **P** | App móvil (React Native) | B | Employee mobile portal |
| 7 | **S** | Billing SaaS (suscripciones, planes) | C | Automated billing |
| 8 | **H** | Vyntia Pulse (gestión rendimiento) | B | **Pro tier** |
| 9 | **G** | Learning + Career | B | Pro tier |
| 10 | **Q** | Vyntia Hire (ATS — reclutamiento) | B | Pro tier |
| 11 | ~~**E**~~ | ~~Extensión Organización (positions, org chart)~~ — *absorbed into B per B-spec 2026-05-09* | B | Core extension |
| 12 | ~~**F**~~ | ~~Policies (gestión políticas SERVIR)~~ — *absorbed into B per B-spec 2026-05-09* | B | GovTech tier |
| 13 | **I** | Labor Relations (relaciones laborales) | B | GovTech tier |
| 14 | **J** | Safety (seguridad y salud) | B | GovTech tier |
| 15 | **K** | Welfare (bienestar) | B | GovTech tier |
| 16 | **L** | Engagement (clima organizacional) | B | GovTech tier |
| 17 | **M** | Communications (comunicaciones internas) | B | GovTech tier |
| 18 | **O** | Discipline (procedimiento disciplinario) | B | GovTech tier |
| 19 | **R** | Vyntia Insights (People Analytics) | B + real data | **Enterprise tier** |
| 20 | **T** | Workflow Engine (motor declarativo) | B | Platform maturity |
| 21 | **U** | DocType Engine (metadata-driven forms) | B | Platform maturity |
| 22 | **V** | Permissions v2 (RBAC + permlevel 0-9 + ABAC) | C | Platform maturity |
| 23 | **W** | Notifications (email, push, in-app) | B | Platform maturity |
| 24 | **X** | Audit Log (transversal audit trail) | B | Platform maturity |

## Commercial brand mapping

| VYNTIA module | Sub-projects | Django apps |
|---|---|---|
| **Vyntia Core** | A, B, C, E, F | identity, organization, employees, contracts, documents, onboarding |
| **Vyntia Pay** | D, N | payroll, time_off, attendance, regional_pe |
| **Vyntia People** | G, H, I-M | learning, career, performance, labor_relations, welfare, engagement, communications |
| **Vyntia Hire** | Q | recruitment |
| **Vyntia Insights** | R | analytics |
| **Vyntia Safety** | J | safety |

## Architecture rules (enforced across all sub-projects)

1. **FK cross-app ONLY via string lazy**: `ForeignKey('employees.Employee', ...)` — never import from another app.
2. **Cross-app logic via service public API**: `from apps.employees.services import get_employee_data`.
3. **`core` has zero domain app dependencies** — pure utility only.
4. **New Django apps only when real code exists** (no speculative empty apps).
5. **English for code; Spanish for UI strings** (i18n in sub-project Z).
6. **Peruvian legal terms preserved**: DNI, RUC, CTS, PLAME, SUNAT, T-Registro, AFP, ONP, ESSALUD.
