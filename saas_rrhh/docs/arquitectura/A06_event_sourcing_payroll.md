# A06. Event Sourcing en Payroll + Auditoría Temporal

> Patrón de persistencia que guarda cada cambio como un evento inmutable, permitiendo reconstruir cualquier estado histórico. Se aplica **acotado al Bounded Context de Payroll** (no global) porque cumple requisitos regulatorios peruanos de trazabilidad.

---

## 1. Por qué Event Sourcing solo en Payroll

El patrón agrega complejidad (storage, proyecciones, versionado de eventos). No se justifica aplicarlo globalmente. **En Payroll sí** por cuatro razones:

1. **Auditoría SUNAT/SUNAFIL**: cualquier planilla generada debe poder reconstruirse con sus insumos exactos años después (libro de planillas electrónico, Art. 10 Ley 28051).
2. **Recálculos retroactivos**: cambio de UIT mid-year, modificación de RMV, correcciones de asistencia afectan planillas ya cerradas. Se necesita reabrir y recalcular.
3. **Arrears** (diferenciales): ajustes salariales retroactivos generan pagos compensatorios con base en la secuencia histórica exacta.
4. **Prescripción laboral 4 años**: un trabajador puede reclamar beneficios hasta 4 años después (Ley 27321); el sistema debe soportar reconstrucción exacta.

Para el resto del sistema (legajos, ausencias, capacitación) basta con audit trail clásico (CDC + tablas `_history`).

---

## 2. Conceptos clave

### 2.1 Eventos de Payroll

Cada evento es un hecho inmutable del pasado. Nombres en tiempo pasado:

| Evento | Descripción | Carga (payload) |
|---|---|---|
| `PayrollPeriodOpened` | Se abre un período mensual de planilla | período, empresa_id |
| `EmployeeAdded` | Empleado incorporado al periodo | empleado_id, fecha_inicio, tipo_contrato |
| `SalaryStructureAssigned` | Asignación de estructura salarial | empleado_id, estructura_id, desde |
| `AttendanceRegistered` | Registro de asistencia (días efectivos, tardanzas, faltas) | empleado_id, fecha, tipo_marca, horas |
| `BonusAdded` | Bono extraordinario (productividad, cumpleaños) | empleado_id, concepto, monto, fecha |
| `DeductionApplied` | Descuento aplicado (préstamo, judicial) | empleado_id, concepto, monto, cuota |
| `LeaveRequested` / `LeaveApproved` | Vacaciones o licencia | empleado_id, tipo, desde, hasta |
| `SalaryRevisioned` | Revisión salarial (aplica retroactivo) | empleado_id, nuevo_basico, fecha_efectiva |
| `PayslipCalculated` | Cálculo del recibo | empleado_id, conceptos[], neto |
| `PayslipApproved` | Aprobación de la planilla | periodo, aprobador_id |
| `PayslipPaid` | Pago ejecutado | empleado_id, monto, cuenta, fecha_pago |
| `PayrollPeriodClosed` | Cierre del período | periodo, hash_snapshot |
| `CorrectionIssued` | Corrección posterior al cierre | periodo, empleado_id, motivo, delta |

### 2.2 Inmutabilidad y reglas

- **Eventos nunca se editan ni eliminan**. Correcciones = eventos nuevos.
- **Orden estricto** por `aggregate_id` + `version`.
- **Idempotencia**: cada evento tiene `event_id` único; reprocesarlo no duplica efectos.

---

## 3. Modelo de datos

### 3.1 Event Store

```sql
CREATE TABLE payroll_events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  aggregate_type VARCHAR(50) NOT NULL,        -- "Payroll" | "Payslip" | "Employee"
  aggregate_id UUID NOT NULL,                 -- id del agregado al que pertenece
  version INT NOT NULL,                       -- secuencia del evento dentro del agregado
  event_type VARCHAR(80) NOT NULL,            -- "PayslipCalculated", etc.
  payload JSONB NOT NULL,                     -- datos del evento
  metadata JSONB,                             -- causa, user_id, ip, trace_id
  occurred_at TIMESTAMP NOT NULL DEFAULT NOW(),
  recorded_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, aggregate_id, version)
);

CREATE INDEX idx_events_aggregate ON payroll_events (tenant_id, aggregate_id, version);
CREATE INDEX idx_events_type ON payroll_events (tenant_id, event_type, occurred_at);
```

### 3.2 Snapshots (optimización de performance)

Replay desde cero es caro si un agregado tiene cientos/miles de eventos. Se toman snapshots cada N eventos (ej. cada 50) o al cierre del período.

```sql
CREATE TABLE payroll_snapshots (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  aggregate_id UUID NOT NULL,
  version INT NOT NULL,                       -- versión del último evento aplicado
  state JSONB NOT NULL,                       -- estado serializado
  taken_at TIMESTAMP DEFAULT NOW(),
  UNIQUE (tenant_id, aggregate_id, version)
);
```

