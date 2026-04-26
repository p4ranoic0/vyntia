# Módulo 04 — Gestión de la Compensación (Planilla)

> **Criticidad:** MÁXIMA · **Tier:** Starter · **Dependencias:** Módulo 03 (Empleados), Módulo 08 (Asistencia)
>
> Este módulo es el **núcleo de cumplimiento regulatorio** del SaaS. Un error aquí genera multas SUNAFIL (hasta 300 UIT), multas SUNAT por declaraciones erradas, y pérdida de confianza del cliente.

---

## 1. Alcance funcional

### 1.1 Sub-módulos
| Código | Sub-módulo | Descripción |
|--------|-----------|-------------|
| 04.1 | Planilla de Remuneraciones | Motor de cálculo multi-régimen |
| 04.2 | Administración de Pensiones | AFP, ONP, pensionistas activos |
| 04.3 | Beneficios Sociales | CTS, gratificaciones, vacaciones, utilidades |
| 04.4 | Retenciones y Aportes | Renta 5ta, EsSalud/EPS, AFP, ONP, judiciales |
| 04.5 | Boletas Electrónicas | Generación, firma digital, envío |
| 04.6 | Exportadores Oficiales | PLAME, T-Registro, AFPnet, bancos |
| 04.7 | Liquidación de BBSS | Motor automático al cese (48h) |
| 04.8 | Provisiones Contables | Contabilización mensual de CTS, grati, vacaciones |
| 04.9 | Ajustes y Reliquidaciones | Motor de recálculo retroactivo |

### 1.2 Regímenes laborales soportados (Strategy Pattern)
| Régimen | Norma base | Estrategia (clase) |
|---------|-----------|---------------------|
| General Privado | D.Leg. 728 / D.S. 003-97-TR | `Regime728Strategy` |
| CAS | D.Leg. 1057 | `RegimeCASStrategy` |
| Carrera Administrativa | D.Leg. 276 | `Regime276Strategy` |
| Servicio Civil | Ley 30057 | `RegimeServirStrategy` |
| MYPE Micro | Ley 32353 | `RegimeMypeMicroStrategy` |
| MYPE Pequeña | Ley 32353 | `RegimeMypePequenaStrategy` |
| Agrario (SP-1) | Ley 31110 | `RegimeAgrarioSP1Strategy` |
| Agrario (SP-2) | Ley 31110 | `RegimeAgrarioSP2Strategy` |
| Construcción Civil | Ley 727 + CAPECO-FTCCP | `RegimeConstruccionStrategy` |
| Minero | D.S. 014-92-EM | `RegimeMineroStrategy` |
| Hogar | Ley 31047 | `RegimeHogarStrategy` |
| Pesquero | Normas específicas | `RegimePesqueroStrategy` |
| Textil/Confecciones | Ley 29245 | `RegimeTextilStrategy` |

---

## 2. Reglas de negocio críticas

### 2.1 Parámetros globales (actualizables anualmente por el sistema)
```yaml
UIT_2026: 5500
RMV_2026: 1130
ASIGNACION_FAMILIAR_2026: 113  # 10% RMV
APORTE_AFP_OBLIGATORIO: 0.10   # 10%
PRIMA_SISCO_2026_Q2: 0.0137    # 1.37% con RMA variable
RMA_SPP_ABR_JUN_2026: 12598.91
APORTE_ONP: 0.13               # 13%
APORTE_ESSALUD: 0.09           # 9% empleador
CREDITO_EPS: 0.0225            # 2.25% (trabajador en EPS)
JORNADA_MAXIMA_DIARIA: 8
JORNADA_MAXIMA_SEMANAL: 48
RECARGO_HORA_EXTRA_25: 0.25    # primeras 2 horas
RECARGO_HORA_EXTRA_35: 0.35    # desde la 3ra hora
RECARGO_NOCTURNO: 0.35         # 22:00 a 06:00
```

### 2.2 Conceptos de planilla (mapeados a Tabla 22 SUNAT)
Cada concepto creado por el administrador **debe mapearse obligatoriamente** a un código oficial SUNAT. Ejemplos:

