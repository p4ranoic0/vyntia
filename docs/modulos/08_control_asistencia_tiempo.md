# Módulo 08 — Control de Asistencia, Tiempo y Turnos

> **Criticidad:** ALTA · **Tier:** Starter · **Dependencias:** M03 (empleados), M04 (impacto en planilla)
> **Procesos SERVIR cubiertos:** 10 (Control de asistencia), 11 (Desplazamiento — compartido con M03)

---

## 1. Alcance

Captura, gestiona y reporta asistencia, turnos, vacaciones, licencias y permisos. Es la **fuente principal de datos para el cálculo de planilla** (M04).

---

## 2. Sub-módulos

### 2.1 Captura de marcaciones
- **Biométrico físico**: integración con ZKTeco, Suprema, HID
- **Móvil con geolocalización**: app con geofencing configurable
- **Reconocimiento facial con liveness**: selfie + detección de vida (anti-fraude)
- **PC con huella/contraseña**: escritorios con lector biométrico
- **QR code**: marcación contactless
- **Web**: para trabajadores remotos con IP validada
- Políticas por perfil (qué métodos permite cada empleado)

### 2.2 Gestión de turnos y horarios
- **Turnos fijos**: 8-17, 9-18, etc.
- **Turnos rotativos**:
  - 4×3 (trabajar 4 días, descansar 3)
  - 6×1 (minería día de trabajo)
  - **14×7 minería** (14 días campamento, 7 descanso)
- **Horarios flexibles** (core hours con entrada/salida variable)
- **Jornada parcial** (<4h diarias)
- **Jornada nocturna** (22:00-06:00, recargo 35%)
- **Home office** (con control de horas trabajadas)

### 2.3 Planificador de turnos
- Calendarios por equipo/área
- Rotación automática
- Coberturas mínimas (ej. 3 personas en turno)
- Intercambio de turnos entre compañeros (con aprobación jefe)
- Restricciones (descanso mínimo entre turnos, máximo semanal)
- Integración con feriados nacionales y regionales

### 2.4 Gestión de vacaciones
- Balance de días disponibles/utilizados/pendientes
- Programación individual y del equipo (gantt)
- Solicitud → aprobación jefe → confirmación RRHH
- Cálculo automático de período a gozar
- **Venta de vacaciones** (hasta 15 días para 728)
- **Vacaciones truncas** al cese (cálculo automático)
- **Triple vacacional** (Ley 30012) — alerta si el empleador no otorga en plazo

### 2.5 Licencias y permisos
Con goce de haber:
- Maternidad (98 días — subsidio EsSalud)
- Paternidad (10 días — Ley 29409)
- Duelo (5-8 días según parentesco)
- Matrimonio (3-5 días según política)
- Lactancia (1 hora diaria hasta 1 año del bebé)
- Por adopción (30 días)
- Sindical (según CCT)
- Por capacitación (M05)

Sin goce de haber:
- Motivos personales
- Estudios
- Cargo público honorario

### 2.6 Descansos médicos
- Registro con CITT (Certificado de Incapacidad Temporal para el Trabajo)
- **Días 1-20: empleador paga**
- **Día 21 en adelante: subsidio EsSalud** (hasta 340 días/año)
- Integración con EsSalud para validación de CITT
- Descuento en asistencia sin afectar beneficios sociales

### 2.7 Horas extras y compensatorias
- Autorización previa (solicitud + aprobación)
- Cálculo automático de recargos (25% primeras 2h, 35% desde la 3ra)
- Registro en planilla (concepto 0106 Tabla 22 SUNAT)
- Compensación con descanso (bancos de horas) — opcional

### 2.8 Desplazamientos (integrado con M03.6)
- Rotación, encargatura, destaque, comisión de servicios, permuta
- Afectación en asistencia por cambio de sede/horario

### 2.9 Cálculo de tareo mensual
- Consolidación de marcaciones por empleado
- Cálculo de:
  - Días trabajados
  - Días subsidiados (descanso médico)
  - Días no laborados
  - Horas extras
  - Tardanzas / inasistencias
- **Cierre del tareo** habilita cálculo de planilla (M04)

---

## 3. Entidades principales

