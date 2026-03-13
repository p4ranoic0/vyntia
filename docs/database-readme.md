# Base de Datos - Sistema de Intranet RRHH

## Descripción General

Este directorio contiene todos los scripts SQL organizados para el Sistema de Intranet de Recursos Humanos. Los archivos han sido reorganizados para facilitar el mantenimiento, desarrollo y despliegue del sistema.

## Estructura de Archivos

### 📋 Archivos Principales

| Archivo | Descripción | Propósito |
|---------|-------------|----------|
| `estructura-completa-bd.sql` | **Estructura completa de la base de datos** | Contiene todas las definiciones de tablas, índices, claves foráneas y constraints del sistema |
| `datos-demo.sql` | **Datos de demostración** | Incluye datos iniciales de configuración y ejemplos para pruebas del sistema |
| `funciones.sql` | **Funciones auxiliares** | Contiene funciones para cálculos y validaciones del sistema |
| `procedimientos.sql` | **Procedimientos almacenados** | Contiene todos los stored procedures del sistema |
| `triggers.sql` | **Triggers del sistema** | Incluye todos los triggers para automatización y auditoría |
| `vistas.sql` | **Vistas del sistema** | Contiene vistas para reportes y consultas optimizadas |

### 📁 Archivos Originales (Referencia)

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `bd-mejorada-sin-datos.sql` | 🔄 Referencia | Archivo original con estructura y datos iniciales |
| `modulo-vacaciones.sql` | 🔄 Referencia | Archivo original del módulo de vacaciones |
| `datos-ejemplo-vacaciones.sql` | 🔄 Referencia | Datos de ejemplo originales del módulo de vacaciones |

## 🚀 Orden de Ejecución

Para configurar la base de datos desde cero, ejecutar los archivos en el siguiente orden:

```sql
-- 1. Crear la estructura completa de la base de datos
SOURCE estructura-completa-bd.sql;

-- 2. Insertar datos de demostración y configuración inicial
SOURCE datos-demo.sql;

-- 3. Crear funciones auxiliares
SOURCE funciones.sql;

-- 4. Crear procedimientos almacenados
SOURCE procedimientos.sql;

-- 5. Crear triggers del sistema
SOURCE triggers.sql;

-- 6. Crear vistas del sistema
SOURCE vistas.sql;
```

## 📊 Módulos del Sistema

### 🏢 Módulo Principal (RRHH)
- **Empleados**: Gestión de información personal y laboral
- **Usuarios**: Sistema de autenticación y autorización
- **Áreas**: Estructura organizacional
- **Documentos**: Gestión de documentos digitales
- **Auditoría**: Registro de accesos y cambios

### 🏖️ Módulo de Vacaciones
- **Períodos Vacacionales**: Generación automática de períodos
- **Solicitudes**: Gestión de solicitudes de vacaciones
- **Goces**: Registro de vacaciones tomadas
- **Reportes**: Vistas para análisis y reportes

## 🗃️ Estructura de Tablas

### Tablas de Configuración
- `modulos` - Módulos del sistema
- `permisos` - Permisos disponibles
- `roles` - Roles de usuario
- `rol_permisos` - Asignación de permisos a roles

### Tablas de Empleados
- `areas` - Unidades organizacionales
- `empleados` - Información personal
- `datos_laborales` - Información laboral
- `datos_familiares` - Información familiar
- `datos_academicos` - Formación académica
- `historial_ubicaciones` - Historial de ubicaciones

### Tablas de Sistema
- `usuarios` - Usuarios del sistema
- `usuario_roles` - Asignación de roles
- `documentos_digitales` - Archivos digitales
- `auditoria_accesos` - Log de accesos
- `auditoria_cambios` - Log de cambios

### Tablas de Vacaciones
- `periodos_vacacionales` - Períodos de vacaciones
- `solicitudes_vacaciones` - Solicitudes de vacaciones
- `historial_solicitudes_vacaciones` - Historial de cambios
- `goces_vacaciones` - Registro de vacaciones tomadas
- `configuracion_vacaciones` - Configuración del módulo

## 🔧 Procedimientos Principales

### Módulo de Vacaciones
- `sp_generar_periodos_vacacionales()` - Genera períodos automáticamente
- `sp_validar_solicitud_vacaciones()` - Valida solicitudes
- `sp_aprobar_solicitud_vacaciones()` - Aprueba solicitudes
- `sp_rechazar_solicitud_vacaciones()` - Rechaza solicitudes
- `sp_registrar_goce_vacaciones()` - Registra goces
- `sp_actualizar_saldos_vacacionales()` - Actualiza saldos

### Módulo Administrativo
- `sp_crear_usuario_sistema()` - Crea usuarios
- `sp_registrar_auditoria_cambio()` - Registra auditoría

## 🎯 Triggers Implementados

### Módulo de Vacaciones
- `tr_actualizar_dias_gozados_*` - Actualiza días gozados automáticamente
- `tr_generar_numero_solicitud` - Genera números correlativos
- `tr_historial_estado_solicitud` - Registra cambios de estado

### Auditoría y Control
- `tr_auditoria_*_update` - Audita cambios en tablas principales
- `tr_validar_*` - Validaciones automáticas
- `tr_actualizar_ultimo_acceso` - Actualiza último acceso

## 📈 Vistas Principales

### Reportes de Vacaciones
- `v_saldos_vacacionales` - Saldos por empleado
- `v_solicitudes_vacaciones` - Solicitudes detalladas
- `v_goces_vacaciones` - Goces registrados
- `v_vacaciones_por_vencer` - Vacaciones próximas a vencer
- `v_solicitudes_pendientes` - Solicitudes pendientes

### Reportes Administrativos
- `v_empleados_activos` - Empleados activos
- `v_usuarios_sistema` - Usuarios del sistema
- `v_documentos_digitales` - Documentos registrados
- `v_auditoria_accesos` - Log de accesos

## 🔍 Funciones Auxiliares

- `fn_calcular_dias_habiles()` - Calcula días hábiles entre fechas
- `fn_incluye_viernes()` - Valida si incluye viernes en el rango
- `fn_calcular_anos_servicio()` - Calcula años de servicio del empleado
- `fn_siguiente_numero_documento()` - Genera números secuenciales

## 🛠️ Configuración de la Base de Datos

### Requisitos
- MySQL 8.0 o superior
- Charset: utf8mb4
- Collation: utf8mb4_unicode_ci

### Variables de Configuración
```sql
-- Configuración recomendada
SET GLOBAL sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO';
SET GLOBAL innodb_file_per_table = ON;
SET GLOBAL innodb_buffer_pool_size = 1G; -- Ajustar según recursos disponibles
```

## 📝 Notas de Mantenimiento

### Respaldos
- Realizar respaldos diarios de la base de datos
- Mantener respaldos de la estructura por separado
- Documentar cambios en el esquema

### Actualizaciones
- Probar cambios en ambiente de desarrollo
- Mantener scripts de migración versionados
- Documentar cambios en este README

### Monitoreo
- Revisar logs de auditoría regularmente
- Monitorear rendimiento de consultas
- Verificar integridad de datos periódicamente

## 🔗 Enlaces Útiles

- [Documentación MySQL](https://dev.mysql.com/doc/)
- [Mejores Prácticas SQL](https://dev.mysql.com/doc/refman/8.0/en/sql-mode.html)
- [Optimización de Consultas](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)

---

**Versión**: 2.0  
**Última actualización**: 2025  
**Mantenido por**: Equipo de Desarrollo RRHH