# N11. Protección de Datos Personales — Ley 29733 + D.S. 016-2024-JUS

> Marco de tratamiento de datos personales aplicable a todo SaaS en Perú. Obligaciones reforzadas tras el nuevo Reglamento vigente desde 30/03/2025.

---

## 1. Marco normativo

- **Ley N° 29733** (03/07/2011) — Ley de Protección de Datos Personales.
- **D.S. 003-2013-JUS** — Primer Reglamento (derogado).
- **D.S. 016-2024-JUS** — **Nuevo Reglamento vigente desde 30/03/2025**.
- **Directiva R.D. 100-2025-JUS/DGTAIPD** — Designación del Oficial de Datos Personales (ODP).
- Directivas ANPD (Autoridad Nacional de Protección de Datos Personales) complementarias.

El Perú armoniza progresivamente con el GDPR europeo y la LGPD brasileña.

---

## 2. Definiciones clave

### 2.1 Dato personal
Información numérica, alfabética, gráfica, fotográfica, acústica, sobre hábitos personales, o de cualquier otro tipo concerniente a personas naturales que las identifica o las hace identificables.

### 2.2 Dato sensible
Datos personales constituidos por:
- Datos biométricos que por sí mismos pueden identificar (huella, iris, rostro, voz).
- Datos referidos al origen racial y étnico.
- Ingresos económicos.
- Opiniones o convicciones políticas, religiosas, filosóficas o morales.
- Afiliación sindical.
- Información relacionada a la salud o a la vida sexual.

**El nuevo Reglamento extiende la noción a geolocalización** en contextos laborales y de supervisión.

### 2.3 Banco de datos personales
Conjunto organizado de datos personales, automatizado o no, estructurado para acceso, consulta o gestión.

### 2.4 Tratamiento
Cualquier operación sobre datos: recolección, registro, organización, almacenamiento, modificación, extracción, consulta, utilización, comunicación por transferencia, difusión, interconexión, supresión.

### 2.5 Titular
La persona natural a quien pertenecen los datos.

### 2.6 Responsable
Quien decide sobre el tratamiento (típicamente el empleador).

### 2.7 Encargado
Quien realiza el tratamiento por cuenta del responsable (típicamente el proveedor SaaS).

---

## 3. Principios rectores

Art. 4-11 Ley + Reglamento:

1. **Legalidad**: tratamiento con base legal.
2. **Consentimiento**: libre, previo, expreso, informado, inequívoco, **demostrable**.
3. **Finalidad**: propósito específico, lícito y conocido.
4. **Proporcionalidad**: solo los datos necesarios para la finalidad.
5. **Calidad**: datos exactos, actualizados.
6. **Seguridad**: medidas técnicas, organizativas y legales para proteger.
7. **Disposición de recurso**: el titular puede reclamar y accionar.
8. **Nivel adecuado de protección** en transferencias internacionales.
9. **Transparencia** (nuevo Reglamento 2024).
10. **Responsabilidad proactiva** / accountability (nuevo Reglamento 2024).

---

## 4. Consentimiento del titular

### 4.1 Características reforzadas por el Reglamento 2024

- **Libre**: sin coacción.
- **Previo**: antes del tratamiento.
- **Expreso**: manifestación clara (no tácita, no presunto).
- **Informado**: conoce finalidad, destinatarios, consecuencias.
- **Inequívoco**: sin duda sobre la voluntad.
- **Demostrable**: el responsable debe poder probar que lo obtuvo.

### 4.2 Para datos sensibles
Consentimiento **expreso y por escrito** (papel firmado o firma electrónica válida). No basta un checkbox.

### 4.3 Excepciones al consentimiento
- Ejecución de contrato laboral o comercial.
- Cumplimiento de obligación legal.
- Protección de la vida o integridad.
- Procedimiento administrativo o judicial.
- Interés público prevalente (estricta interpretación).

### 4.4 Revocación
El titular puede revocar el consentimiento en cualquier momento, sin efecto retroactivo.

---

## 5. Derechos ARCO + Portabilidad + No decisiones automatizadas

### 5.1 Derechos ARCO (clásicos)

| Derecho | Plazo respuesta |
|---|---|
| **Acceso** | 20 días hábiles |
| **Rectificación** | 10 días hábiles |
| **Cancelación** | 10 días hábiles |
| **Oposición** | 10 días hábiles |

### 5.2 Derechos adicionales (nuevo Reglamento)

- **Portabilidad**: recibir los datos en formato estructurado y común, y transmitirlos a otro responsable.
- **No ser objeto de decisiones automatizadas** sin intervención humana que produzcan efectos jurídicos o les afecten significativamente (inspirado en GDPR Art. 22).

---

## 6. Oficial de Datos Personales (ODP)