```
Attendance
├── Employee
├── Date
├── ClockIn, ClockOut
├── Method (BIOMETRICO_HUELLA, FACIAL, QR, WEB, MOVIL)
├── Location (GPS + validación geofence)
├── DeviceId
└── AnomalyFlag (tardanza, inasistencia, sobre-horario)

Shift (turno)
├── Name
├── StartTime, EndTime
├── BreakMinutes
├── IsRotating
├── IsNightShift
└── OvertimeRules

Schedule (horario asignado)
├── Employee
├── Shift
├── Period (rango de fechas)
└── Exceptions (días con otro turno)

TimeOff / Leave
├── Employee
├── Type (VACACIONES, MATERNIDAD, PATERNIDAD, ENFERMEDAD, DUELO, etc.)
├── StartDate, EndDate
├── Days
├── Paid (S/N)
├── SubsidyEssalud (S/N)
├── Status (SOLICITADO, APROBADO, RECHAZADO, EN_GOCE, FINALIZADO)
├── Approver
├── Document (CITT, certificado, etc.)
└── AffectsBenefits (computo para CTS, etc.)

MedicalRest
├── Employee
├── CITT (número, fecha, diagnostico código CIE-10)
├── Days
├── DoctorData
├── Validated (con EsSalud)
└── Subsidy

OvertimeRequest
├── Employee
├── Date
├── Hours
├── Reason
├── Approver
├── Status
└── Rate25Hours, Rate35Hours

TareaMensual (cierre)
├── Period (año/mes)
├── DaysWorked
├── DaysSubsidized
├── DaysNonWorked
├── OvertimeHours
├── Tardiness
└── Status (ABIERTO, CERRADO)
```

---

## 4. Workflows clave

### 4.1 Solicitud de vacaciones
```
1. Empleado consulta balance disponible
2. Solicita rango en calendario
3. Sistema verifica: balance, conflictos de equipo, políticas
4. Notificación al jefe directo
5. Jefe aprueba/rechaza con comentarios
6. RRHH valida y confirma (si política lo requiere)
7. Actualización en calendario
8. Pago anticipado por M04 (si política lo indica)
9. Durante el goce: estado EN_GOCE
10. Al retornar: estado FINALIZADO + actualización balance
```

### 4.2 Registro de descanso médico
```
1. Empleado informa descanso + envía CITT digital
2. RRHH valida CITT con EsSalud
3. Registro automático en ausencias
4. Cálculo: días 1-20 empleador, 21+ EsSalud
5. Impacto en planilla del mes
6. Si >340 días/año: alerta (fin de cobertura)
```

### 4.3 Cierre de tareo mensual
```
1. Fecha de corte (ej. día 25 del mes)
2. Consolidación automática de marcaciones
3. Aplicación de excepciones (vacaciones, licencias, descansos)
4. Revisión por RRHH (detección de anomalías)
5. Correcciones manuales con trazabilidad
6. Cierre definitivo
7. Emisión de datos a M04 (evento AttendancePeriodConsolidated)
```

---

## 5. Integraciones críticas

| Sistema | Propósito |
|---------|-----------|
| ZKTeco SDK | Lectura de dispositivos biométricos |
| Suprema SDK | Lectura de dispositivos biométricos |
| HID | Control de acceso integrado |
| Google/Apple Maps | Geofencing |
| AWS Rekognition / ML Kit | Reconocimiento facial con liveness |
| EsSalud CITT | Validación de descansos médicos |
| Calendario nacional (feriados) | Actualización automática |

---

## 6. Consideraciones especiales

### 6.1 Protección de datos (Ley 29733)
- Datos biométricos son **sensibles**: cifrado AES-256, banco registrado ante ANPD
- Geolocalización: solo en jornada, finalidad declarada, evaluación de impacto
- Retención limitada (12 meses para marcaciones detalladas)

### 6.2 Cumplimiento laboral
- Sanción por no registrar asistencia: infracción grave (3-20 UIT según tamaño empresa)
- Obligación de llevar libro de registro o su equivalente digital

### 6.3 Sector minero y construcción
- Régimen 14×7 (14 días en campamento + 7 descanso) especial
- Pago por guardia (feriados en campamento)
- SCTR obligatorio

### 6.4 Marcación con geofencing
- Radio configurable por ubicación de trabajo
- Validación cruzada con WiFi corporativo cuando aplique
- Registro de intentos fuera de zona (no bloquea, solo alerta)

---

## 7. KPIs del módulo
- Tasa de ausentismo (ausencias / días laborables)
- Tasa de tardanza promedio
- % vacaciones gozadas vs acumuladas
- Horas extras ejecutadas / presupuestadas
- Tiempo de cierre de tareo mensual (meta: <24h del día corte)
- % de marcaciones con anomalía

---

## 8. Referencias normativas
- [D.Leg. 713 — Descansos remunerados](https://www.gob.pe/institucion/mtpe/normas-legales/)
- [Ley 30012 — Triple vacacional](https://www.gob.pe/institucion/mtpe/normas-legales/)
- [Ley 29409 — Licencia paternidad](https://www.gob.pe/institucion/mtpe/normas-legales/)
- [Ley 30367 — Lactancia](https://www.gob.pe/institucion/mtpe/normas-legales/)
- [EsSalud — CITT](https://www.essalud.gob.pe/)
- [Ley 29733 + D.S. 016-2024-JUS — Datos Personales](https://www.gob.pe/)

---

## 9. MDs relacionados
- `modulos/03_gestion_empleo.md` (desplazamientos)
- `modulos/04_gestion_compensacion.md` (horas extras, descuentos)
- `normativa/N11_proteccion_datos_personales.md`