| Código SUNAT | Concepto | Rubro | Afecta Renta 5ta | Afecta AFP/ONP | Afecta EsSalud | Afecta CTS |
|--------------|----------|-------|------------------|----------------|----------------|------------|
| 0101 | Alimentación principal — dinero | Ingreso | SÍ | SÍ | SÍ | SÍ |
| 0102 | Alimentación principal — especie | Ingreso | SÍ | SÍ | SÍ | SÍ |
| 0103 | Comisiones regulares | Ingreso | SÍ | SÍ | SÍ | SÍ (si ≥3 veces/semestre) |
| 0104 | Asignación familiar | Ingreso | SÍ | SÍ | SÍ | SÍ |
| 0106 | Horas extras | Ingreso | SÍ | SÍ | SÍ | SÍ (si ≥3 veces/semestre) |
| 0107 | Vacaciones | Ingreso | SÍ | SÍ | SÍ | NO (ya computada) |
| 0109 | Gratificación Fiestas Patrias | Ingreso | SÍ | SÍ | NO (Ley 30334) | NO |
| 0110 | Gratificación Navidad | Ingreso | SÍ | SÍ | NO (Ley 30334) | NO |
| 0304 | Bonificación Extraordinaria (9% Ley 30334) | Ingreso no remun. | SÍ | NO | NO | NO |
| 0503 | Indemnización despido arbitrario | Indemnización | NO | NO | NO | NO |
| 0601 | Aporte AFP - Fondo | Tributo | — | — | — | — |
| 0605 | Retención Renta 5ta | Tributo | — | — | — | — |
| 0606 | Comisión AFP / Prima | Tributo | — | — | — | — |
| 0607 | Aporte ONP | Tributo | — | — | — | — |
| 0801 | Aporte EsSalud (empleador) | Aporte | — | — | — | — |

> **Detalle completo de Tabla 22:** → `normativa/N06_planilla_electronica_sunat.md`

### 2.3 Fórmulas de cálculo principales

#### CTS (régimen 728)
```
Remuneracion_Computable = Basico + Asig_Familiar + (Gratificacion_Ultima / 6) + Promedio_Variables

donde Promedio_Variables = Σ(horas_extras + comisiones + bonos) / 6
  solo si cada concepto fue percibido en ≥3 meses del semestre

CTS_Semestral = (Rem_Computable / 12 × meses_completos) + (Rem_Computable / 360 × dias_restantes)

Períodos:
- Depósito Mayo: computa Nov(año-1) a Abr(año)
- Depósito Noviembre: computa May(año) a Oct(año)

Plazo depósito: hasta el 15 del mes siguiente al cierre del período
```

#### Gratificaciones (Ley 27735 + Ley 30334)
```
Gratificacion = (Rem_Computable / 6) × meses_trabajados_semestre
Bonif_Extraord = Gratificacion × 0.09  (si EsSalud)
Bonif_Extraord = Gratificacion × 0.0675 (si EPS)

Requisitos: estar en planilla al 15-jul (FP) y 15-dic (Navidad)
Plazos: primera quincena julio; primera quincena diciembre
```

#### Vacaciones truncas
```
Vacaciones_Truncas = (Rem_Computable / 360) × dias_computables

Donde dias_computables = (meses × 30) + dias_del_mes_parcial
```

#### Renta de 5ta Categoría — proyección mensual
```python
# Algoritmo mensual
def retencion_renta_5ta(mes, remuneracion_mes, remuneraciones_ya_pagadas, gratificaciones_previstas):
    # 1. Remuneración Bruta Anual (RBA)
    meses_restantes = 13 - mes  # incluye mes actual
    RBA = (remuneracion_mes * meses_restantes) + remuneraciones_ya_pagadas + gratificaciones_previstas
    
    # 2. Renta Neta de Trabajo
    UIT = 5500  # 2026
    renta_neta = max(0, RBA - (7 * UIT))
    
    # 3. Escala progresiva
    if renta_neta <= 5*UIT:
        impuesto = renta_neta * 0.08
    elif renta_neta <= 20*UIT:
        impuesto = (5*UIT * 0.08) + ((renta_neta - 5*UIT) * 0.14)
    elif renta_neta <= 35*UIT:
        impuesto = (5*UIT*0.08) + (15*UIT*0.14) + ((renta_neta - 20*UIT) * 0.17)
    elif renta_neta <= 45*UIT:
        impuesto = (5*UIT*0.08) + (15*UIT*0.14) + (15*UIT*0.17) + ((renta_neta - 35*UIT) * 0.20)
    else:
        impuesto = (5*UIT*0.08) + (15*UIT*0.14) + (15*UIT*0.17) + (10*UIT*0.20) + ((renta_neta - 45*UIT) * 0.30)
    
    # 4. Denominador mensual según el mes
    denominadores = {1:12, 2:12, 3:12, 4:9, 5:8, 6:8, 7:8, 8:5, 9:4, 10:4, 11:4}
    if mes in denominadores:
        retencion_mensual = impuesto / denominadores[mes]
    elif mes == 12:
        retencion_mensual = impuesto - suma_retenciones_anteriores  # ajuste final
    
    return retencion_mensual
```

