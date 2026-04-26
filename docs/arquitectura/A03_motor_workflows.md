# A03. Motor de Workflows Configurable

> Componente transversal que gobierna aprobaciones, enrutamientos y automatizaciones en todos los módulos (vacaciones, licencias, desplazamientos, sanciones, PAD, selección, contratos, etc.). Debe ser **declarativo, versionable y extensible por tenant** sin requerir despliegues de código.

---

## 1. Requisitos que impone el negocio

El motor debe resolver casos reales del sector público y privado peruano:

- **Aprobación de vacaciones** con cadenas L1 → L2 → L3 dependiendo del nivel del solicitante.
- **Desplazamiento de servidores públicos** (rotación, encargatura, destaque, comisión, designación, transferencia, permuta) con hasta 5 niveles de aprobación y validaciones legales (DL 276 / Ley 30057).
- **Procedimiento Administrativo Disciplinario (PAD)** con plazos legales estrictos (preliminar → instructiva → sancionadora → recursos) y tribunales internos.
- **Liquidación de beneficios sociales** con plazo legal 48 horas tras cese (SLA y alerta temprana).
- **Gestión de contratos** con validaciones de plazo máximo 5 años consolidado D.S. 003-97-TR.
- **Evaluaciones de desempeño** 90°/180°/360° con ciclos de feedback.
- **Selección de personal** con pipeline configurable (postulación → filtro → evaluación → entrevista → propuesta → contrato).

Ningún motor comercial "listo para usar" cubre este espectro sin adaptación profunda. Por eso se construye uno propio siguiendo el patrón de **Frappe Workflow** (declarativo, simple, suficiente) con extensión opcional a **Flowable / Camunda Zeebe** para flujos BPMN complejos.

---

## 2. Modelo de datos del motor

### 2.1 Entidades principales

```sql
-- Plantilla de workflow (Blueprint)
CREATE TABLE workflow_template (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  codigo VARCHAR(100) NOT NULL,           -- ej. "solicitud_vacaciones_728"
  nombre VARCHAR(200) NOT NULL,
  descripcion TEXT,
  doctype_objetivo VARCHAR(100),          -- a qué entidad aplica (Solicitud, Contrato, etc.)
  estado_inicial VARCHAR(50) NOT NULL,
  version INT NOT NULL DEFAULT 1,
  activo BOOLEAN NOT NULL DEFAULT true,
  creado_por UUID,
  creado_en TIMESTAMP DEFAULT NOW(),
  UNIQUE (tenant_id, codigo, version)
);

-- Estados del workflow (State Machine)
CREATE TABLE workflow_state (
  id UUID PRIMARY KEY,
  template_id UUID NOT NULL REFERENCES workflow_template(id),
  codigo VARCHAR(50) NOT NULL,            -- "borrador", "pendiente_jefe", "aprobado"
  nombre VARCHAR(200),
  tipo VARCHAR(20) NOT NULL,              -- inicial | intermedio | final | rechazo
  color VARCHAR(20),                      -- para UI (rojo, verde, amarillo, gris)
  es_editable BOOLEAN DEFAULT false,      -- ¿permite editar la solicitud?
  UNIQUE (template_id, codigo)
);

-- Transiciones entre estados
CREATE TABLE workflow_transition (
  id UUID PRIMARY KEY,
  template_id UUID NOT NULL REFERENCES workflow_template(id),
  estado_origen_id UUID REFERENCES workflow_state(id),
  estado_destino_id UUID REFERENCES workflow_state(id),
  accion VARCHAR(100) NOT NULL,           -- "aprobar", "rechazar", "devolver"
  etiqueta VARCHAR(200),                  -- label visible para el usuario
  orden INT DEFAULT 0,
  condicion JSONB,                        -- expresión declarativa opcional
  requiere_justificacion BOOLEAN DEFAULT false
);

-- Quién puede ejecutar una transición (RBAC + ABAC)
CREATE TABLE workflow_transition_actor (
  id UUID PRIMARY KEY,
  transition_id UUID NOT NULL REFERENCES workflow_transition(id),
  tipo_actor VARCHAR(30) NOT NULL,        -- "rol" | "posicion" | "jefe_directo" | "usuario_especifico"
  valor_actor VARCHAR(200) NOT NULL       -- "hr_admin" | "jefe_ugel_piura" | etc.
);

-- Acciones automáticas al cambiar de estado
CREATE TABLE workflow_action (
  id UUID PRIMARY KEY,
  template_id UUID NOT NULL REFERENCES workflow_template(id),
  estado_trigger_id UUID REFERENCES workflow_state(id),
  momento VARCHAR(20) NOT NULL,           -- "on_enter" | "on_exit" | "on_timeout"
  tipo_accion VARCHAR(50) NOT NULL,       -- email | notif | webhook | script | generar_doc
  configuracion JSONB NOT NULL,           -- parámetros específicos de la acción
  orden INT DEFAULT 0
);

-- SLA / plazos por estado (alertas y escalamiento)
CREATE TABLE workflow_sla (
  id UUID PRIMARY KEY,
  template_id UUID NOT NULL REFERENCES workflow_template(id),
  estado_id UUID NOT NULL REFERENCES workflow_state(id),
  plazo_horas INT NOT NULL,
  accion_al_vencer VARCHAR(50),           -- "escalar_nivel_superior" | "notificar" | "auto_aprobar"
  destinatario_escalamiento VARCHAR(200)
);
```

