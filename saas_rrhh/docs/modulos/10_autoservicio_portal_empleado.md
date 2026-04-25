# Módulo 10 — Portal del Empleado y App Móvil

> **Criticidad:** ALTA · **Tier:** Starter · **Dependencias:** todos los módulos (es la cara al usuario final)
>
> Es el **canal principal de contacto con el trabajador**. Un portal bien diseñado reduce 60-80% las consultas administrativas a RRHH y es factor de adopción clave.

---

## 1. Alcance

Portal web responsivo + App móvil nativa (iOS/Android) para autoservicio del colaborador. Acceso seguro con autenticación multi-factor.

---

## 2. Funcionalidades por dominio

### 2.1 Dashboard principal
- Resumen del colaborador (nombre, puesto, área, jefe)
- Próximos eventos (cumpleaños, aniversarios laborales, eventos institucionales)
- Alertas pendientes (docs por firmar, solicitudes por aprobar, encuestas)
- Saldos clave (vacaciones disponibles, días acumulados)
- Accesos rápidos

### 2.2 Mi perfil (datos personales)
- Visualización de datos personales
- Actualización de datos editables (dirección, teléfono, correo personal, estado civil, derechohabientes)
- Flujo de aprobación para cambios críticos (RRHH valida)
- Cambio de foto de perfil
- Consentimientos de datos personales (gestión Ley 29733)

### 2.3 Mis documentos
- Boletas de pago (descarga histórica)
- Certificados (trabajo, retenciones, CTS)
- Contrato y addendas
- Constancias varias (solicitables on-demand)
- Políticas con acuse de recibo pendiente
- Certificados de capacitación
- **Firma electrónica** de documentos

### 2.4 Mi tiempo
- Calendario personal de vacaciones/licencias
- **Solicitud de vacaciones** (con saldo visible, calendario del equipo)
- Solicitud de permisos (con/sin goce)
- Solicitud de licencias especiales (duelo, matrimonio, paternidad, etc.)
- Visualización de turnos asignados
- **Intercambio de turnos** con compañeros (si política lo permite)
- Solicitud de descanso médico (con carga de CITT)

### 2.5 Mi asistencia
- Marcación remota (con geofencing + reconocimiento facial si aplica)
- Historial de marcaciones
- Solicitud de regularización de marcación (olvidos)
- Horas extras registradas
- Tardanzas e inasistencias reportadas

### 2.6 Mi remuneración (con privacidad máxima)
- Boleta del mes actual
- Histórico de boletas
- Detalle del cálculo (conceptos, aportes, retenciones)
- Adelantos solicitables (si política activa)
- Préstamos vigentes (saldo, cuotas)
- Simulador de liquidación por cese
- Declaración de gastos deducibles Renta 5ta (3 UIT)

### 2.7 Mi desarrollo
- Mis objetivos/OKRs del ciclo
- Mi evaluación de desempeño (cuando esté visible)
- Cursos asignados y disponibles
- Ruta de aprendizaje personal
- Certificados obtenidos
- Feedback recibido
- 1-on-1s programados con mi jefe

### 2.8 Comunidad (feed institucional)
- Timeline de publicaciones de la organización
- Reconocimientos entre compañeros (P2P)
- Galería de eventos
- Anuncios importantes
- Cumpleaños del día
- Nuevos ingresos / promociones
- Reacciones y comentarios (moderados)

### 2.9 Beneficios
- Catálogo de convenios corporativos
- Descuentos disponibles
- Programas de bienestar activos
- Inscripciones a eventos

### 2.10 Canal de atención
- Ticketing con RRHH
- Chatbot para consultas frecuentes
- Sugerencias (buzón)
- Canal de denuncias (anónimo o identificado) — integración con Ley 27942
- Encuestas pulse periódicas

### 2.11 SST
- Reportar incidente/accidente
- Registrar acto o condición insegura
- Acceso a material de capacitación SST
- Ubicación de EPP y kits de emergencia
- Acceso al IPERC de mi puesto

### 2.12 Para jefes (módulo jefatura)
- Aprobaciones pendientes (vacaciones, horas extras, permisos)
- Tablero del equipo
- Calendario consolidado del equipo
- Evaluación de mis reportes directos
- Feedback 1-on-1s
- Métricas del equipo (ausentismo, rotación)

---

## 3. Arquitectura técnica

### 3.1 Stack
- **Web**: React/Next.js 14 (App Router) con SSR para performance
- **Mobile**: React Native (compartir código con web)
- **Auth**: OAuth 2.0 + OIDC con Keycloak / Auth0
- **MFA**: TOTP (Google Authenticator) + biometría (Touch ID, Face ID)
- **Push**: Firebase Cloud Messaging
- **Offline-first mobile**: datos críticos en local storage con sync al reconectar