> **Detalle completo:** → `normativa/N09_renta_5ta_categoria.md`

---

## 3. Arquitectura técnica del motor

### 3.1 Strategy Pattern para regímenes

```python
# Interfaz base
class RegimenEstrategia(ABC):
    @abstractmethod
    def calcular_cts(self, trabajador, periodo) -> Decimal: ...
    
    @abstractmethod
    def calcular_gratificacion(self, trabajador, periodo) -> Decimal: ...
    
    @abstractmethod
    def vacaciones_dias_anuales(self) -> int: ...
    
    @abstractmethod
    def tasa_aporte_salud_empleador(self) -> Decimal: ...
    
    @abstractmethod
    def calcular_indemnizacion_despido(self, trabajador) -> Decimal: ...

# Implementaciones concretas
class Regime728Strategy(RegimenEstrategia):
    def vacaciones_dias_anuales(self) -> int:
        return 30
    
    def calcular_cts(self, trabajador, periodo):
        # Fórmula completa 728
        ...

class RegimeMypePequenaStrategy(RegimenEstrategia):
    def vacaciones_dias_anuales(self) -> int:
        return 15  # reducidas en MYPE
    
    def calcular_cts(self, trabajador, periodo):
        # CTS = 15 días/año, tope 90 días
        ...

class RegimeAgrarioSP1Strategy(RegimenEstrategia):
    """Sistema de pago 1: remuneración diaria incluye gratif y CTS"""
    def calcular_remuneracion_diaria(self, basico_mensual):
        # RD = Rem. Básica + 16.66% grat + 9.72% CTS, dividido entre 30
        return (basico_mensual + basico_mensual * 0.1666 + basico_mensual * 0.0972) / 30

# Factory
class RegimenFactory:
    @staticmethod
    def get_strategy(codigo_regimen: str) -> RegimenEstrategia:
        strategies = {
            'D_LEG_728': Regime728Strategy(),
            'CAS_1057': RegimeCASStrategy(),
            'D_LEG_276': Regime276Strategy(),
            'SERVIR_30057': RegimeServirStrategy(),
            'MYPE_MICRO': RegimeMypeMicroStrategy(),
            'MYPE_PEQUENA': RegimeMypePequenaStrategy(),
            'AGRARIO_SP1': RegimeAgrarioSP1Strategy(),
            'AGRARIO_SP2': RegimeAgrarioSP2Strategy(),
            'CONSTRUCCION': RegimeConstruccionStrategy(),
            'MINERO': RegimeMineroStrategy(),
            'HOGAR': RegimeHogarStrategy(),
        }
        return strategies[codigo_regimen]
```

### 3.2 Event Sourcing del contexto Payroll

**Justificación:** SUNAT exige auditabilidad total. Cambios retroactivos (ej. incremento salarial retroactivo) deben ser recalculables sin perder historia.

**Eventos inmutables del agregado PayrollRun:**
```
PayrollRunCreated(tenant_id, periodo, fecha_corte)
SalaryStructureAssigned(trabajador_id, estructura_id, vigencia_desde)
AttendancePeriodConsolidated(trabajador_id, periodo, dias_trabajados, horas_extras)
BonusAdded(trabajador_id, concepto_id, monto, motivo)
DeductionApplied(trabajador_id, concepto_id, monto, origen)
PayslipCalculated(trabajador_id, payslip_snapshot)
PayslipApproved(payslip_id, aprobador_id, timestamp)
PayslipSigned(payslip_id, firma_digital_hash)
PayslipDelivered(payslip_id, canal, timestamp)
PayslipPaid(payslip_id, transferencia_ref, banco)
PayrollRunClosed(periodo, cierre_por, timestamp)
PayrollRunReopened(periodo, motivo, autorizador)  # para reliquidación
```