### 2.2 Instancias de workflow (Request / Solicitud)

```sql
-- Instancia concreta del workflow corriendo
CREATE TABLE workflow_instance (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  template_id UUID NOT NULL REFERENCES workflow_template(id),
  template_version INT NOT NULL,          -- snapshot de versión usada
  doctype VARCHAR(100) NOT NULL,          -- "SolicitudVacaciones"
  doc_id UUID NOT NULL,                   -- id del registro afectado
  estado_actual VARCHAR(50) NOT NULL,
  solicitante_id UUID NOT NULL,
  creado_en TIMESTAMP DEFAULT NOW(),
  finalizado_en TIMESTAMP,
  resultado VARCHAR(30),                  -- "aprobado" | "rechazado" | "cancelado"
  metadata JSONB DEFAULT '{}'::jsonb
);

-- Historial completo de cambios de estado (Event Sourcing ligero)
CREATE TABLE workflow_history (
  id UUID PRIMARY KEY,
  instance_id UUID NOT NULL REFERENCES workflow_instance(id),
  estado_origen VARCHAR(50),
  estado_destino VARCHAR(50) NOT NULL,
  accion_ejecutada VARCHAR(100) NOT NULL,
  actor_id UUID NOT NULL,
  actor_rol VARCHAR(100),
  justificacion TEXT,
  timestamp TIMESTAMP DEFAULT NOW(),
  metadata JSONB
);
```

---

## 3. Ejemplo concreto: Solicitud de vacaciones 728

### 3.1 Definición declarativa (JSON)