### 3.2 Principios UX
- **Mobile-first**: la app móvil es primaria, no secundaria
- **Responsive web**: adaptación a tablet, desktop, móvil (el colaborador usa su dispositivo personal)
- **Accesibilidad**: WCAG 2.1 nivel AA (obligatorio sector público), soporte lectores de pantalla
- **Performance**: First Contentful Paint <1.5s, Time to Interactive <3s
- **Internacionalización**: español + lenguas originarias (quechua, aimara) para sector público

### 3.3 Seguridad
- HTTPS obligatorio (TLS 1.3)
- JWT con expiración corta (15 min) + refresh tokens (7 días)
- Rate limiting por usuario
- Session timeout inactivo (30 min)
- Cifrado local de datos sensibles en mobile
- Bloqueo de screenshots en vistas sensibles (boletas)
- Detección de jailbreak/root en móviles

### 3.4 Permission levels aplicados
- **Nivel 0 (empleado visible)**: sus propios datos no sensibles
- **Nivel 3 (jefe)**: información resumida de su equipo
- Datos sensibles (sueldo bruto de otros, médicos) nunca visibles en portal

---

## 4. Integraciones con todos los módulos

| Módulo | Qué expone al portal |
|--------|---------------------|
| M01 Políticas | Documentos con acuse de recibo |
| M02 Organización | Organigrama, mi puesto |
| M03 Empleo | Datos personales, legajo, solicitudes |
| M04 Compensación | Boletas, certificados, adelantos |
| M05 Capacitación | Cursos, rutas, certificados |
| M06 Desempeño | OKRs, evaluaciones, feedback |
| M07 RRHH Sociales | Feed, encuestas, denuncias, SST |
| M08 Asistencia | Marcación, vacaciones, permisos, turnos |
| M09 Disciplinario | (oculto — solo notificaciones formales) |
| M11 ATS | (portal externo de candidatos) |
| M12 Analytics | Dashboards personales del jefe |

---

## 5. App móvil — funcionalidades priorizadas

**Tier 1 (MVP mobile):**
- Login biométrico
- Marcación con geofencing
- Consulta de boleta
- Solicitud de vacaciones/permisos
- Feed institucional
- Notificaciones push

**Tier 2:**
- Firma electrónica de documentos
- Chat con RRHH
- Aprobaciones del jefe
- Encuestas pulse
- Reconocimientos entre compañeros

**Tier 3:**
- Capacitación microlearning
- Streaming de eventos institucionales
- Live chat colaborativo

---

## 6. Ejemplos de flujos clave en mobile

### 6.1 Marcación de entrada
```
1. Empleado abre app
2. Autenticación biométrica
3. App detecta ubicación (GPS)
4. Valida geofence del centro de trabajo
5. Solicita selfie con detección de vida
6. ML Kit / Rekognition valida contra foto de perfil
7. Registra marcación con timestamp + ubicación
8. Confirmación visual
```

### 6.2 Solicitud de vacaciones
```
1. Menú "Mi tiempo" → "Vacaciones"
2. Ve saldo disponible
3. Selecciona rango en calendario
4. Sistema muestra conflictos del equipo (opcional)
5. Agrega comentario
6. Envía solicitud
7. Push notification al jefe
8. Tracking del estado
9. Al aprobarse: notificación + calendario actualizado
```

---

## 7. Consideraciones especiales

### 7.1 Trabajadores sin smartphone (inclusión digital)
- Kioskos físicos en sedes (tablets compartidos)
- Resumen impreso disponible en RRHH
- Mensajes SMS para notificaciones críticas

### 7.2 Trabajadores en campo (minería, construcción)
- Modo offline robusto con sync diferido
- Reducción de data (imágenes optimizadas)
- Conectividad satelital integrada donde aplique

### 7.3 Sector público — enfoque intercultural
- UI en lenguas originarias (quechua, aimara, awajún, shipibo)
- Soporte a accesibilidad (Ley 29973)
- Contenido audiovisual en lengua de señas peruana

---

## 8. KPIs del módulo
- **Tasa de adopción**: % colaboradores que usan el portal/app al menos 1 vez/mes
- **Frecuencia de uso**: logins por colaborador/mes
- **Reducción de tickets RRHH**: % de consultas resueltas por autoservicio
- **Satisfacción del portal (NPS)**: eNPS específico del portal
- **Tiempo de respuesta a solicitudes**: promedio de aprobación
- **Errores de marcación biométrica**: % fallas falsas positivas/negativas
- **Uso mobile vs web**: distribución

---

## 9. Roadmap de implementación
1. **Fase 1**: Portal web con funcionalidades core (boletas, solicitudes, perfil)
2. **Fase 2**: App móvil con marcación + solicitudes + notificaciones
3. **Fase 3**: Feed social + reconocimientos + firma electrónica
4. **Fase 4**: Streaming + IA conversacional + marketplace beneficios

---

## 10. MDs relacionados
- Todos los módulos (este es el canal unificado)
- `arquitectura/A01_arquitectura_general.md`
- `arquitectura/A04_rbac_permisos.md`
- `normativa/N11_proteccion_datos_personales.md`