**Proyecciones (CQRS):**
- `payslip_current_state` → último estado por empleado/período
- `payroll_monthly_summary` → totales por planilla para dashboards
- `plame_export_ready` → datos formateados para PLAME
- `afp_export_ready` → datos formateados para AFPnet

### 3.3 Modelo de datos principal

```sql
-- Parámetros del sistema (actualizables por año)
CREATE TABLE system_parameters (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    code VARCHAR(50) NOT NULL,        -- 'UIT', 'RMV', 'ASIG_FAMILIAR'
    valid_from DATE NOT NULL,
    valid_to DATE,
    value NUMERIC(18,4) NOT NULL,
    metadata JSONB,
    UNIQUE(tenant_id, code, valid_from)
);

-- Conceptos de planilla (catálogo por tenant)
CREATE TABLE payroll_concepts (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    code VARCHAR(20) NOT NULL,        -- código interno
    sunat_code VARCHAR(10) NOT NULL,  -- código Tabla 22 SUNAT
    name VARCHAR(200) NOT NULL,
    type VARCHAR(20),                 -- INCOME, DEDUCTION, CONTRIBUTION, TAX
    subtype VARCHAR(50),
    formula TEXT,                     -- fórmula editable (DSL propia)
    affects_income_tax BOOLEAN,
    affects_afp_onp BOOLEAN,
    affects_essalud BOOLEAN,
    affects_cts BOOLEAN,
    affects_gratification BOOLEAN,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(tenant_id, code)
);

-- Estructura salarial (contrato)
CREATE TABLE salary_structures (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    employee_id UUID NOT NULL,
    regime_code VARCHAR(30) NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE,
    base_salary NUMERIC(12,2),
    has_family_allowance BOOLEAN,
    pension_regime VARCHAR(20),       -- AFP_INTEGRA, AFP_PRIMA, AFP_HABITAT, AFP_PROFUTURO, ONP
    pension_commission_type VARCHAR(10), -- FLUJO, MIXTA, SALDO
    health_regime VARCHAR(20),        -- ESSALUD, EPS
    eps_provider_id UUID,
    cci VARCHAR(20),                  -- nivel 9 de permiso
    bank_code VARCHAR(10)
);

-- Corrida de planilla
CREATE TABLE payroll_runs (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    period_year INT NOT NULL,
    period_month INT NOT NULL,
    period_type VARCHAR(20),          -- REGULAR, ADJUSTMENT, LIQUIDATION
    status VARCHAR(20),               -- DRAFT, CALCULATED, APPROVED, CLOSED, REOPENED
    created_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    closed_by UUID
);

-- Boleta individual (proyección desde event stream)
CREATE TABLE payslips (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    payroll_run_id UUID NOT NULL,
    employee_id UUID NOT NULL,
    gross_income NUMERIC(12,2),       -- nivel 9
    total_deductions NUMERIC(12,2),   -- nivel 9
    net_pay NUMERIC(12,2),            -- nivel 0 (empleado ve)
    concepts JSONB,                   -- detalle de conceptos aplicados
    digital_signature_hash VARCHAR(256),
    is_delivered BOOLEAN,
    event_stream_position BIGINT      -- para recalcular desde eventos
);
```

### 3.4 Permission Levels por campo (crítico)
```
Permlevel 0 (empleado): net_pay, gross_income (su propia boleta)
Permlevel 3 (jefe directo): + deductions_summary
Permlevel 6 (HR): + all_concepts_detail + cci + pension_fund_id
Permlevel 9 (Contabilidad/CFO): + all financial fields + audit_trail
```

---

## 4. Workflows operativos del módulo

