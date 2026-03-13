# Módulo de Gestión de Vacaciones

## Descripción General

El módulo de gestión de vacaciones es un sistema completo que permite administrar los períodos vacacionales, solicitudes, aprobaciones y goces de vacaciones de los empleados, cumpliendo con la normativa laboral peruana.

## Características Principales

### 1. Gestión de Períodos Vacacionales
- **Generación automática**: Por cada año de servicio se generan 30 días de vacaciones
- **Múltiples períodos**: Un empleado puede tener varios récords según su antigüedad
- **Control de saldos**: Seguimiento de días generados, gozados y pendientes
- **Vencimiento**: Los períodos vencen 1 año después de su fecha límite

### 2. Solicitudes de Vacaciones
- **Numeración automática**: Formato VAC-YYYY-0001 (correlativo por año)
- **Tipos de solicitud**: Completa (30 días) o fraccionada (máximo 7 días)
- **Validaciones automáticas**:
  - Fraccionamiento máximo de 7 días
  - Inclusión automática de fines de semana si incluye viernes
  - Verificación de saldos disponibles
  - No solapamiento con solicitudes existentes

### 3. Flujo de Aprobación
- **Estados**: Borrador → Enviada → En Revisión → Aprobada/Rechazada
- **Aprobación por jefe**: El jefe del área debe aprobar las solicitudes
- **Historial completo**: Registro de todos los cambios de estado
- **Observaciones**: Tanto del empleado como del jefe revisor

### 4. Registro de Goces
- **Goces efectivos**: Registro de vacaciones realmente tomadas
- **Actualización automática**: Los saldos se actualizan automáticamente
- **Documentación**: Control de documentos de autorización
- **Tipos de goce**: Completo, fraccionado o medio día

## Estructura de Tablas

### Tabla: `periodos_vacacionales`
**Propósito**: Almacena los períodos vacacionales generados por cada año de servicio del empleado.

**Campos principales**:
- `empleado_id`: Referencia al empleado
- `anio_periodo`: Año del período vacacional
- `fecha_inicio_periodo`: Inicio del período (fecha ingreso + años)
- `fecha_fin_periodo`: Fin del período (un año después)
- `dias_generados`: Días generados (normalmente 30)
- `dias_gozados`: Días ya utilizados
- `dias_pendientes`: Días disponibles (calculado automáticamente)
- `fecha_vencimiento`: Fecha límite para usar las vacaciones

### Tabla: `solicitudes_vacaciones`
**Propósito**: Gestiona las solicitudes de vacaciones de los empleados.

**Campos principales**:
- `numero_solicitud`: Número correlativo automático
- `empleado_id`: Empleado solicitante
- `periodo_id`: Período vacacional a utilizar
- `tipo_solicitud`: Completa o fraccionada
- `fecha_inicio_solicitud` / `fecha_fin_solicitud`: Fechas solicitadas
- `dias_solicitados`: Número de días solicitados
- `incluye_fines_semana`: Si incluye sábado y domingo por normativa
- `estado_solicitud`: Estado actual de la solicitud
- `revisado_por_usuario_id`: Usuario que aprueba/rechaza

### Tabla: `goces_vacaciones`
**Propósito**: Registra las vacaciones efectivamente tomadas.

**Campos principales**:
- `solicitud_id`: Solicitud aprobada que origina el goce
- `fecha_inicio_goce` / `fecha_fin_goce`: Fechas reales del goce
- `dias_gozados`: Días efectivamente gozados
- `tipo_goce`: Completo, fraccionado o medio día
- `documento_autorizacion`: Documento que autoriza el goce

## Validaciones Implementadas

### 1. Fraccionamiento de Vacaciones
```sql
-- Validación: Máximo 7 días para fraccionamiento
IF v_diferencia_dias > 7 AND v_diferencia_dias < 30 THEN
    SET p_mensaje_error = 'Las vacaciones fraccionadas no pueden exceder 7 días';
END IF;
```

### 2. Inclusión de Fines de Semana
```sql
-- Si las vacaciones incluyen viernes, automáticamente incluyen sábado y domingo
SET p_incluye_fines_semana = fn_incluye_viernes(p_fecha_inicio, p_fecha_fin);
```

### 3. Verificación de Saldos
```sql
-- Buscar período con días disponibles suficientes
SELECT pv.periodo_id, pv.dias_pendientes
FROM periodos_vacacionales pv
WHERE pv.empleado_id = p_empleado_id
AND pv.estado_periodo = 'vigente'
AND pv.dias_pendientes >= p_dias_solicitados
```

### 4. No Solapamiento
```sql
-- Verificar que no hay solicitudes aprobadas en las mismas fechas
IF EXISTS (
    SELECT 1 FROM solicitudes_vacaciones sv
    WHERE sv.empleado_id = p_empleado_id
    AND sv.estado_solicitud IN ('aprobada', 'en_revision')
    AND (fechas se solapan)
) THEN
    SET p_mensaje_error = 'Ya tiene una solicitud para esas fechas';
END IF;
```

## Reportes Disponibles

### 1. Reporte de Saldos Vacacionales (`v_saldos_vacacionales`)
**Información incluida**:
- Datos del empleado (nombre, DNI, puesto, área)
- Períodos vacacionales (año, fechas, días generados/gozados/pendientes)
- Días para vencer
- Estado del período

**Filtros disponibles**:
- Por empleado específico
- Por área
- Por estado del empleado (activos/todos)
- Por año del período