### 6.1 Obligatoriedad
Designación obligatoria para:
- Entidades de la Administración Pública.
- Responsables que realicen tratamiento de **datos sensibles a gran escala**.
- Responsables cuyo tratamiento requiera monitoreo sistemático y habitual a gran escala.

### 6.2 Rol
- Punto de contacto con la ANPD.
- Asesora al responsable en cumplimiento.
- Supervisa políticas internas.
- Supervisa la capacitación al personal.
- Coopera con la ANPD en inspecciones.

### 6.3 Designación
Mediante acto administrativo o resolución (según tipo de entidad). Registro ante la ANPD obligatorio (Directiva R.D. 100-2025-JUS/DGTAIPD).

### 6.4 Cualificaciones
- Conocimiento de la Ley 29733 y el Reglamento.
- Experiencia relevante (RR.HH., legal, TI, compliance).
- Independencia para ejercer sus funciones.

---

## 7. Medidas de seguridad — clasificación por nivel

El Reglamento define **4 niveles** según sensibilidad de los datos:

| Nivel | Tipo de datos | Medidas |
|---|---|---|
| **Básico** | Datos identificativos | Control de acceso, registro de usuarios |
| **Intermedio** | Datos económicos, laborales | + cifrado en tránsito, backups, logs |
| **Complejo** | Datos sensibles (salud, sindical, político) | + cifrado en reposo, controles estrictos, auditorías |
| **Crítico** | Datos biométricos, de salud detallados, menores | + HSM, llaves KMS, anonimización cuando posible, auditorías externas |

---

## 8. Obligaciones operativas del responsable

### 8.1 Registro de Bancos de Datos
- Declaración ante la ANPD de cada banco de datos personales con su finalidad, tipo, medidas, transferencias.
- Actualización cuando haya cambios.

### 8.2 Política de Privacidad
Documento público y difundido que contenga:
- Identidad del responsable.
- Finalidades del tratamiento.
- Categorías de datos.
- Destinatarios y transferencias.
- Plazos de conservación.
- Derechos del titular y cómo ejercerlos.
- Datos de contacto del ODP.

### 8.3 Acuerdo de Encargo
Contrato escrito con cada encargado (ej. proveedor SaaS) que defina:
- Objeto, duración, finalidad.
- Tipo de datos tratados.
- Obligaciones de confidencialidad.
- Medidas de seguridad.
- Subcontratación (permitida/no).
- Destino de los datos al término.

### 8.4 Notificación de brechas
**48 horas** para notificar a la ANPD brechas que afecten datos personales, con:
- Naturaleza de la brecha.
- Categorías y número de titulares afectados.
- Consecuencias probables.
- Medidas adoptadas.

Si afecta a datos sensibles o a gran número, también **notificar a los titulares afectados**.

### 8.5 Evaluación de Impacto (EIPD)
Obligatoria para tratamientos de **alto riesgo**:
- Uso masivo de biometría.
- Videovigilancia sistemática.
- Decisiones automatizadas con efecto significativo.
- Datos sensibles a gran escala.

---

## 9. Datos de empleados — obligaciones específicas

### 9.1 Biometría (huella, facial, iris)
- **Dato sensible** por definición.
- Requiere evaluación de proporcionalidad (¿hay alternativa menos invasiva?).
- Registro del banco de datos ante ANPD.
- Cifrado obligatorio.
- Imposibilidad de uso para finalidades distintas a la declarada.

### 9.2 Geolocalización (GPS en marcaciones, flotas)
- **Considerado dato sensible en contexto laboral** (nuevo Reglamento 2024).
- Solo durante la jornada laboral.
- Finalidad clara (control de asistencia, rutas de reparto).
- Informar al trabajador de alcance, tiempos, uso.
- EIPD obligatoria si es sistemática.

### 9.3 Videovigilancia
- Carteles visibles indicando la grabación.
- Prohibido en zonas de intimidad (baños, vestuarios, comedores cerrados).
- Retención máxima: **30-60 días** salvo causa justificada.
- No se usa para evaluación del desempeño ni sanciones disciplinarias sin aviso previo.

### 9.4 Monitoreo de correo y uso de TI
Requiere:
- Política escrita previa y conocida por el trabajador.
- Proporcionalidad (no leer contenidos sin justificación).
- Jurisprudencia TC: Exp. 03599-2010-PA y 00114-2011-PA (expectativa razonable de privacidad).

### 9.5 Historias clínicas ocupacionales
- Confidencialidad absoluta.
- Custodia del servicio médico ocupacional.
- Acceso restringido al trabajador titular y al médico.
- El empleador recibe solo **resultado de aptitud** (apto/no apto), no el detalle diagnóstico.

---

## 10. Transferencias internacionales

### 10.1 Regla general
Solo a países con **nivel adecuado de protección** (acreditado por la ANPD) o con **garantías suficientes** (cláusulas contractuales tipo, BCRs, consentimiento expreso del titular).