### 4.1 Flujo de procesamiento mensual de planilla
```
1. [INICIO MES] Cierre del período anterior confirmado
2. Consolidación de tareo desde Módulo 08 (asistencia)
3. Ingesta de novedades:
   - Altas/bajas del período
   - Licencias, descansos médicos con CITT
   - Bonos variables aprobados
   - Préstamos y adelantos
4. Aplicación de estructura salarial vigente por trabajador
5. Ejecución del motor de cálculo por régimen (Strategy Pattern)
   - Cálculo de ingresos
   - Cálculo de aportes trabajador (AFP/ONP, renta 5ta)
   - Cálculo de aportes empleador (EsSalud, SCTR)
6. Aplicación de descuentos no previsionales (préstamos, judiciales, adelantos)
7. Generación de boletas (estado: CALCULATED)
8. Revisión por el administrador de RRHH
9. Aprobación por gerencia (estado: APPROVED)
10. Generación de:
    - Archivo PLAME (.txt Anexo 3)
    - Archivo T-Registro si hay altas/bajas
    - Archivo AFPnet (.xlsx 25 columnas por cada AFP)
    - Archivos de transferencia bancaria (BCP telecrédito, BBVA, Interbank, Scotiabank)
    - Provisiones contables (CTS, gratif, vacaciones devengadas)
11. Envío de boletas por email / disponibilidad en portal empleado
12. Ejecución de pagos
13. Cierre del período (estado: CLOSED) — bloqueo de edición
```

### 4.2 Flujo de liquidación por cese (48h máximo legal)
```
1. Módulo 03 registra el cese (renuncia, despido, mutuo disenso)
2. Motor calcula automáticamente:
   - Remuneración trunca del mes parcial
   - CTS trunca del semestre en curso
   - Gratificación trunca (si aplica)
   - Vacaciones truncas
   - Indemnización por despido arbitrario (si aplica): 1.5 rem/mes × años, tope 12
   - Horas extras pendientes
   - Utilidades si ya devengadas
   - Cualquier concepto pendiente del expediente
3. Aplicación de Renta 5ta (regularización por cese)
4. Descuentos pendientes (préstamos no amortizados, adelantos)
5. Generación del documento "Liquidación de Beneficios Sociales"
6. Generación del Certificado de Trabajo (Art. 45 LPCL)
7. Revisión por RRHH
8. Ejecución del pago vía transferencia
9. Generación de declaración rectificatoria T-Registro (baja)
10. Archivo en legajo digital del ex-trabajador
```

### 4.3 Flujo de recálculo retroactivo (reliquidación)
```
1. Evento externo: aumento salarial con efecto retroactivo / error detectado
2. Autorización por gerencia (estado: REOPENED del período afectado)
3. Replay del event stream desde el punto de cambio
4. Aplicación del nuevo evento (SalaryStructureUpdated con vigencia retroactiva)
5. Recálculo de todos los períodos afectados
6. Generación de "Reintegro" como concepto 0108 en el período actual
7. Ajuste de Renta 5ta (acumulado)
8. Archivo corregido de PLAME (declaración rectificatoria)
9. Boleta de reintegro generada para el trabajador
```

---

## 5. Integraciones críticas

| Integración | Propósito | Criticidad |
|-------------|-----------|------------|
| SUNAT - PDT PLAME | Validación y declaración mensual | CRÍTICA |
| SUNAT - T-Registro | Altas, bajas, modificaciones contractuales | CRÍTICA |
| AFPnet | Declaración y pago mensual SPP | CRÍTICA |
| SBS API | Actualización automática de tasas AFP | ALTA |
| Bancos (BCP, BBVA, Interbank, Scotiabank) | Archivos de pago masivo | ALTA |
| EsSalud - CITT electrónico | Validación de descansos médicos | ALTA |
| ZKTeco / Suprema biométricos | Marcaciones (vía Módulo 08) | MEDIA |
| Google/Microsoft email | Envío de boletas | MEDIA |
| Firma digital (Llama.pe, Digiflow) | Firma de boletas y liquidaciones | ALTA |

---

## 6. Exportadores oficiales — especificación técnica

### 6.1 Archivo PLAME (Anexo 3 SUNAT)
- Formato: `.txt` plano, delimitado por `|`
- Codificación: ASCII
- Estructura: 10 archivos (`PLANI.txt`, `JORNA.txt`, `DERECH.txt`, etc.)
- Archivo ZIP consolidado para carga masiva
- Validación obligatoria con PVS antes de envío

### 6.2 Archivo AFPnet
- Formato: `.xlsx`
- 25 columnas exactas en orden específico:
  1. CUSPP
  2. Tipo documento
  3. Número documento
  4. Apellido paterno
  5. Apellido materno
  6. Nombres
  7. Fecha nacimiento (dd/mm/aaaa)
  8. Sexo (M/F)
  9. Relación laboral existe (S/N)
  10. Inicio relación en período (dd/mm/aaaa o vacío)
  11. Término relación en período (dd/mm/aaaa o vacío)
  12. Días laborados
  13. Días subsidiados
  14. Días no laborados
  15. Motivo excepción aporte (S/L/C/P/O/vacío)
  16. Remuneración asegurable
  17. Aportes voluntarios con fin previsional
  18. Aportes voluntarios sin fin previsional
  19. Aporte empleador
  20. Aporte complementario Ley 27252 trabajador
  21. Aporte complementario Ley 27252 empleador
  22. Comisión flujo (si aplica)
  23. Comisión mixta (si aplica)
  24. Prima seguro
  25. Tipo trabajo (N/C/M/P)

