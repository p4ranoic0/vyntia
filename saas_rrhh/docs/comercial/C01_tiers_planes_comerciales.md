# C01. Tiers y Planes Comerciales

> Estructura comercial en 4 tiers que permite **negociación modular** (vender por módulos) sin fragmentar la experiencia de producto. Cada módulo es una unidad facturable independiente pero algunos módulos requieren otros como prerequisito funcional.

---

## 1. Filosofía comercial

Tres principios guían el pricing:

1. **Empezar en el dolor más fuerte**: Planilla correcta y cumplimiento normativo. Es el trabajo que el cliente YA paga hacer, y que si falla genera multas. Ese es el Core.
2. **Upsell por modularidad**: el cliente entra con Planilla y se suscribe a más módulos conforme madura su proceso de RRHH.
3. **Tier por complejidad operativa**, no por cantidad de empleados. Una empresa de 80 empleados con operaciones en 4 sedes y 3 regímenes laborales paga más que una de 300 empleados con un solo régimen simple.

---

## 2. Los 4 tiers

| Tier | Empleados aprox | Regímenes | Módulos incluidos | Soporte |
|---|---|---|---|---|
| **Starter** | 1-50 | 1 (728 o MYPE) | 01, 02, 03 (básico), 04 (core planilla), 08, 10 | Email L1, 48h |
| **Pro** | 50-500 | Hasta 3 | Starter + 03 (full), 04 (full), 05, 06, 08 (full), 09, 10, 11 | Email + chat, 24h |
| **Enterprise** | 500+ | Todos | Pro + 07 (full), 12, integraciones iPaaS, API full, webhooks, single sign-on | Chat + phone, 8h SLA |
| **GovTech** | Entidades públicas | 276, CAS, 30057 | Enterprise + módulo SERVIR 23 procesos + residencia datos Perú + DB dedicada | Phone + CSM dedicado, 4h |

---

## 3. Mapa de módulos por tier

| # | Módulo | Starter | Pro | Enterprise | GovTech |
|---|---|:---:|:---:|:---:|:---:|
| 01 | Planificación de políticas de RRHH | ✓ básico | ✓ | ✓ | ✓ |
| 02 | Organización del trabajo (puestos, CCF) | ✓ básico | ✓ | ✓ | ✓ |
| 03 | Gestión del empleo (selección, vinculación, legajos, desvinculación) | ✓ limitado | ✓ | ✓ | ✓ |
| 04 | Gestión de la compensación (planilla + AFP/ONP/EsSalud/PLAME) | ✓ | ✓ | ✓ | ✓ |
| 05 | Gestión del desarrollo y capacitación (LMS) | ✗ | ✓ | ✓ | ✓ |
| 06 | Gestión del rendimiento (evaluaciones, OKRs) | ✗ | ✓ | ✓ | ✓ |
| 07 | Relaciones humanas y sociales (SST, bienestar, cultura/clima) | ✗ | ✓ parcial | ✓ | ✓ |
| 08 | Control de asistencia y tiempo | ✓ | ✓ | ✓ | ✓ |
| 09 | Procedimiento disciplinario (PID/PAD) | ✗ | ✓ | ✓ | ✓ |
| 10 | Autoservicio / portal del empleado | ✓ | ✓ | ✓ | ✓ |
| 11 | ATS reclutamiento | ✗ | ✓ | ✓ | ✓ |
| 12 | People Analytics + BI | ✗ | ✗ | ✓ | ✓ |

### Marcas de ámbito

- `✓ básico`: funcionalidad reducida, sin personalización avanzada.
- `✓ limitado`: núcleo funcional, 1 workflow por proceso, límites de volumen.
- `✓`: funcional completo.
- `✓ parcial`: algunos submódulos sí, otros requieren upgrade.
- `✓ completo`: el mayor alcance disponible.

---

## 4. Pricing sugerido (referencial Perú)

### 4.1 Starter

- **Setup**: S/ 0 (onboarding automatizado 15 días).
- **Por empleado/mes**: S/ 8-12.
- **Mínimo mensual**: S/ 199.
- **Límites**:
  - 1 empresa, 2 sedes máx.
  - 50 empleados activos (si excede, upgrade automático a Pro).
  - 5 workflows custom.
  - 10 campos custom por DocType.
  - 3 exportaciones PLAME/mes.

### 4.2 Pro

- **Setup**: S/ 2,500-5,000 (onboarding guiado 30 días + migración básica).
- **Por empleado/mes**: S/ 15-22.
- **Mínimo mensual**: S/ 1,500.
- **Límites**:
  - Hasta 5 empresas del grupo, 10 sedes.
  - 500 empleados activos.
  - Workflows ilimitados.
  - 30 campos custom por DocType.
  - Exportaciones PLAME ilimitadas.
  - API REST público (rate limit 300/min).

### 4.3 Enterprise

- **Setup**: S/ 15,000-50,000 (onboarding con consultor dedicado 60-90 días + migración completa).
- **Por empleado/mes**: S/ 25-40 (escalonado inverso: más empleados = menor tarifa).
- **Mínimo mensual**: S/ 8,000.
- **Límites**:
  - Empresas y sedes ilimitadas.
  - Custom DocTypes.
  - SSO (SAML 2.0, Azure AD, Okta).
  - Webhooks outbound ilimitados.
  - API GraphQL.
  - Conector SBS automático para tasas AFP.

