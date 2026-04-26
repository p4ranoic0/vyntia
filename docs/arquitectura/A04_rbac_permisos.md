# A04. RBAC, Permission Levels y ABAC

> Sistema de permisos granular inspirado en Frappe (Permission Levels 0-9 por campo) + RBAC clásico + ABAC (Attribute-Based). Crítico para que un empleado vea su boleta sin ver la de otros, un jefe vea su equipo sin ver toda la empresa, y RRHH vea todo.

---

## 1. Por qué tres capas de permisos

Un solo modelo RBAC (rol → acción) es insuficiente para HR. Se necesitan tres capas combinables:

| Capa | Pregunta que responde | Ejemplo |
|---|---|---|
| **RBAC** (Role-Based) | ¿Este rol puede hacer esta acción sobre este recurso? | ¿"HR Admin" puede crear empleados? |
| **Permission Levels 0-9** (por campo) | Dentro de un registro permitido, ¿qué campos son visibles/editables? | Un empleado ve su boleta (level 0) pero no los descuentos administrativos (level 3) |
| **ABAC** (Attribute-Based) | ¿Este usuario puede actuar sobre este registro específico? | Un jefe solo aprueba vacaciones de SU equipo, no de otras áreas |

---

## 2. Modelo de datos RBAC

```sql
-- Roles
CREATE TABLE roles (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  codigo VARCHAR(100) NOT NULL,
  nombre VARCHAR(200) NOT NULL,
  descripcion TEXT,
  es_sistema BOOLEAN DEFAULT false,       -- roles core no eliminables
  UNIQUE (tenant_id, codigo)
);

-- Permisos (acción sobre doctype)
CREATE TABLE permisos (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  rol_id UUID NOT NULL REFERENCES roles(id),
  doctype VARCHAR(100) NOT NULL,          -- "Empleado", "Planilla", "Vacacion"
  accion VARCHAR(30) NOT NULL,            -- create | read | update | delete | approve | export
  permission_level SMALLINT DEFAULT 0 CHECK (permission_level BETWEEN 0 AND 9),
  condiciones JSONB,                      -- ABAC: restricciones adicionales
  UNIQUE (tenant_id, rol_id, doctype, accion, permission_level)
);

-- Asignación usuario-rol
CREATE TABLE usuario_rol (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  usuario_id UUID NOT NULL,
  rol_id UUID NOT NULL REFERENCES roles(id),
  alcance VARCHAR(50),                    -- "global" | "empresa" | "sede" | "area"
  alcance_valor VARCHAR(200),
  valido_desde TIMESTAMP DEFAULT NOW(),
  valido_hasta TIMESTAMP,
  UNIQUE (tenant_id, usuario_id, rol_id, alcance, alcance_valor)
);
```

### 2.1 Roles tipo sugeridos

| Rol | Alcance típico | Permisos clave |
|---|---|---|
| `super_admin` | Global tenant | Todo excepto datos cifrados de otros tenants |
| `rrhh_admin` | Empresa | CRUD empleados, ejecutar planilla, configurar workflows |
| `rrhh_compensacion` | Empresa | Ver/editar sueldos, CTS, gratificaciones |
| `rrhh_selec` | Empresa | ATS completo, sin acceso a sueldos vigentes |
| `rrhh_desarrollo` | Empresa | Capacitación, evaluaciones, planes de carrera |
| `rrhh_relaciones` | Empresa | SST, bienestar, clima, comunicación interna |
| `jefe_area` | Área/posición | Aprobar vacaciones y gastos de su equipo; ver desempeño |
| `gerente_general` | Empresa | Dashboards ejecutivos, aprobaciones L-final |
| `contador` | Empresa | Export PLAME, T-Registro, bancos; ver totales planilla |
| `empleado` | Propio | Ver/editar su perfil limitado, solicitar ausencias, ver sus boletas |
| `auditor_externo` | Solo lectura con timebox | Acceso temporal read-only a logs y planilla |

---

## 3. Permission Levels 0-9 por campo (patrón Frappe)

Dentro de cada DocType los campos se etiquetan con `permission_level` 0-9. El usuario ve/edita un campo solo si tiene permiso para ESE nivel específico en ese DocType.