```json
{
  "codigo": "solicitud_vacaciones_728",
  "nombre": "Solicitud de Vacaciones - Régimen 728",
  "doctype_objetivo": "SolicitudVacaciones",
  "estado_inicial": "borrador",
  "estados": [
    {"codigo": "borrador", "tipo": "inicial", "es_editable": true},
    {"codigo": "pendiente_jefe", "tipo": "intermedio", "color": "amarillo"},
    {"codigo": "pendiente_rrhh", "tipo": "intermedio", "color": "amarillo"},
    {"codigo": "aprobado", "tipo": "final", "color": "verde"},
    {"codigo": "rechazado", "tipo": "rechazo", "color": "rojo"}
  ],
  "transiciones": [
    {
      "origen": "borrador", "destino": "pendiente_jefe", "accion": "enviar",
      "actores": [{"tipo": "rol", "valor": "empleado_solicitante"}],
      "condicion": {"campo": "dias_solicitados", "op": "<=", "valor": "dias_disponibles"}
    },
    {
      "origen": "pendiente_jefe", "destino": "pendiente_rrhh", "accion": "aprobar",
      "actores": [{"tipo": "jefe_directo"}]
    },
    {
      "origen": "pendiente_jefe", "destino": "rechazado", "accion": "rechazar",
      "actores": [{"tipo": "jefe_directo"}],
      "requiere_justificacion": true
    },
    {
      "origen": "pendiente_rrhh", "destino": "aprobado", "accion": "aprobar",
      "actores": [{"tipo": "rol", "valor": "rrhh_vacaciones"}]
    },
    {
      "origen": "pendiente_rrhh", "destino": "borrador", "accion": "devolver",
      "actores": [{"tipo": "rol", "valor": "rrhh_vacaciones"}],
      "requiere_justificacion": true
    }
  ],
  "acciones_automaticas": [
    {
      "estado_trigger": "pendiente_jefe", "momento": "on_enter",
      "tipo_accion": "email",
      "config": {"plantilla": "notificar_jefe_vacaciones", "destinatario": "jefe_directo"}
    },
    {
      "estado_trigger": "aprobado", "momento": "on_enter",
      "tipo_accion": "script",
      "config": {"funcion": "descontar_dias_vacaciones"}
    },
    {
      "estado_trigger": "aprobado", "momento": "on_enter",
      "tipo_accion": "generar_doc",
      "config": {"plantilla": "papeleta_vacaciones.pdf"}
    }
  ],
  "slas": [
    {"estado": "pendiente_jefe", "plazo_horas": 72, "accion_al_vencer": "escalar_nivel_superior"},
    {"estado": "pendiente_rrhh", "plazo_horas": 48, "accion_al_vencer": "notificar"}
  ]
}
```

---

## 4. Implementación del motor (Python / FastAPI)

### 4.1 Clase principal

```python
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

@dataclass
class WorkflowEngine:
    """Motor declarativo basado en State Machine."""
    
    def iniciar(self, template_codigo: str, doc_id: UUID, solicitante_id: UUID) -> UUID:
        """Crea una instancia nueva de workflow."""
        template = self._cargar_template(template_codigo)
        instance_id = self._crear_instance(
            template=template,
            doc_id=doc_id,
            solicitante_id=solicitante_id,
            estado=template.estado_inicial
        )
        self._ejecutar_acciones(instance_id, template.estado_inicial, momento="on_enter")
        return instance_id
    
    def ejecutar_transicion(
        self,
        instance_id: UUID,
        accion: str,
        actor_id: UUID,
        justificacion: Optional[str] = None,
        datos_adicionales: Optional[dict] = None
    ) -> str:
        """Aplica una transición si el actor tiene permisos y se cumplen condiciones."""
        instance = self._cargar_instance(instance_id)
        transicion = self._buscar_transicion(instance, accion)
        
        # 1. Validar actor
        if not self._actor_puede_ejecutar(actor_id, transicion):
            raise PermissionError(f"Usuario {actor_id} no puede ejecutar {accion}")
        
        # 2. Validar condición
        if transicion.condicion and not self._evaluar_condicion(instance, transicion.condicion):
            raise ValueError("Condición de transición no se cumple")
        
        # 3. Validar justificación requerida
        if transicion.requiere_justificacion and not justificacion:
            raise ValueError("Esta transición requiere justificación")
        
        # 4. Ejecutar acciones de salida del estado actual
        self._ejecutar_acciones(instance_id, instance.estado_actual, momento="on_exit")
        
        # 5. Cambiar estado (atómico)
        estado_anterior = instance.estado_actual
        self._actualizar_estado(instance_id, transicion.estado_destino)
        
        # 6. Registrar historia (event sourcing ligero)
        self._registrar_historia(
            instance_id=instance_id,
            origen=estado_anterior,
            destino=transicion.estado_destino,
            accion=accion,
            actor=actor_id,
            justificacion=justificacion
        )
        
        # 7. Ejecutar acciones de entrada al nuevo estado
        self._ejecutar_acciones(instance_id, transicion.estado_destino, momento="on_enter")
        
        # 8. Programar SLA si corresponde
        self._programar_sla(instance_id, transicion.estado_destino)
        
        return transicion.estado_destino
```

### 4.2 Evaluador de condiciones (expresiones seguras)