### 4.4 GovTech

- **Setup**: S/ 40,000-150,000 (onboarding con consultor legal + consultor técnico; adaptación a 23 procesos SERVIR).
- **Por empleado/mes**: S/ 18-30.
- **Mínimo mensual**: S/ 12,000.
- **Incluye**:
  - DB dedicada (no pooled multi-tenant) con residencia datos Perú.
  - Backups cada 6h + cold storage 5 años.
  - Conector AIRHSP SERVIR.
  - Soporte integral al régimen 276, CAS, Ley 30057.
  - Tribunal Servicio Civil (rol acceso especial).
  - Auditoría externa anual SGSI ISO 27001.
  - CSM dedicado con reuniones mensuales.

---

## 5. Módulos comprables por separado (add-ons)

Fuera del paquete base, se ofrecen como add-ons individuales:

| Add-on | Tier desde | Precio mensual |
|---|---|---|
| Firma electrónica integrada (Llama/Digiflow) | Starter | S/ 200 + S/ 0.80 por documento firmado |
| App móvil white-label | Pro | S/ 1,500/mes |
| Módulo minería (SCTR, bonif. altura/subsuelo) | Pro | +20% base |
| Módulo construcción civil (jornales, BUC, CONAFOVICER) | Pro | +20% base |
| Módulo agroindustrial (Ley 31110 dos sistemas) | Pro | +15% base |
| Canal de denuncias con cadena de custodia legal | Pro | S/ 800/mes |
| People Analytics con IA predictiva | Enterprise | S/ 3,000/mes |
| Integración iPaaS (Flexspring/Zapier) | Enterprise | S/ 1,200/mes |
| Biometría facial con liveness (ZKTeco integrado) | Pro | S/ 500/mes + hardware |
| SDK white-label para integrador | Enterprise | Negociar |

---

## 6. Negociación comercial — flexibilidad típica

El equipo de ventas puede flexibilizar en estos rangos sin escalar:

| Palanca | Flexibilidad | Límite |
|---|---|---|
| Descuento por pago anual adelantado | 10-20% | 20% |
| Descuento por contrato 2-3 años | 10-15% adicional | 15% |
| Waiver de setup fee | Total o parcial | Solo con compromiso 24 meses |
| Grace period de onboarding | Hasta 90 días sin cobro | Starter/Pro |
| Capacitación adicional | Créditos de horas | Pro+ |

Escalamiento a gerencia comercial si:
- Descuento total > 30%.
- Request de módulo fuera del tier contratado sin upgrade.
- SLA custom que afecte SRE.
- Residencia datos fuera de Perú (solo GovTech no aplica).

---

## 7. Trial y freemium

- **Trial Starter**: 30 días gratis, hasta 20 empleados, sin tarjeta.
- **Freemium**: NO se ofrece freemium permanente. El costo operativo por tenant (infra, soporte, compliance) no lo sustenta.
- **Plan educacional**: 50% descuento para universidades/institutos con <200 empleados.
- **Plan ONG**: 30% descuento para ONGs acreditadas.

---

## 8. Ciclo de vida del cliente y expansion

**Patrón ideal**:
1. Cliente entra en Starter con planilla + asistencia (dolor inmediato).
2. A los 3-6 meses añade módulo de selección (11) y autoservicio (10 full).
3. Al año upgrade a Pro cuando supera 50 empleados o necesita evaluaciones.
4. Año 2-3: agrega analytics y People Analytics.
5. Clientes corporativos maduran a Enterprise.

**Métricas clave**:
- Net Revenue Retention (NRR) > 110% objetivo.
- Logo churn < 5% anual.
- Revenue churn < 3% anual.
- Time to first value (TTFV): < 15 días en Starter, < 45 días en Pro.

---

## 9. Proceso de Onboarding por tier (resumen)

| Etapa | Starter | Pro | Enterprise | GovTech |
|---|---|---|---|---|
| Kickoff | Video-tutorial | Sesión 1h remota | Reunión on-site/remota | Reunión on-site |
| Configuración inicial | Self-service + checklist | Consultor remoto 15h | Consultor dedicado 60-120h | Consultor + legal 120-200h |
| Migración de data | CSV templates | CSV + validación asistida | ETL personalizado | ETL + adaptación a AIRHSP |
| Paralelo con sistema actual | 1 mes sugerido | 2 meses | 3 meses | 3-6 meses |
| Go-live | 15 días | 30-45 días | 60-90 días | 90-180 días |
| Soporte post-golive | Email 90 días | Consultor 90 días | CSM 180 días | CSM permanente |

---

## 10. Checklist comercial

- [ ] Cotizador automatizado por web con los 4 tiers
- [ ] Módulos sectoriales (minería, construcción, agro) claramente diferenciados
- [ ] Contratos tipo por tier + adenda modular
- [ ] Procesos de upgrade/downgrade documentados sin pérdida de data
- [ ] Billing integrado con Izipay/Culqi/Mercado Pago (tarjetas locales)
- [ ] Facturación electrónica vía proveedor autorizado SUNAT
- [ ] Formularios de baja con retención de data según prescripción (5 años mínimo)
- [ ] Playbooks del equipo comercial con casos típicos peruanos