### 3.1 Ejemplo para DocType "Empleado"

| Campo | Permission Level | Acceso |
|---|---|---|
| `codigo`, `nombres`, `apellidos`, `dni` | 0 | Empleado ve el suyo; jefes ven el de su equipo |
| `foto`, `email_corporativo`, `celular_corporativo` | 0 | idem |
| `fecha_nacimiento`, `direccion`, `estado_civil` | 1 | Sólo RRHH |
| `numero_cuenta_bancaria`, `cci` | 2 | Sólo RRHH Compensación |
| `sueldo_basico_actual`, `estructura_salarial_id` | 3 | Sólo RRHH Compensación + Gerencia |
| `resultado_evaluacion_desempeno` | 4 | Sólo RRHH Desarrollo + Jefe Directo |
| `condicion_salud`, `incapacidad`, `licencias_medicas` | 5 | Sólo RRHH + personal médico ocupacional |
| `antecedentes_disciplinarios`, `sanciones` | 6 | Sólo Comité Disciplinario + RRHH Relaciones |
| `observaciones_internas_confidenciales` | 7 | Sólo Gerencia General |
| `flag_riesgo_corrupcion` | 9 | Sólo auditoría interna de integridad |

### 3.2 Implementación en ORM

```python
# DocType con permission levels declarados en metadata
EMPLEADO_SCHEMA = {
    "doctype": "Empleado",
    "campos": [
        {"nombre": "codigo", "tipo": "str", "permlevel": 0},
        {"nombre": "nombres", "tipo": "str", "permlevel": 0},
        {"nombre": "dni", "tipo": "str", "permlevel": 0},
        {"nombre": "cci", "tipo": "str", "permlevel": 2, "cifrado": True},
        {"nombre": "sueldo_basico", "tipo": "decimal", "permlevel": 3},
        {"nombre": "condicion_salud", "tipo": "text", "permlevel": 5, "sensible": True},
    ]
}

def serializar_empleado(empleado: dict, usuario: Usuario) -> dict:
    """Devuelve solo campos que el usuario puede ver según permlevels."""
    niveles_permitidos = obtener_niveles_lectura(usuario, "Empleado")
    return {
        campo["nombre"]: empleado[campo["nombre"]]
        for campo in EMPLEADO_SCHEMA["campos"]
        if campo["permlevel"] in niveles_permitidos
    }

def puede_editar_campo(usuario: Usuario, doctype: str, campo: str) -> bool:
    schema = SCHEMA_REGISTRY[doctype]
    campo_def = next(c for c in schema["campos"] if c["nombre"] == campo)
    niveles = obtener_niveles_escritura(usuario, doctype)
    return campo_def["permlevel"] in niveles
```

---

## 4. ABAC — Restricciones contextuales

RBAC + permlevel responden "qué puede hacer el usuario", ABAC responde "sobre qué registros específicos". Se modela en el campo `condiciones` del permiso.

### 4.1 Ejemplos de condiciones

```json
// Jefe solo ve empleados de su área
{
  "doctype": "Empleado",
  "accion": "read",
  "condiciones": {
    "tipo": "ownership",
    "expresion": "empleado.area_id IN (SELECT area_id FROM usuario_areas WHERE usuario_id = :current_user)"
  }
}

// Contador solo exporta planilla de empresas a las que fue asignado
{
  "doctype": "Planilla",
  "accion": "export",
  "condiciones": {
    "tipo": "scope",
    "campo": "empresa_id",
    "valores_permitidos_query": "SELECT empresa_id FROM contadores_empresas WHERE contador_id = :current_user"
  }
}

// Auditor externo: solo lectura, solo últimos 90 días, solo módulos habilitados
{
  "doctype": "*",
  "accion": "read",
  "condiciones": {
    "tipo": "compuesta",
    "reglas": [
      {"campo": "fecha_creacion", "op": ">=", "valor": "NOW() - INTERVAL '90 days'"},
      {"campo": "modulo", "op": "IN", "valor": "${auditor.modulos_autorizados}"}
    ]
  }
}
```