### 2. Reporte de Solicitudes (`v_solicitudes_vacaciones`)
**Información incluida**:
- Datos de la solicitud (número, fechas, días)
- Información del empleado y área
- Estado de la solicitud
- Datos del revisor
- Observaciones

### 3. Reporte de Goces (`v_goces_vacaciones`)
**Información incluida**:
- Goces efectivos realizados
- Fechas reales de las vacaciones
- Documentos de autorización
- Tipo de goce realizado

## Casos de Uso Principales

### Caso 1: Empleado Consulta su Saldo
```sql
-- Consultar saldo vacacional actual
SELECT 
    anio_periodo,
    dias_generados,
    dias_gozados,
    dias_pendientes,
    fecha_vencimiento
FROM v_saldos_vacacionales 
WHERE numero_documento = '12345678'
AND estado_periodo = 'vigente'
ORDER BY anio_periodo;
```

### Caso 2: Empleado Solicita Vacaciones
```sql
-- Validar y crear solicitud
CALL sp_validar_solicitud_vacaciones(
    123, -- empleado_id
    '2024-07-15', -- fecha_inicio
    '2024-07-19', -- fecha_fin
    5, -- dias_solicitados
    @es_valida,
    @mensaje_error,
    @periodo_id,
    @incluye_fines_semana
);

-- Si es válida, insertar solicitud
IF @es_valida THEN
    INSERT INTO solicitudes_vacaciones (...) VALUES (...);
END IF;
```

### Caso 3: Jefe Aprueba Solicitud
```sql
-- Aprobar solicitud
UPDATE solicitudes_vacaciones 
SET estado_solicitud = 'aprobada',
    fecha_respuesta = NOW(),
    revisado_por_usuario_id = 456,
    observaciones_jefe = 'Aprobado'
WHERE solicitud_id = 789;
```

### Caso 4: Registrar Goce Efectivo
```sql
-- Registrar que el empleado efectivamente gozó las vacaciones
INSERT INTO goces_vacaciones (
    solicitud_id,
    empleado_id,
    periodo_id,
    fecha_inicio_goce,
    fecha_fin_goce,
    dias_gozados,
    tipo_goce
) VALUES (
    789, 123, 456, '2024-07-15', '2024-07-19', 5, 'fraccionado'
);
-- Los triggers actualizarán automáticamente el saldo del período
```

## Automatizaciones

### 1. Generación de Períodos
```sql
-- Generar períodos vacacionales para el año 2024
CALL sp_generar_periodos_vacacionales(2024);
```

### 2. Actualización Automática de Saldos
Los triggers `tr_actualizar_dias_gozados_*` actualizan automáticamente los días gozados en los períodos cuando se registran, modifican o eliminan goces.

### 3. Numeración Correlativa
El trigger `tr_generar_numero_solicitud` asigna automáticamente números correlativos a las solicitudes con formato VAC-YYYY-0001.

### 4. Historial de Estados
El trigger `tr_historial_estado_solicitud` registra automáticamente todos los cambios de estado en las solicitudes.

## Configuración del Módulo

La tabla `configuracion_vacaciones` permite ajustar parámetros del sistema:

- `dias_vacaciones_anuales`: 30 días por año
- `maximo_dias_fraccionamiento`: 7 días máximo
- `incluir_fines_semana_viernes`: true (incluir sábado y domingo si incluye viernes)
- `dias_anticipacion_solicitud`: 15 días mínimos de anticipación
- `anios_vencimiento_vacaciones`: 1 año para vencimiento
- `permitir_medio_dia`: true (permitir solicitudes de medio día)
- `requiere_aprobacion_jefe`: true (requiere aprobación del jefe)

## Permisos y Roles

### Empleado
- Ver módulo de vacaciones
- Solicitar vacaciones propias
- Ver solicitudes propias
- Ver saldos vacacionales propios

### Jefe de Área
- Todos los permisos de empleado
- Aprobar vacaciones del área
- Ver solicitudes del área

### Analista RRHH
- Todos los permisos anteriores
- Generar reportes de vacaciones
- Administrar períodos vacacionales
- Registrar goces de vacaciones

### Administrador RRHH
- Todos los permisos del módulo
- Configurar parámetros del módulo

## Ejemplo de Flujo Completo

### Escenario: Empleado con 3 años de servicio solicita vacaciones fraccionadas

1. **Estado inicial**:
   - Empleado ingresó el 15/03/2021
   - Tiene períodos: 2022-2023, 2023-2024, 2024-2025
   - Período 2023-2024: 30 días generados, 20 gozados, 10 pendientes

2. **Solicitud**:
   - Empleado solicita 5 días del 15/07/2024 al 19/07/2024
   - Sistema valida: ✓ Máximo 7 días, ✓ Saldo disponible, ✓ No solapamiento
   - Incluye viernes → Automáticamente incluye fin de semana

3. **Aprobación**:
   - Jefe del área revisa y aprueba la solicitud
   - Se registra en historial el cambio de estado

4. **Goce**:
   - Se registra el goce efectivo
   - Saldo del período se actualiza: 10 - 5 = 5 días pendientes

5. **Reporte**:
   - El empleado puede consultar su nuevo saldo
   - RRHH puede generar reportes del área

Este módulo proporciona una solución completa y robusta para la gestión de vacaciones, cumpliendo con todos los requerimientos normativos y de negocio especificados.