### 3.3 Proyecciones de lectura (Read Models / CQRS)

Para queries rápidas de UI y reports, se mantienen proyecciones denormalizadas:

```sql
-- Proyección: resumen mensual por empleado
CREATE TABLE proyeccion_planilla_mensual (
  tenant_id UUID NOT NULL,
  empleado_id UUID NOT NULL,
  periodo VARCHAR(7) NOT NULL,                -- "2026-04"
  basico NUMERIC(12,2),
  asignacion_familiar NUMERIC(12,2),
  horas_extras NUMERIC(12,2),
  bonificaciones NUMERIC(12,2),
  gratificaciones NUMERIC(12,2),
  aporte_afp NUMERIC(12,2),
  aporte_onp NUMERIC(12,2),
  renta_5ta NUMERIC(12,2),
  neto NUMERIC(12,2),
  bruto NUMERIC(12,2),
  updated_at TIMESTAMP,
  PRIMARY KEY (tenant_id, empleado_id, periodo)
);

-- Proyección: dashboard empresa
CREATE TABLE proyeccion_planilla_empresa (
  tenant_id UUID NOT NULL,
  empresa_id UUID NOT NULL,
  periodo VARCHAR(7) NOT NULL,
  total_empleados INT,
  total_bruto NUMERIC(14,2),
  total_neto NUMERIC(14,2),
  total_aportes_empleador NUMERIC(14,2),
  PRIMARY KEY (tenant_id, empresa_id, periodo)
);
```

Las proyecciones se actualizan por **proyectores** asíncronos que escuchan el event store.

---

## 4. Implementación (Python / pseudocódigo)

### 4.1 Agregado Payslip

```python
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

@dataclass
class Payslip:
    id: UUID
    tenant_id: UUID
    empleado_id: UUID
    periodo: str
    version: int = 0
    conceptos: dict = field(default_factory=dict)
    estado: str = "borrador"
    neto: Decimal = Decimal("0")
    
    def apply(self, event: dict):
        """Aplica un evento al estado (mutación interna)."""
        kind = event["type"]
        if kind == "PayslipCalculated":
            self.conceptos = event["payload"]["conceptos"]
            self.neto = Decimal(event["payload"]["neto"])
            self.estado = "calculado"
        elif kind == "PayslipApproved":
            self.estado = "aprobado"
        elif kind == "PayslipPaid":
            self.estado = "pagado"
        elif kind == "CorrectionIssued":
            delta = event["payload"]["delta_conceptos"]
            for k, v in delta.items():
                self.conceptos[k] = self.conceptos.get(k, Decimal("0")) + Decimal(v)
            self.neto = sum(self.conceptos.values())
        self.version += 1
    
    @classmethod
    def from_events(cls, tenant_id, aggregate_id, events):
        """Reconstruye el agregado a partir de la lista ordenada de eventos."""
        slip = cls(
            id=aggregate_id, tenant_id=tenant_id,
            empleado_id=events[0]["payload"]["empleado_id"],
            periodo=events[0]["payload"]["periodo"]
        )
        for ev in events:
            slip.apply(ev)
        return slip

class PayslipRepository:
    def load(self, tenant_id, aggregate_id) -> Payslip:
        # 1. Cargar snapshot más reciente (si existe)
        snapshot = db.query_one(
            "SELECT version, state FROM payroll_snapshots "
            "WHERE tenant_id=%s AND aggregate_id=%s ORDER BY version DESC LIMIT 1",
            tenant_id, aggregate_id
        )
        start_version = snapshot.version if snapshot else 0
        
        # 2. Cargar eventos posteriores al snapshot
        events = db.query(
            "SELECT event_type, payload FROM payroll_events "
            "WHERE tenant_id=%s AND aggregate_id=%s AND version > %s ORDER BY version",
            tenant_id, aggregate_id, start_version
        )
        
        # 3. Reconstruir estado
        if snapshot:
            slip = Payslip.from_state(snapshot.state)
        else:
            slip = Payslip.from_events(tenant_id, aggregate_id, events[:1])
            events = events[1:]
        
        for ev in events:
            slip.apply(ev)
        return slip
    
    def save_event(self, tenant_id, aggregate_id, event_type, payload, expected_version):
        """Persiste evento con control de concurrencia optimista."""
        db.execute(
            "INSERT INTO payroll_events "
            "(tenant_id, aggregate_type, aggregate_id, version, event_type, payload) "
            "VALUES (%s, 'Payslip', %s, %s, %s, %s::jsonb)",
            tenant_id, aggregate_id, expected_version + 1, event_type, payload
        )
        # 4. Publicar al bus para proyectores
        event_bus.publish("PayrollEvent", {
            "tenant_id": tenant_id, "aggregate_id": aggregate_id,
            "version": expected_version + 1, "type": event_type, "payload": payload
        })
```

### 4.2 Recálculo retroactivo