### 4.2 Resolución de ABAC en query Postgres

Las condiciones ABAC se inyectan en el WHERE de la query ORM:

```python
def aplicar_filtros_abac(query, usuario, doctype, accion):
    permisos = obtener_permisos(usuario, doctype, accion)
    for permiso in permisos:
        if permiso.condiciones:
            where_clause = generar_where_desde_condicion(permiso.condiciones, usuario)
            query = query.where(text(where_clause))
    return query
```

---

## 5. Alcance (scope) del rol

Un mismo usuario puede tener el rol `jefe_area` en el Área de Sistemas y el rol `empleado` en otras. La tabla `usuario_rol` lleva `alcance` y `alcance_valor`:

| Alcance | Significado | Valor ejemplo |
|---|---|---|
| `global` | Todo el tenant | NULL |
| `empresa` | Una empresa del grupo | `empresa_id` |
| `sede` | Una sede específica | `sede_id` |
| `area` | Área/gerencia | `area_id` |
| `proyecto` | Proyecto temporal | `proyecto_id` |

---

## 6. Integración con RLS Postgres

El RBAC/ABAC de la aplicación se complementa con **Row-Level Security de Postgres** como defensa en profundidad. Aunque el código aplicativo pierda un filtro, la policy RLS bloquea la fuga cross-tenant (ver módulo A02).

Para el filtrado **dentro de un tenant** (ej. jefe solo ve su equipo), la estrategia es aplicar los filtros en la capa de query/ORM porque RLS no tiene contexto completo del usuario. Esto requiere disciplina: todo endpoint que devuelve listas DEBE pasar por la función `aplicar_filtros_abac`.

---

## 7. Auditoría de permisos

Todo cambio de permisos se registra en `audit_log_permisos`:

```sql
CREATE TABLE audit_log_permisos (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  timestamp TIMESTAMP DEFAULT NOW(),
  actor_id UUID NOT NULL,
  tipo_evento VARCHAR(50),                -- "rol_asignado" | "rol_removido" | "permiso_modificado"
  usuario_afectado_id UUID,
  detalle JSONB NOT NULL
);
```

Adicionalmente, vistas administrativas en el panel de seguridad:

- **Matriz de permisos efectivos por usuario**: expande roles y muestra cada DocType × acción × permlevel.
- **Informe de sobre-privilegio**: detecta usuarios con roles heredados que ya no aplican.
- **Control dual para acciones sensibles**: crear usuario administrador requiere aprobación de 2 súper-admins.

---

## 8. Casos especiales del sector público peruano

### 8.1 Régimen 276 — acceso a legajos físicos

Ley 27444 de Procedimiento Administrativo General obliga a mantener legajos individuales. Solo la Oficina de Recursos Humanos de la entidad y el propio servidor pueden acceder; Comité PAD en proceso abierto tiene acceso parcial con registro obligatorio.

### 8.2 CAS y transferencia de expedientes

El cambio de régimen (ej. CAS → Ley 30057) obliga a migrar expediente electrónico respetando derechos. El sistema debe preservar historial con los permlevels correctos y auditar cada migración.

### 8.3 Tribunal del Servicio Civil

El Tribunal tiene un rol propio de acceso: ver recursos de apelación + expediente disciplinario + evaluación de desempeño. **Solo lectura, con marca de agua y log acceso obligatorio**.

---

## 9. Checklist de seguridad

- [ ] Toda tabla de negocio sujeta a RBAC + RLS Postgres
- [ ] DocTypes críticos (Planilla, Empleado, Evaluación) con permlevel por campo
- [ ] Permisos ABAC para jefes de área (solo ven su equipo)
- [ ] Auditoría de todos los cambios de permisos y asignación de roles
- [ ] Principio de mínimo privilegio en roles por defecto
- [ ] Revisión semestral automática de permisos "durmientes" (sin uso 90 días)
- [ ] MFA obligatorio para roles `super_admin`, `rrhh_admin`, `gerente_general`
- [ ] Impersonación (acceso soporte) registrada con justificación y notificación al usuario afectado
- [ ] Break-glass procedure documentado para emergencias
