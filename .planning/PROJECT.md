# Sistema de Gestión de RRHH — Intranet

## What This Is

Sistema web integral de Recursos Humanos para gestión del ciclo completo del servidor: desde el onboarding hasta la desvinculación. Incluye legajo digital, remuneraciones, vacaciones, contratos, certificados y reportes para sistemas externos (AFP Net, PDT-PLAME). Monorepo Django 4.2 + DRF (backend) + React 18 + TypeScript + Vite (frontend).

## Core Value

El servidor completa su información una sola vez — al ingresar — y esa información alimenta todos los procesos posteriores sin volver a pedírsela: contratos, boletas, certificados, vacaciones y reportes salen de un único legajo digital confiable.

## Requirements

### Validated

- ✓ Gestión de empleados (CRUD básico, modelo `Empleado`) — existente
- ✓ Contratos y adendas (modelo `ContratosAdendas`, `contratos_views.py`) — existente
- ✓ Planilla mensual de remuneraciones (modelo `PlanillaMensual`, `remuneraciones_views.py`) — existente parcial
- ✓ Gestión de vacaciones (`/api/v1/vacaciones/`) — existente parcial
- ✓ Almacenamiento de documentos digitales (modelo `DocumentosDigitales`) — existente
- ✓ Autenticación, roles y permisos (`Usuario`, `Rol`, `Permiso`) — existente
- ✓ Modelo de onboarding (`OnboardingEmpleado`, `onboarding_service`) — existente parcial

### Active

#### Onboarding y Legajo Digital (v1 — Priorizado)
- [ ] Envío de correo de bienvenida al crear usuario en onboarding
- [ ] Vista restringida para el empleado en onboarding (solo accede a sus secciones de carga)
- [ ] Carga de foto de perfil en datos personales
- [ ] Subida de documentos PDF por sección: datos personales (DNI, carné de extranjería), familiares (DNI familiar, partida de nacimiento), académico (certificados, diplomas)
- [ ] Subida de documentos en datos laborales: DDJJ, CV, certificado de trabajo, carta de recomendación (solo subida — RRHH gestiona los datos laborales)
- [ ] Legajo digital unificado: vista RRHH con todos los datos y documentos del empleado por sección

#### Información Personal y Laboral (v1 — Priorizado)
- [ ] Empleado puede actualizar datos personales, contacto y familiares con flujo de aprobación RRHH
- [ ] RRHH recibe alertas de cambios y aprueba/rechaza modificaciones antes de registrarlas
- [ ] Generación de certificados y constancias de trabajo en PDF según datos laborales
- [ ] Alertas de vencimiento de contratos y adendas con reportes por oficina
- [ ] Generación de contratos y adendas en PDF
- [ ] Generación de archivos Excel para carga masiva en AIRHSP (altas y bajas)

#### Remuneraciones (v1 — Priorizado)
- [ ] Configuración de parámetros salariales (remuneración fija, bonos, gratificaciones, descuentos deducibles/no deducibles, retenciones, cargas sociales)
- [ ] Generación de planilla detallada por meta presupuestal (plazo indeterminado, determinado, subsidios)
- [ ] Carga masiva de descuentos
- [ ] Generación de boletas de pago descargables por el colaborador
- [ ] Reportes: por banco y modalidad, descuentos por modalidad, sistema de pensiones
- [ ] Exportación Excel para AFP Net (planilla)
- [ ] Exportación Excel para PDT-PLAME (incluyendo liquidaciones)
- [ ] Exportación Excel de ingresos, descuentos y sueldo neto
- [ ] Archivo Excel zipeado para carga de planilla web
- [ ] Certificado de Retención de 4ta categoría (anual y a la fecha de cese)
- [ ] Certificado de rentas de 5ta categoría

#### Vacaciones (v1 — Priorizado)
- [ ] Empleado registra solicitud de goce vacacional aprobada por jefe inmediato
- [ ] Consulta en línea de saldo vacacional vigente y acumulación por tipo de contrato
- [ ] Solicitud de días fraccionados según calendario laboral
- [ ] RRHH gestiona solicitudes, revisa conflictos, aprueba/rechaza y actualiza saldos
- [ ] Integración automática de vacaciones en liquidaciones
- [ ] Reporte de récord vacacional por servidor
- [ ] Reporte de vacaciones no gozadas y truncas
- [ ] Reporte total por oficinas
- [ ] Reporte provisional mensual para finanzas (con cálculo por mes/día trabajado, descontando licencias sin goce)

### Out of Scope

| Módulo | Razón |
|--------|-------|
| Proceso de Selección y Reclutamiento | Alta complejidad, no es prioridad v1 — diferir a v2 |
| Proceso de Liquidaciones | Depende de Remuneraciones y Desvinculación completos — diferir a v2 |
| Inducción virtual (videos, evaluaciones) | Requiere plataforma e-learning — diferir a v2 |
| Desplazamiento (rotación, traslados) | Depende de Legajo e Info Laboral completos — diferir a v2 |
| Proceso de Desvinculación | Requiere integración con múltiples áreas — diferir a v2 |
| Capacitación y PDP | Alta complejidad, no es prioridad v1 — diferir a v2 |
| Diseño de Puesto y Organigrama | Depende de definición organizacional — diferir a v2 |
| Comunicación Interna | No es core RRHH operativo — diferir a v2 |
| Gestión de Rendimiento (metas, SERVIR) | Requiere integración normativa específica — diferir a v2 |

## Context

- **Stack existente**: Django 4.2 + DRF backend, React 18 + TypeScript + Vite frontend, MySQL `bd_rrhh_intranet`
- **Modelos clave ya existentes**: `Empleado`, `Area`, `DatosLaborales`, `ContratosAdendas`, `DocumentosDigitales`, `PlanillaMensual`, `OnboardingEmpleado`, `Rol`, `Permiso`
- **API base**: `/api/v1/` con patrón ViewSet + `APIResponse` wrapper. Frontend con React Query v5
- **PDF**: Cadena xhtml2pdf → WeasyPrint → ReportLab (solo ReportLab confiable en Windows)
- **Contexto peruano**: Legislación laboral peruana — AFP, ONP, PDT-PLAME, gratificaciones (julio/diciembre), CTS, 4ta y 5ta categoría de renta
- **Caso disparador**: Usuario `ggarcia` completó onboarding pero no recibió correo de bienvenida — primer bug a resolver
- **Email**: Backend Django con sistema de envío de correo — revisar configuración en settings

## Constraints

- **Tech**: Stack fijo (Django + React) — no introducir nuevas tecnologías sin justificación
- **PDF en Windows**: Solo ReportLab es confiable — WeasyPrint falla por dependencia GTK
- **Legislación**: Cálculos de remuneraciones deben seguir normativa peruana (SUNAT, SUNAFIL, AFP Net, PDT-PLAME)
- **Datos**: MySQL — ORM patterns específicos (PKs personalizados: `empleado_id`, `contrato_id`)
- **Seguridad**: Empleados en onboarding solo ven sus propias secciones — no acceso admin

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Empleado accede con cuenta normal pero vista restringida | RRHH crea la cuenta, el onboarding es una vista limitada del sistema, no portal separado | — Pending |
| Documentos integrados por sección (no módulo separado) | Flujo más natural: cada documento junto a sus datos relacionados | — Pending |
| DDJJ como subida de archivo PDF (no formulario digital) | El empleado firma y sube el PDF — sin necesidad de formulario digital en v1 | — Pending |
| Legajo digital como vista unificada en panel RRHH | RRHH ve todo junto; el empleado ve sus propias secciones | — Pending |

---
*Last updated: 2026-03-13 after initialization*