> **Detalle completo:** → `normativa/N06_planilla_electronica_sunat.md`

---

## 7. Casos de uso frecuentes

### 7.1 "Trabajador cambia de AFP a mitad de mes"
- Registrar evento `PensionRegimeChanged(employee_id, from_afp, to_afp, effective_date)`
- Motor divide el mes en dos segmentos
- Aportes se calculan proporcionalmente y se declaran a ambas AFP
- PLAME refleja ambos períodos

### 7.2 "Trabajador con descanso médico de 45 días"
- Días 1-20: empleador paga y declara en PLAME
- Día 21 en adelante: subsidio EsSalud (empleador paga y recupera vía reembolso)
- CITT validado con EsSalud
- Aportes AFP se mantienen (la remuneración es base asegurable completa)
- CTS se computa normalmente (días subsidiados cuentan)

### 7.3 "Incremento salarial retroactivo 3 meses"
- Ver flujo 4.3 (recálculo retroactivo)
- Generar reintegro
- Rectificatoria PLAME de 3 períodos anteriores
- Ajuste de Renta 5ta proyectada

### 7.4 "Cambio de régimen de 728 a CAS" (sector público)
- Cese en 728 con liquidación completa
- Alta en CAS con nuevo contrato
- Tratamiento como dos relaciones laborales separadas

---

## 8. Pruebas obligatorias del motor

| Test | Descripción |
|------|-------------|
| Test matemático | Cálculo coincide con Excel validado por contador externo |
| Test PVS | Archivo PLAME pasa validación SUNAT sin errores |
| Test AFPnet | Archivo carga sin errores en portal AFPnet staging |
| Test regímenes cruzados | Trabajador que cambia régimen conserva historia correcta |
| Test retroactivo | Recálculo de 6 meses atrás produce mismos totales que cálculo fresh |
| Test de borde | RMV = 0 no debe permitirse; aportes mínimos calculados sobre RMV |
| Test tributario | Renta 5ta anual coincide con lo declarado al cese |
| Test de volumen | 10,000 boletas procesadas en <60 segundos |

---

## 9. KPIs del módulo
- Tiempo promedio de cierre mensual: <2 horas para 1000 trabajadores
- % archivos PLAME validados en primer intento: >99%
- % errores de cálculo detectados por el trabajador: <0.1%
- Tiempo de generación de liquidación por cese: <5 minutos

---

## 10. Referencias normativas
- [SUNAT - Tablas paramétricas](https://orientacion.sunat.gob.pe/7086-12-tablas-parametricas)
- [SUNAT - Tabla 22 Conceptos PLAME](https://orientacion.sunat.gob.pe/sites/default/files/inline-files/Tabla%20N22%20Definici%C3%B3n%20Conceptos%20Plame_011025.pdf)
- [SUNAT - Cartilla PDT PLAME](http://contenido.app.sunat.gob.pe/insc/PLAME/CARTILLA_PDT+PLAME_12FEB2013.pdf)
- [D.Leg. 728 - TUO (D.S. 003-97-TR)](https://infopublic.bpaprocorp.com/banco-de-leyes/decreto-supremo-003-97-tr)
- [EY Perú - CTS 2026](https://www.ey.com/es_pe/insights/workforce/cts)

---

## 11. Dependencias con otros MDs
- `normativa/N06_planilla_electronica_sunat.md` → Tablas paramétricas completas
- `normativa/N07_aportes_pensiones_salud.md` → AFP, ONP, EsSalud detalle
- `normativa/N08_beneficios_sociales.md` → CTS, gratif, vacaciones, utilidades
- `normativa/N09_renta_5ta_categoria.md` → algoritmo completo
- `arquitectura/A06_event_sourcing_payroll.md` → detalle técnico del event store
- `arquitectura/A07_strategy_regimenes.md` → implementación de todas las strategies