### 10.2 Excepciones
- Consentimiento expreso del titular.
- Contrato del titular.
- Cumplimiento de obligación legal.
- Protección de vida o integridad.

### 10.3 Para SaaS con infra en USA/Europa
Se requiere:
- Acuerdo de encargo con cláusulas estándar.
- Medidas de seguridad equivalentes.
- Evaluación de riesgos del país destino.

---

## 11. Sanciones

### 11.1 Infracciones leves
- 0.5 a 5 UIT.
- Ej.: falta de registro del banco, no actualizar política.

### 11.2 Infracciones graves
- 5 a 50 UIT.
- Ej.: tratamiento sin consentimiento, no atender derechos ARCO.

### 11.3 Infracciones muy graves
- 50 a 100 UIT.
- Ej.: tratamiento ilegítimo de datos sensibles, incumplimiento sistemático.

### 11.4 Tope
Hasta el **10% de ingresos brutos anuales** del ejercicio anterior, sin exceder 100 UIT por infracción.

### 11.5 Multa coercitiva
Hasta 10 UIT por cada omisión del mandato de la ANPD.

---

## 12. Impacto en el diseño del SaaS

### 12.1 Arquitectura
- **Multi-tenancy**: aislamiento lógico de tenants con RLS (ver A02).
- **Cifrado at-rest** obligatorio para datos sensibles (CCI, salud, biometría).
- **Cifrado en tránsito** (TLS 1.2+).
- **KMS por tenant** para clientes Enterprise/GovTech.
- **Permission Levels 0-9** para protección granular por campo (ver A04).
- **Audit log** completo (quién accede, qué, cuándo) — requisito normativo.

### 12.2 Funcionalidades obligatorias
- **Portal de derechos ARCO** para el empleado (solicitar acceso, rectificación, oposición).
- **Consentimiento demostrable**: checkbox + timestamp + IP + versión del aviso.
- **Política de privacidad** configurable por tenant con versionado.
- **Retención configurable** con purga automática al vencimiento.
- **Notificación de brechas** con workflow de 48h.
- **Evaluación de Impacto (EIPD)** como artefacto generable.

### 12.3 Rol ODP
- Dashboard específico del ODP con:
  - Inventario de bancos de datos del tenant.
  - Registro de incidentes.
  - Solicitudes ARCO pendientes.
  - Auditorías programadas.
  - Capacitaciones al personal.

### 12.4 Transferencia internacional
- Si el cliente aloja en región USA/Europa, se genera automáticamente el acuerdo de encargo con cláusulas tipo.
- Para GovTech la regla es **residencia datos Perú** obligatoria.

---

## 13. Responsabilidad compartida

El SaaS es **encargado**, el empleador es **responsable**. Obligaciones compartidas:

| Actividad | Responsable (empleador) | Encargado (SaaS) |
|---|---|---|
| Recolección del consentimiento | ✓ | Provee el mecanismo |
| Definición de finalidades | ✓ | — |
| Registro del banco ante ANPD | ✓ | Genera reportes |
| Designación de ODP | ✓ | Provee dashboard |
| Atención ARCO | ✓ | Provee workflow |
| Notificación de brechas | ✓ | Detecta y alerta |
| Seguridad técnica | Supervisa | ✓ |
| Cifrado, backups, monitoreo | Supervisa | ✓ |
| EIPD | ✓ | Provee plantilla |
| Capacitación al personal | ✓ | Provee cursos LMS |

---

## 14. Referencias oficiales

- [Ley 29733 actualizada](https://lpderecho.pe/ley-proteccion-datos-personales-ley-29733-actualizada/)
- [D.S. 016-2024-JUS (Reglamento vigente)](https://www.gob.pe/institucion/minjus/)
- [ANPD — Portal](https://www.gob.pe/minjus/autoridad-nacional-de-proteccion-de-datos-personales)
- [Directiva ODP R.D. 100-2025-JUS](https://busquedas.elperuano.pe/)

---

## 15. Checklist

- [ ] Política de Privacidad por tenant versionada
- [ ] Consentimiento demostrable con timestamp, IP y versión
- [ ] Bancos de datos declarables/registrables
- [ ] Portal ARCO funcional (acceso, rectificación, cancelación, oposición, portabilidad)
- [ ] ODP asignable con dashboard propio
- [ ] Cifrado at-rest para datos sensibles
- [ ] Cifrado en tránsito (TLS 1.2+) forzado
- [ ] Audit log completo con quién/qué/cuándo
- [ ] Permission levels 0-9 configurados para campos sensibles
- [ ] Retención y purga automática configurable
- [ ] Notificación de brechas con SLA 48h
- [ ] Plantillas de EIPD para tratamientos de alto riesgo
- [ ] Cláusulas tipo de transferencia internacional
- [ ] Residencia datos Perú obligatoria en GovTech
- [ ] Capacitaciones en LMS para todo el personal del cliente