```python
import ast
import operator

OPERADORES_SEGUROS = {
    ast.Eq: operator.eq, ast.NotEq: operator.ne,
    ast.Lt: operator.lt, ast.LtE: operator.le,
    ast.Gt: operator.gt, ast.GtE: operator.ge,
    ast.And: operator.and_, ast.Or: operator.or_,
}

def evaluar_expresion_segura(expresion: str, contexto: dict) -> bool:
    """Evalúa expresiones como 'dias_solicitados <= dias_disponibles' sin exec()."""
    tree = ast.parse(expresion, mode="eval")
    return _eval_node(tree.body, contexto)

def _eval_node(node, ctx):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id not in ctx:
            raise ValueError(f"Variable no definida: {node.id}")
        return ctx[node.id]
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, ctx)
        for op, comparator in zip(node.ops, node.comparators):
            right = _eval_node(comparator, ctx)
            if not OPERADORES_SEGUROS[type(op)](left, right):
                return False
            left = right
        return True
    if isinstance(node, ast.BoolOp):
        results = [_eval_node(v, ctx) for v in node.values]
        return OPERADORES_SEGUROS[type(node.op)](*results) if len(results) == 2 else all(results)
    raise ValueError(f"Nodo no permitido: {type(node).__name__}")
```

---

## 5. Motor propio vs. Flowable/Camunda

| Criterio | Motor propio (Frappe-style) | Flowable/Camunda Zeebe |
|---|---|---|
| Complejidad curva | Baja | Alta (BPMN 2.0) |
| Cobertura casos | 80% de RRHH | 100% incluido BPMN riguroso |
| Infra adicional | Solo BD | JVM + motor BPMN separado |
| Licencia | Propia (MIT/Apache) | Flowable AGPL/EE; Camunda 8 no libre |
| Tiempo de desarrollo | 4-8 semanas | 2-3 semanas integración + aprendizaje |
| Casos donde vale la pena | Aprobaciones simples, cascadas, SLAs | Procesos multi-departamento con compensaciones, bifurcaciones paralelas, reintentos con backoff, timers complejos |

**Recomendación**: implementar **motor propio** como componente core del SaaS. Dejar abierto un adapter para **Flowable Community** (Apache 2.0) como plug-in opcional en tier Enterprise para procesos BPMN reales (onboarding complejo multi-departamento con dependencias externas).

---

## 6. Versionado de workflows

Un tema crítico: las plantillas evolucionan pero las instancias en vuelo deben terminar con la versión con la que iniciaron. Por eso `workflow_instance.template_version` guarda la versión usada. Cuando se modifica un template, se crea una nueva versión; las instancias antiguas siguen corriendo contra la versión anterior hasta finalizar.

---

## 7. Integración con otros módulos del SaaS

Todos los módulos relevantes declaran `workflow_templates` por defecto, y cada tenant puede sobrescribirlos:

| Módulo | Workflows típicos |
|---|---|
| 04 Compensación | Ajuste salarial, bono extraordinario, préstamo empleado |
| 05 Capacitación | Aprobación PDI, solicitud de capacitación externa, beca |
| 06 Rendimiento | Calibración 9-box, apelación de evaluación |
| 07 Relaciones Humanas | Queja laboral, solicitud intervención comité hostigamiento |
| 08 Control Asistencia | Justificación de tardanza/falta, solicitud vacaciones, licencia |
| 09 Procedimiento Disciplinario | PID (728), PAD (sector público) con 4 fases |
| 11 ATS | Pipeline de selección por etapas |

---

## 8. Checklist de implementación

- [ ] Modelo de datos creado con versionado
- [ ] Motor soporta condiciones, actores multi-tipo, acciones automáticas, SLAs
- [ ] Editor visual drag-and-drop para el tenant (UI configuración)
- [ ] Importar/exportar plantillas en JSON (marketplace interno)
- [ ] Pruebas con casos reales peruanos: PAD 4 fases, selección pública 6 etapas, vacaciones L1-L3
- [ ] Simulador de workflow (ver camino sin ejecutar transiciones reales)
- [ ] Dashboard de instancias en vuelo con SLAs en rojo
- [ ] Adapter opcional para Flowable Community