```python
def recalcular_periodo(tenant_id, periodo, motivo):
    """Ante cambio de UIT/RMV/asistencia, reemite PayslipCalculated para todos los empleados."""
    empleados = obtener_empleados_del_periodo(tenant_id, periodo)
    for emp_id in empleados:
        payslip_id = obtener_payslip_id(tenant_id, emp_id, periodo)
        nuevo_calculo = calcular_conceptos(tenant_id, emp_id, periodo)
        
        # Emitir CorrectionIssued en vez de editar el original
        repo.save_event(
            tenant_id, payslip_id, "CorrectionIssued",
            {
                "motivo": motivo,
                "fecha_correccion": datetime.now().isoformat(),
                "delta_conceptos": computar_delta(payslip_original, nuevo_calculo),
                "conceptos_nuevos": nuevo_calculo
            },
            expected_version=obtener_version_actual(tenant_id, payslip_id)
        )
    
    # Reconstruir proyecciones
    reproyectar_periodo(tenant_id, periodo)
```

---

## 5. Proyectores asíncronos

Un proyector escucha el bus de eventos y actualiza la tabla de lectura:

```python
@event_handler("PayrollEvent")
def actualizar_proyeccion_mensual(event):
    if event["type"] in ("PayslipCalculated", "CorrectionIssued"):
        payload = event["payload"]
        db.execute("""
            INSERT INTO proyeccion_planilla_mensual (
                tenant_id, empleado_id, periodo, basico, ..., neto, updated_at
            ) VALUES (%s, %s, %s, %s, ..., %s, NOW())
            ON CONFLICT (tenant_id, empleado_id, periodo) DO UPDATE SET
                basico = EXCLUDED.basico, ...,
                neto = EXCLUDED.neto, updated_at = NOW()
        """, ...)
```

---

## 6. Temporal tables para el resto del sistema

Para el resto (legajos, contratos, evaluaciones) no se usa ES sino el patrón **Temporal Table / SCD Type 2**:

```sql
CREATE TABLE empleado_historial (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  empleado_id UUID NOT NULL,
  dni VARCHAR(15),
  nombres VARCHAR(200),
  area_id UUID,
  cargo_id UUID,
  valid_from TIMESTAMP NOT NULL,
  valid_to TIMESTAMP,                          -- NULL = vigente
  operacion VARCHAR(10),                       -- INSERT | UPDATE | DELETE
  operated_by UUID
);

-- Trigger AFTER UPDATE en empleados cierra el registro vigente e inserta uno nuevo
```

Esto es más simple que ES completo y suficiente para auditoría general.

---

## 7. Consideraciones de performance

- **Snapshots**: cada 50 eventos o al cierre del período.
- **Particionado** de `payroll_events` por mes (`PARTITION BY RANGE (occurred_at)`).
- **Índices** sólo en columnas realmente usadas en queries (evitar inflar escrituras).
- **Proyecciones materializadas** refrescadas cada N minutos para dashboards no críticos.
- **Outbox pattern**: el evento se inserta en la misma transacción que la BD transaccional, un proceso lo reenvía al bus garantizando at-least-once.

Benchmark típico para reconstruir un agregado con 200 eventos + snapshot: **50-200 ms**. Sin snapshot (replay completo): 2-5 s. Con snapshot es viable para UI en tiempo real.

---

## 8. Versionado de eventos

Los eventos nunca se rompen pero evolucionan. Estrategia:

- Cada evento tiene `version_schema` en metadata.
- Se mantiene un `EventUpcaster` que convierte eventos antiguos al formato nuevo al cargarlos.
- Nunca se migran eventos existentes; siempre se agregan upcasters.

---

## 9. Requisitos regulatorios cubiertos

| Norma | Requisito | Cómo se cumple con ES |
|---|---|---|
| Art. 10 Ley 28051 | Libro planillas electrónico por 5 años | Event store conserva todo |
| Ley 27321 | Prescripción laboral 4 años | Reconstrucción exacta hasta 4+ años atrás |
| SUNAT / PLAME | Trazabilidad de conceptos declarados | Cada concepto tiene origen auditable |
| Ley 29733 | Registro de operaciones sobre datos | Todo evento lleva actor, ip, timestamp |
| Inspecciones SUNAFIL | Presentación de libro de planillas por período | Query dirigida al snapshot del período |

---

## 10. Checklist

- [ ] Event Store `payroll_events` con constraint UNIQUE (aggregate, version)
- [ ] Snapshots configurados cada 50 eventos
- [ ] Particionado mensual de la tabla de eventos
- [ ] Outbox pattern para publicar al bus con consistencia
- [ ] Proyecciones materializadas para queries comunes
- [ ] Recálculo retroactivo emite CorrectionIssued, nunca modifica eventos
- [ ] Upcasters registrados para evolución de esquemas
- [ ] Test: reconstruir payslip a fecha X de hace 3 años y verificar match con boleta impresa
- [ ] Retención de eventos alineada con prescripción laboral (mínimo 5 años)
- [ ] Backups separados del event store (append-only, cold storage)
