# A05. Campos Personalizados y Extensibilidad por Tenant

> Mecanismo que permite a cada cliente extender los DocTypes del sistema (agregar campos, reglas, validaciones) **sin fork de código**. Patrón metadata-driven inspirado en Frappe Custom Field + Custom DocType.

---

## 1. Problema que se resuelve

Dos tenants con el mismo plan pueden tener necesidades distintas:

- Una constructora necesita en el DocType "Empleado" los campos `nivel_calificacion_construccion_civil` (operario/oficial/peón), `sindicato_afiliado`, `hoja_vida_tecnica`.
- Un hospital necesita `colegio_profesional`, `cmp_vigente`, `rne_rtm`, `especialidad_medica`, `vacunas_requeridas`.
- Un municipio necesita `numero_resolucion_nombramiento`, `grupo_ocupacional_276`, `nivel_276`, `fecha_ultimo_ascenso`, `declaracion_jurada_bienes_vigente`.

Tres opciones de diseño evaluadas:

| Opción | Pros | Contras |
|---|---|---|
| **DDL dinámico** (ALTER TABLE al agregar campo) | Columnas reales, índices fáciles, queries nativos | Requiere privilegios DDL al tenant; locks en tablas grandes |
| **EAV** (Entity-Attribute-Value) | Cero DDL, máxima flexibilidad | Queries complejos, performance pobre en agregados |
| **JSONB** (columna JSON con índices GIN) | Balance: queries razonables + zero DDL | Menos performante que columnas nativas en agregados masivos |

**Recomendación**: **JSONB como default + DDL dinámico opcional para campos estratégicos** (los que se usan en reports masivos o cálculos de planilla).

---

## 2. Modelo de datos

### 2.1 Definición de campos personalizados por tenant

```sql
CREATE TABLE campo_personalizado (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  doctype VARCHAR(100) NOT NULL,              -- "Empleado", "Contrato", etc.
  codigo VARCHAR(100) NOT NULL,               -- ej. "nivel_calificacion_cc"
  etiqueta VARCHAR(200) NOT NULL,             -- label UI
  tipo_dato VARCHAR(30) NOT NULL,             -- string, int, decimal, date, datetime, boolean, link, table, select, attach
  longitud INT,                               -- para string
  precision SMALLINT,                         -- para decimal
  opciones TEXT,                              -- para select: valores separados por \n; para link: doctype destino
  obligatorio BOOLEAN DEFAULT false,
  unico BOOLEAN DEFAULT false,
  permlevel SMALLINT DEFAULT 0 CHECK (permlevel BETWEEN 0 AND 9),
  default_valor TEXT,
  descripcion TEXT,
  orden_ui INT DEFAULT 0,
  seccion_ui VARCHAR(100),                    -- agrupar en tabs/secciones
  -- Storage strategy
  almacenamiento VARCHAR(20) DEFAULT 'jsonb', -- 'jsonb' | 'ddl_column'
  nombre_columna_ddl VARCHAR(100),            -- si almacenamiento='ddl_column'
  -- Validación
  regex_validacion TEXT,
  min_valor NUMERIC,
  max_valor NUMERIC,
  formula_calculada TEXT,                     -- campo derivado (read-only)
  activo BOOLEAN DEFAULT true,
  creado_en TIMESTAMP DEFAULT NOW(),
  UNIQUE (tenant_id, doctype, codigo)
);
```

### 2.2 Tablas de negocio con columna `custom_fields` JSONB

```sql
ALTER TABLE empleados ADD COLUMN custom_fields JSONB DEFAULT '{}'::jsonb;

-- Índice GIN para búsquedas eficientes dentro del JSON
CREATE INDEX idx_empleados_custom_gin ON empleados USING GIN (custom_fields);

-- Índice específico para un campo crítico en búsquedas
CREATE INDEX idx_empleados_custom_dni_secundario
  ON empleados ((custom_fields ->> 'dni_conyuge'));
```

### 2.3 Ejemplo de uso

```sql
-- Tenant configura campo personalizado
INSERT INTO campo_personalizado (
  tenant_id, doctype, codigo, etiqueta, tipo_dato, opciones, obligatorio, permlevel
) VALUES (
  '11111111-...', 'Empleado',
  'grupo_ocupacional_276',
  'Grupo Ocupacional (DL 276)',
  'select',
  E'Profesional\nTécnico\nAuxiliar',
  true, 0
);

-- Empleado guardado con campo custom
INSERT INTO empleados (id, tenant_id, dni, nombres, custom_fields)
VALUES (
  gen_random_uuid(), '11111111-...',
  '12345678', 'Juan Pérez',
  '{"grupo_ocupacional_276": "Profesional", "nivel_276": "SPC"}'::jsonb
);

-- Query con filtro custom
SELECT nombres FROM empleados
WHERE tenant_id = '11111111-...'
  AND custom_fields @> '{"grupo_ocupacional_276": "Profesional"}';
```

---

## 3. Transición de JSONB a columna DDL real

Cuando un campo custom pasa a ser crítico (usado en reports masivos, cálculos de planilla, filtros frecuentes), se puede promoverlo a columna DDL real con una migración automatizada.

### 3.1 Procedimiento

```sql
-- 1. Agregar columna DDL nueva
ALTER TABLE empleados ADD COLUMN grupo_ocupacional_276 VARCHAR(20);

-- 2. Copiar datos desde JSON
UPDATE empleados
SET grupo_ocupacional_276 = custom_fields ->> 'grupo_ocupacional_276'
WHERE tenant_id = '11111111-...'
  AND custom_fields ? 'grupo_ocupacional_276';

-- 3. Actualizar metadata: cambiar almacenamiento del campo
UPDATE campo_personalizado
SET almacenamiento = 'ddl_column',
    nombre_columna_ddl = 'grupo_ocupacional_276'
WHERE tenant_id = '11111111-...'
  AND doctype = 'Empleado'
  AND codigo = 'grupo_ocupacional_276';

-- 4. Crear índice si aplica
CREATE INDEX idx_empleados_grupo_276
  ON empleados (tenant_id, grupo_ocupacional_276);

-- 5. Limpiar del JSONB
UPDATE empleados
SET custom_fields = custom_fields - 'grupo_ocupacional_276'
WHERE tenant_id = '11111111-...';
```

### 3.2 Estrategia de acceso unificada (ORM)

El ORM debe leer/escribir el valor desde el almacenamiento correcto de forma transparente para el desarrollador:

```python
class EmpleadoRepo:
    def get(self, empleado_id, usuario):
        row = db.query("SELECT * FROM empleados WHERE id = %s", empleado_id)
        custom_fields_def = cargar_definicion_campos(usuario.tenant_id, "Empleado")
        
        resultado = dict(row)
        for campo_def in custom_fields_def:
            if campo_def.almacenamiento == "ddl_column":
                resultado[campo_def.codigo] = row[campo_def.nombre_columna_ddl]
            elif campo_def.almacenamiento == "jsonb":
                resultado[campo_def.codigo] = (row["custom_fields"] or {}).get(campo_def.codigo)
        return filtrar_por_permlevel(resultado, usuario)
```

---

## 4. Custom DocTypes

Más allá de campos, un tenant puede necesitar **entidades nuevas**: "Acta de Comité Paritario", "Licencia CAS Especial", "Permuta Intersedes". Se ofrece un generador de DocTypes custom con límites:

- Tabla unificada `custom_doctype_record` con columna JSONB `datos` + discriminador `doctype_codigo`.
- Metadatos en `custom_doctype` (similar a `campo_personalizado` pero para la entidad completa).
- Vistas automáticas generadas en UI.
- Permisos heredan de los DocTypes base + overrides propios.

Esta opción se ofrece solo en tier Enterprise/GovTech porque añade complejidad operativa.

---

## 5. Fórmulas y campos calculados

Los campos `formula_calculada` son derivados (read-only para el usuario):

```json
{
  "codigo": "edad_calculada",
  "tipo_dato": "int",
  "formula_calculada": "DATE_DIFF(CURRENT_DATE, fecha_nacimiento, 'year')"
}
```

El motor evalúa la fórmula con el mismo engine seguro del módulo A03 (Workflows). Se ejecuta al leer el registro (o se materializa en un trigger si el campo se usa en búsquedas masivas).

---

## 6. Validaciones y reglas de negocio extensibles

Además de constraints simples (regex, min/max, obligatorio), el tenant puede declarar **reglas de validación** compuestas:

```json
{
  "doctype": "Contrato",
  "regla": "si_modalidad_obra_entonces_fecha_fin_obligatoria",
  "condicion_aplica": "tipo_contrato == 'obra_determinada'",
  "expresion_validacion": "fecha_fin != null AND fecha_fin > fecha_inicio",
  "mensaje_error": "Los contratos de obra determinada requieren fecha fin posterior al inicio"
}
```

El backend aplica estas reglas al guardar. Reglas críticas del sistema core (ej. "dni válido peruano") no pueden deshabilitarse; las del tenant sí.

---

## 7. Límites y gobernanza

Para prevenir abuso:

| Límite | Starter | Pro | Enterprise |
|---|---|---|---|
| Campos custom por DocType | 10 | 30 | 100 |
| Campos promovidos a DDL | 0 | 5 | ilimitado |
| Custom DocTypes nuevos | 0 | 3 | 20 |
| Reglas de validación por DocType | 5 | 20 | 100 |

Todo cambio se registra en `audit_log_metadata` y requiere rol `admin_configuracion` + aprobación dual para cambios destructivos (eliminación de campos con datos).

---

## 8. Checklist

- [ ] Todas las tablas de negocio tienen columna `custom_fields JSONB`
- [ ] Índice GIN en `custom_fields`
- [ ] Tabla `campo_personalizado` con metadatos
- [ ] ORM serializa/deserializa considerando ambos almacenamientos
- [ ] Validaciones (regex, min/max, obligatorio) aplicadas en backend
- [ ] Fórmulas calculadas evaluadas con motor seguro
- [ ] Editor UI drag-and-drop para campos custom por tenant
- [ ] Permisos separados para configurar metadatos vs. datos
- [ ] Procedimiento automatizado JSONB → DDL documentado
- [ ] Límites por plan aplicados por feature flag
