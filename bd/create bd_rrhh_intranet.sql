-- =====================================================
-- ESTRUCTURA DE BASE DE DATOS REFACTORIZADA PARA DJANGO
-- Sistema de Gestión de Recursos Humanos - Intranet
-- =====================================================
-- 
-- Este archivo contiene la estructura de base de datos refactorizada
-- para coincidir exactamente con los modelos Django del proyecto.
-- 
-- Fecha de creación: 2025-01-30
-- Versión: 2.0 (Refactorizada para Django)
-- =====================================================

-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS `bd_rrhh_intranet` 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

USE `bd_rrhh_intranet`;

-- =====================================================
-- TABLAS DEL SISTEMA DE AUTENTICACIÓN DJANGO
-- =====================================================

-- Tabla: auth_group (Django Auth Groups)
CREATE TABLE IF NOT EXISTS `auth_group` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(150) NOT NULL UNIQUE,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Grupos de autenticación de Django';

-- Tabla: auth_permission (Django Auth Permissions)
CREATE TABLE IF NOT EXISTS `auth_permission` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(255) NOT NULL,
    `content_type_id` int(11) NOT NULL,
    `codename` varchar(100) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`, `codename`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Permisos de autenticación de Django';

-- Tabla: django_content_type (Django Content Types)
CREATE TABLE IF NOT EXISTS `django_content_type` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `app_label` varchar(100) NOT NULL,
    `model` varchar(100) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`, `model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tipos de contenido de Django';

-- Tabla: django_migrations (Django Migrations)
CREATE TABLE IF NOT EXISTS `django_migrations` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `app` varchar(255) NOT NULL,
    `name` varchar(255) NOT NULL,
    `applied` datetime(6) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Historial de migraciones de Django';

-- Tabla: django_session (Django Sessions)
CREATE TABLE IF NOT EXISTS `django_session` (
    `session_key` varchar(40) NOT NULL,
    `session_data` longtext NOT NULL,
    `expire_date` datetime(6) NOT NULL,
    PRIMARY KEY (`session_key`),
    KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Sesiones de Django';

-- =====================================================
-- TABLAS DEL SISTEMA DE MÓDULOS
-- =====================================================

-- Tabla: modulos
-- Gestiona los módulos del sistema de intranet
CREATE TABLE IF NOT EXISTS `modulos` (
    `modulo_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del módulo',
    `nombre_modulo` varchar(100) NOT NULL COMMENT 'Nombre del módulo del sistema',
    `descripcion_modulo` text COMMENT 'Descripción detallada del módulo',
    `icono_modulo` varchar(100) DEFAULT NULL COMMENT 'Icono representativo del módulo',
    `ruta_modulo` varchar(200) DEFAULT NULL COMMENT 'Ruta de acceso al módulo',
    `orden_visualizacion` int(11) NOT NULL DEFAULT 0 COMMENT 'Orden de visualización en el menú',
    `estado_modulo` varchar(15) NOT NULL DEFAULT 'activo' COMMENT 'Estado del módulo (activo, inactivo, mantenimiento)',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del módulo',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`modulo_id`),
    KEY `modulos_nombre__2dcfd2_idx` (`nombre_modulo`),
    KEY `modulos_estado__d844f1_idx` (`estado_modulo`),
    KEY `modulos_orden_v_4e26cd_idx` (`orden_visualizacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Módulos del sistema de intranet';

-- =====================================================
-- TABLAS DEL SISTEMA DE ROLES Y PERMISOS
-- =====================================================

-- Tabla: rol
-- Gestiona los roles del sistema
CREATE TABLE IF NOT EXISTS `rol` (
    `rol_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del rol',
    `nombre_rol` varchar(100) NOT NULL UNIQUE COMMENT 'Nombre único del rol',
    `descripcion_rol` text COMMENT 'Descripción del rol y sus responsabilidades',
    `nivel_jerarquico` int(11) NOT NULL DEFAULT 1 COMMENT 'Nivel jerárquico del rol (1=más bajo)',
    `es_rol_sistema` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si es un rol del sistema (no modificable)',
    `estado_rol` varchar(10) NOT NULL DEFAULT 'activo' COMMENT 'Estado del rol (activo, inactivo)',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del rol',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`rol_id`),
    UNIQUE KEY `nombre_rol` (`nombre_rol`),
    KEY `rol_nombre__f7571c_idx` (`nombre_rol`),
    KEY `rol_estado__d844f1_idx` (`estado_rol`),
    KEY `rol_nivel_j_4e26cd_idx` (`nivel_jerarquico`),
    KEY `rol_es_rol__0b5e21_idx` (`es_rol_sistema`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Roles del sistema de autenticación';

-- Tabla: permiso
-- Gestiona los permisos específicos del sistema
CREATE TABLE IF NOT EXISTS `permiso` (
    `permiso_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del permiso',
    `nombre_permiso` varchar(100) NOT NULL COMMENT 'Nombre descriptivo del permiso',
    `descripcion_permiso` text COMMENT 'Descripción detallada del permiso',
    `modulo_id` int(11) NOT NULL COMMENT 'ID del módulo al que pertenece el permiso',
    `tipo_permiso` varchar(15) NOT NULL COMMENT 'Tipo de permiso (crear, leer, actualizar, eliminar, ejecutar, aprobar)',
    `estado_permiso` varchar(10) NOT NULL DEFAULT 'activo' COMMENT 'Estado del permiso (activo, inactivo)',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del permiso',
    PRIMARY KEY (`permiso_id`),
    KEY `permiso_nombre__2dcfd2_idx` (`nombre_permiso`),
    KEY `permiso_tipo_pe_d844f1_idx` (`tipo_permiso`),
    KEY `permiso_estado__d844f1_idx` (`estado_permiso`),
    KEY `permiso_modulo__4e26cd_idx` (`modulo_id`),
    CONSTRAINT `fk_permiso_modulo` FOREIGN KEY (`modulo_id`) REFERENCES `modulos` (`modulo_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Permisos específicos del sistema';

-- Tabla: rol_permisos
-- Tabla intermedia para la relación muchos a muchos entre roles y permisos
CREATE TABLE IF NOT EXISTS `rol_permisos` (
    `rol_permiso_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único de la asignación',
    `rol_id` int(11) NOT NULL COMMENT 'ID del rol',
    `permiso_id` int(11) NOT NULL COMMENT 'ID del permiso',
    `fecha_asignacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de asignación del permiso al rol',
    `asignado_por_usuario_id` int(11) DEFAULT NULL COMMENT 'ID del usuario que realizó la asignación',
    PRIMARY KEY (`rol_permiso_id`),
    UNIQUE KEY `rol_permisos_rol_id_permiso_id_unique` (`rol_id`, `permiso_id`),
    KEY `rol_permisos_rol_id_idx` (`rol_id`),
    KEY `rol_permisos_permiso_id_idx` (`permiso_id`),
    KEY `rol_permisos_fecha_asignacion_idx` (`fecha_asignacion`),
    CONSTRAINT `fk_rol_permisos_rol` FOREIGN KEY (`rol_id`) REFERENCES `rol` (`rol_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_rol_permisos_permiso` FOREIGN KEY (`permiso_id`) REFERENCES `permiso` (`permiso_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Asignación de permisos a roles';

-- =====================================================
-- TABLAS ORGANIZACIONALES
-- =====================================================

-- Tabla: area
-- Gestiona las áreas organizacionales de la institución
CREATE TABLE IF NOT EXISTS `area` (
    `area_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del área',
    `nombre_organo` varchar(150) NOT NULL DEFAULT 'SIN ESPECIFICAR' COMMENT 'Nombre del órgano organizacional',
    `nombre_unidad_organica` varchar(150) NOT NULL DEFAULT 'SIN ESPECIFICAR' COMMENT 'Nombre de la unidad orgánica',
    `siglas_area` varchar(20) NOT NULL UNIQUE DEFAULT 'TEMP' COMMENT 'Siglas únicas del área',
    `descripcion_area` text COMMENT 'Descripción detallada del área',
    `jefe_area` varchar(150) DEFAULT NULL COMMENT 'Nombre del jefe del área',
    `area_padre_id` int(11) DEFAULT NULL COMMENT 'ID del área padre (jerarquía)',
    `nivel_jerarquico` int(11) NOT NULL DEFAULT 1 COMMENT 'Nivel jerárquico del área',
    `codigo_presupuestal` varchar(20) DEFAULT NULL COMMENT 'Código presupuestal del área',
    `total_empleados` int(11) NOT NULL DEFAULT 0 COMMENT 'Total de empleados en el área',
    `estado_area` varchar(20) NOT NULL DEFAULT 'activa' COMMENT 'Estado del área (activa, inactiva, reestructuracion)',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del área',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`area_id`),
    UNIQUE KEY `siglas_area` (`siglas_area`),
    KEY `area_siglas_area_idx` (`siglas_area`),
    KEY `area_estado_area_idx` (`estado_area`),
    KEY `area_nombre_organo_idx` (`nombre_organo`),
    KEY `area_area_padre_idx` (`area_padre_id`),
    KEY `area_nivel_jerarquico_idx` (`nivel_jerarquico`),
    KEY `area_codigo_presupuestal_idx` (`codigo_presupuestal`),
    KEY `area_total_empleados_idx` (`total_empleados`),
    CONSTRAINT `fk_area_padre` FOREIGN KEY (`area_padre_id`) REFERENCES `area` (`area_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Áreas organizacionales de la institución';

-- =====================================================
-- TABLAS DE EMPLEADOS
-- =====================================================

-- Tabla: app_rrhh_empleado
-- Gestiona la información personal de los empleados
CREATE TABLE IF NOT EXISTS `app_rrhh_empleado` (
    `empleado_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del empleado',
    `numero_documento` varchar(20) NOT NULL UNIQUE COMMENT 'Número de documento de identidad',
    `tipo_documento` varchar(15) NOT NULL DEFAULT 'DNI' COMMENT 'Tipo de documento (DNI, CE, PASAPORTE, OTROS)',
    `nombres` varchar(100) NOT NULL COMMENT 'Nombres del empleado',
    `apellido_paterno` varchar(100) NOT NULL COMMENT 'Apellido paterno',
    `apellido_materno` varchar(100) NOT NULL COMMENT 'Apellido materno',
    `fecha_nacimiento` date DEFAULT NULL COMMENT 'Fecha de nacimiento',
    `genero` varchar(15) DEFAULT 'no_especifica' COMMENT 'Género (masculino, femenino, otro, no_especifica)',
    `estado_civil` varchar(15) DEFAULT 'soltero' COMMENT 'Estado civil',
    `nacionalidad` varchar(50) DEFAULT 'Peruana' COMMENT 'Nacionalidad',
    `telefono_personal` varchar(20) DEFAULT NULL COMMENT 'Teléfono personal',
    `telefono_trabajo` varchar(20) DEFAULT NULL COMMENT 'Teléfono de trabajo',
    `email_personal` varchar(254) DEFAULT NULL COMMENT 'Email personal',
    `email_institucional` varchar(254) DEFAULT NULL COMMENT 'Email institucional',
    `direccion_actual` text COMMENT 'Dirección actual de residencia',
    `distrito` varchar(100) DEFAULT NULL COMMENT 'Distrito de residencia',
    `provincia` varchar(100) DEFAULT NULL COMMENT 'Provincia de residencia',
    `departamento` varchar(100) DEFAULT NULL COMMENT 'Departamento de residencia',
    `codigo_postal` varchar(10) DEFAULT NULL COMMENT 'Código postal',
    `contacto_emergencia_nombre` varchar(200) DEFAULT NULL COMMENT 'Nombre del contacto de emergencia',
    `contacto_emergencia_telefono` varchar(20) DEFAULT NULL COMMENT 'Teléfono del contacto de emergencia',
    `contacto_emergencia_relacion` varchar(50) DEFAULT NULL COMMENT 'Relación con el contacto de emergencia',
    `numero_cuenta_bancaria` varchar(30) DEFAULT NULL COMMENT 'Número de cuenta bancaria',
    `banco` varchar(100) DEFAULT NULL COMMENT 'Banco de la cuenta',
    `numero_cci` varchar(30) DEFAULT NULL COMMENT 'Número CCI',
    `sistema_pensiones` varchar(30) DEFAULT 'ONP' COMMENT 'Sistema de pensiones',
    `cuspp` varchar(15) DEFAULT NULL COMMENT 'CUSPP para AFP',
    `tipo_comision` varchar(10) DEFAULT NULL COMMENT 'Tipo de comisión AFP (FLUJO, MIXTA)',
    `tipo_seguro` varchar(15) DEFAULT 'ESSALUD' COMMENT 'Tipo de seguro de salud',
    `eps_nombre` varchar(100) DEFAULT NULL COMMENT 'Nombre de EPS si aplica',
    `tipo_sangre` varchar(5) DEFAULT NULL COMMENT 'Tipo de sangre',
    `alergias` text COMMENT 'Alergias conocidas',
    `enfermedades_cronicas` text COMMENT 'Enfermedades crónicas',
    `medicamentos_actuales` text COMMENT 'Medicamentos que toma actualmente',
    `observaciones_medicas` text COMMENT 'Observaciones médicas adicionales',
    `foto_empleado` varchar(500) DEFAULT NULL COMMENT 'Ruta de la foto del empleado',
    `estado_empleado` varchar(15) NOT NULL DEFAULT 'activo' COMMENT 'Estado del empleado (activo, inactivo, licencia, vacaciones)',
    `fecha_ingreso_institucion` date DEFAULT NULL COMMENT 'Fecha de ingreso a la institución',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del registro',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`empleado_id`),
    UNIQUE KEY `numero_documento` (`numero_documento`),
    UNIQUE KEY `email_institucional` (`email_institucional`),
    KEY `empleado_nombres_idx` (`nombres`),
    KEY `empleado_apellido_paterno_idx` (`apellido_paterno`),
    KEY `empleado_tipo_documento_idx` (`tipo_documento`),
    KEY `empleado_estado_idx` (`estado_empleado`),
    KEY `empleado_fecha_ingreso_idx` (`fecha_ingreso_institucion`),
    KEY `empleado_genero_idx` (`genero`),
    KEY `empleado_sistema_pensiones_idx` (`sistema_pensiones`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Información personal de empleados';

-- =====================================================
-- TABLAS DE USUARIOS
-- =====================================================

-- Tabla: app_rrhh_usuario
-- Gestiona los usuarios del sistema (Django Custom User)
CREATE TABLE IF NOT EXISTS `app_rrhh_usuario` (
    `usuario_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del usuario',
    `password` varchar(128) NOT NULL COMMENT 'Contraseña encriptada',
    `last_login` datetime(6) DEFAULT NULL COMMENT 'Fecha del último login',
    `is_superuser` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si es superusuario',
    `username` varchar(150) NOT NULL UNIQUE COMMENT 'Nombre de usuario único',
    `email` varchar(254) NOT NULL UNIQUE COMMENT 'Email único del usuario',
    `nombres_usuario` varchar(100) NOT NULL COMMENT 'Nombres del usuario',
    `apellidos_usuario` varchar(100) NOT NULL COMMENT 'Apellidos del usuario',
    `tipo_usuario` varchar(20) NOT NULL COMMENT 'Tipo de usuario (administrador, rrhh, jefe, empleado, consulta, invitado)',
    `nivel_acceso` varchar(20) NOT NULL DEFAULT 'personal' COMMENT 'Nivel de acceso (total, departamental, personal, limitado, lectura)',
    `estado_usuario` varchar(15) NOT NULL DEFAULT 'activo' COMMENT 'Estado del usuario (activo, inactivo, suspendido, bloqueado, pendiente)',
    `intentos_fallidos` int(11) NOT NULL DEFAULT 0 COMMENT 'Número de intentos fallidos de login',
    `fecha_ultimo_acceso` datetime(6) DEFAULT NULL COMMENT 'Fecha del último acceso exitoso',
    `fecha_bloqueo` datetime(6) DEFAULT NULL COMMENT 'Fecha de bloqueo del usuario',
    `fecha_expiracion_password` date DEFAULT NULL COMMENT 'Fecha de expiración de la contraseña',
    `requiere_cambio_password` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si requiere cambio de contraseña',
    `token_recuperacion` varchar(100) DEFAULT NULL COMMENT 'Token para recuperación de contraseña',
    `fecha_expiracion_token` datetime(6) DEFAULT NULL COMMENT 'Fecha de expiración del token',
    `ip_ultimo_acceso` varchar(45) DEFAULT NULL COMMENT 'IP del último acceso',
    `user_agent_ultimo_acceso` text COMMENT 'User agent del último acceso',
    `configuracion_usuario` json DEFAULT NULL COMMENT 'Configuraciones personalizadas del usuario',
    `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Indica si el usuario está activo',
    `is_staff` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si puede acceder al admin de Django',
    `date_joined` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de registro del usuario',
    `empleado_id` int(11) DEFAULT NULL COMMENT 'ID del empleado asociado',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del usuario',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`usuario_id`),
    UNIQUE KEY `username` (`username`),
    UNIQUE KEY `email` (`email`),
    UNIQUE KEY `empleado_id` (`empleado_id`),
    KEY `usuario_tipo_usuario_idx` (`tipo_usuario`),
    KEY `usuario_estado_usuario_idx` (`estado_usuario`),
    KEY `usuario_nivel_acceso_idx` (`nivel_acceso`),
    KEY `usuario_fecha_ultimo_acceso_idx` (`fecha_ultimo_acceso`),
    KEY `usuario_is_active_idx` (`is_active`),
    KEY `usuario_is_staff_idx` (`is_staff`),
    CONSTRAINT `fk_usuario_empleado` FOREIGN KEY (`empleado_id`) REFERENCES `app_rrhh_empleado` (`empleado_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Usuarios del sistema de autenticación';

-- Tabla: usuario_roles
-- Tabla intermedia para la relación muchos a muchos entre usuarios y roles
CREATE TABLE IF NOT EXISTS `usuario_roles` (
    `usuario_rol_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único de la asignación',
    `usuario_id` int(11) NOT NULL COMMENT 'ID del usuario',
    `rol_id` int(11) NOT NULL COMMENT 'ID del rol',
    `fecha_asignacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de asignación del rol',
    `fecha_expiracion` datetime(6) DEFAULT NULL COMMENT 'Fecha de expiración del rol',
    `asignado_por_usuario_id` int(11) DEFAULT NULL COMMENT 'ID del usuario que realizó la asignación',
    `estado_asignacion` varchar(15) NOT NULL DEFAULT 'activo' COMMENT 'Estado de la asignación (activo, inactivo, suspendido, expirado)',
    PRIMARY KEY (`usuario_rol_id`),
    UNIQUE KEY `usuario_roles_usuario_id_rol_id_unique` (`usuario_id`, `rol_id`),
    KEY `usuario_rol_usuario_418f26_idx` (`usuario_id`),
    KEY `usuario_rol_rol_id_6b1e29_idx` (`rol_id`),
    KEY `usuario_rol_estado__ca8c4d_idx` (`estado_asignacion`),
    KEY `usuario_rol_fecha_expiracion_idx` (`fecha_expiracion`),
    CONSTRAINT `fk_usuario_roles_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_usuario_roles_rol` FOREIGN KEY (`rol_id`) REFERENCES `rol` (`rol_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_usuario_roles_asignado_por` FOREIGN KEY (`asignado_por_usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Asignación de roles a usuarios';

-- Tabla: app_rrhh_usuario_groups (Django Many-to-Many)
CREATE TABLE IF NOT EXISTS `app_rrhh_usuario_groups` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `usuario_id` int(11) NOT NULL,
    `group_id` int(11) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `app_rrhh_usuario_groups_usuario_id_group_id_unique` (`usuario_id`, `group_id`),
    KEY `app_rrhh_usuario_groups_usuario_id_idx` (`usuario_id`),
    KEY `app_rrhh_usuario_groups_group_id_idx` (`group_id`),
    CONSTRAINT `fk_usuario_groups_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_usuario_groups_group` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Grupos de Django asignados a usuarios';

-- Tabla: app_rrhh_usuario_user_permissions (Django Many-to-Many)
CREATE TABLE IF NOT EXISTS `app_rrhh_usuario_user_permissions` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `usuario_id` int(11) NOT NULL,
    `permission_id` int(11) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `app_rrhh_usuario_user_permissions_usuario_id_permission_id_unique` (`usuario_id`, `permission_id`),
    KEY `app_rrhh_usuario_user_permissions_usuario_id_idx` (`usuario_id`),
    KEY `app_rrhh_usuario_user_permissions_permission_id_idx` (`permission_id`),
    CONSTRAINT `fk_usuario_permissions_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_usuario_permissions_permission` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Permisos de Django asignados directamente a usuarios';

-- =====================================================
-- TABLAS DE DATOS LABORALES
-- =====================================================

-- Tabla: datos_laborales
-- Gestiona la información laboral de los empleados
CREATE TABLE IF NOT EXISTS `datos_laborales` (
    `datos_laborales_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único de los datos laborales',
    `empleado_id` int(11) NOT NULL COMMENT 'ID del empleado',
    `area_id` int(11) NOT NULL COMMENT 'ID del área de trabajo',
    `cargo_empleado` varchar(150) NOT NULL COMMENT 'Cargo del empleado',
    `nivel_cargo` varchar(50) DEFAULT NULL COMMENT 'Nivel del cargo',
    `tipo_empleado` varchar(30) NOT NULL DEFAULT 'PERMANENTE' COMMENT 'Tipo de empleado (PERMANENTE, CONTRATADO, PRACTICANTE, CONSULTOR)',
    `regimen_laboral` varchar(50) NOT NULL DEFAULT 'DL_728' COMMENT 'Régimen laboral',
    `modalidad_trabajo` varchar(30) DEFAULT 'PRESENCIAL' COMMENT 'Modalidad de trabajo (PRESENCIAL, REMOTO, HIBRIDO)',
    `jornada_laboral` varchar(30) DEFAULT 'COMPLETA' COMMENT 'Jornada laboral (COMPLETA, PARCIAL, FLEXIBLE)',
    `horario_entrada` time DEFAULT '08:00:00' COMMENT 'Horario de entrada',
    `horario_salida` time DEFAULT '17:00:00' COMMENT 'Horario de salida',
    `horas_semanales` decimal(5,2) DEFAULT 40.00 COMMENT 'Horas de trabajo por semana',
    `sueldo_basico` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Sueldo básico mensual',
    `asignacion_familiar` decimal(8,2) DEFAULT 0.00 COMMENT 'Asignación familiar',
    `bonificaciones` decimal(10,2) DEFAULT 0.00 COMMENT 'Bonificaciones adicionales',
    `otros_ingresos` decimal(10,2) DEFAULT 0.00 COMMENT 'Otros ingresos',
    `sueldo_bruto` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Sueldo bruto total',
    `descuentos_ley` decimal(10,2) DEFAULT 0.00 COMMENT 'Descuentos de ley',
    `otros_descuentos` decimal(10,2) DEFAULT 0.00 COMMENT 'Otros descuentos',
    `sueldo_neto` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Sueldo neto a pagar',
    `fecha_inicio_labores` date NOT NULL COMMENT 'Fecha de inicio de labores',
    `fecha_fin_labores` date DEFAULT NULL COMMENT 'Fecha de fin de labores',
    `estado_laboral` varchar(20) NOT NULL DEFAULT 'activo' COMMENT 'Estado laboral (activo, inactivo, licencia, vacaciones, cesado)',
    `observaciones_laborales` text COMMENT 'Observaciones sobre la situación laboral',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del registro',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`datos_laborales_id`),
    UNIQUE KEY `empleado_id` (`empleado_id`),
    KEY `datos_laborales_area_id_idx` (`area_id`),
    KEY `datos_laborales_cargo_idx` (`cargo_empleado`),
    KEY `datos_laborales_tipo_empleado_idx` (`tipo_empleado`),
    KEY `datos_laborales_estado_laboral_idx` (`estado_laboral`),
    KEY `datos_laborales_fecha_inicio_idx` (`fecha_inicio_labores`),
    KEY `datos_laborales_sueldo_basico_idx` (`sueldo_basico`),
    CONSTRAINT `fk_datos_laborales_empleado` FOREIGN KEY (`empleado_id`) REFERENCES `app_rrhh_empleado` (`empleado_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_datos_laborales_area` FOREIGN KEY (`area_id`) REFERENCES `area` (`area_id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Datos laborales de empleados';

-- =====================================================
-- TABLAS DE CONTRATOS Y ADENDAS
-- =====================================================

-- Tabla: contratos_adendas
-- Gestiona los contratos y adendas de los empleados
CREATE TABLE IF NOT EXISTS `contratos_adendas` (
    `contrato_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del contrato/adenda',
    `empleado_id` int(11) NOT NULL COMMENT 'ID del empleado',
    `numero_contrato` varchar(50) NOT NULL UNIQUE COMMENT 'Número único del contrato',
    `tipo_documento` varchar(20) NOT NULL DEFAULT 'CONTRATO' COMMENT 'Tipo de documento (CONTRATO, ADENDA, RENOVACION)',
    `tipo_contrato` varchar(30) NOT NULL COMMENT 'Tipo de contrato (INDEFINIDO, PLAZO_FIJO, OBRA_SERVICIO, PRACTICAS)',
    `modalidad_contrato` varchar(50) DEFAULT NULL COMMENT 'Modalidad específica del contrato',
    `objeto_contrato` text NOT NULL COMMENT 'Objeto o descripción del contrato',
    `fecha_inicio` date NOT NULL COMMENT 'Fecha de inicio del contrato',
    `fecha_fin` date DEFAULT NULL COMMENT 'Fecha de fin del contrato',
    `duracion_meses` int(11) DEFAULT NULL COMMENT 'Duración en meses',
    `duracion_dias` int(11) DEFAULT NULL COMMENT 'Duración en días',
    `sueldo_contrato` decimal(10,2) NOT NULL COMMENT 'Sueldo establecido en el contrato',
    `moneda` varchar(10) NOT NULL DEFAULT 'PEN' COMMENT 'Moneda del contrato',
    `lugar_trabajo` varchar(200) DEFAULT NULL COMMENT 'Lugar de trabajo especificado',
    `horario_trabajo` varchar(100) DEFAULT NULL COMMENT 'Horario de trabajo especificado',
    `periodo_prueba_dias` int(11) DEFAULT NULL COMMENT 'Días de período de prueba',
    `renovable` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si el contrato es renovable',
    `clausulas_especiales` text COMMENT 'Cláusulas especiales del contrato',
    `beneficios_adicionales` text COMMENT 'Beneficios adicionales acordados',
    `estado_contrato` varchar(20) NOT NULL DEFAULT 'vigente' COMMENT 'Estado del contrato (vigente, vencido, rescindido, suspendido)',
    `motivo_fin` varchar(100) DEFAULT NULL COMMENT 'Motivo de finalización del contrato',
    `archivo_contrato` varchar(500) DEFAULT NULL COMMENT 'Ruta del archivo del contrato',
    `firmado_empleado` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si fue firmado por el empleado',
    `fecha_firma_empleado` date DEFAULT NULL COMMENT 'Fecha de firma del empleado',
    `firmado_empleador` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si fue firmado por el empleador',
    `fecha_firma_empleador` date DEFAULT NULL COMMENT 'Fecha de firma del empleador',
    `usuario_creacion_id` int(11) DEFAULT NULL COMMENT 'ID del usuario que creó el registro',
    `usuario_modificacion_id` int(11) DEFAULT NULL COMMENT 'ID del usuario que modificó el registro',
    `observaciones` text COMMENT 'Observaciones adicionales',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del registro',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`contrato_id`),
    UNIQUE KEY `numero_contrato` (`numero_contrato`),
    KEY `contratos_empleado_id_idx` (`empleado_id`),
    KEY `contratos_tipo_documento_idx` (`tipo_documento`),
    KEY `contratos_tipo_contrato_idx` (`tipo_contrato`),
    KEY `contratos_estado_idx` (`estado_contrato`),
    KEY `contratos_fecha_inicio_idx` (`fecha_inicio`),
    KEY `contratos_fecha_fin_idx` (`fecha_fin`),
    KEY `contratos_sueldo_idx` (`sueldo_contrato`),
    CONSTRAINT `fk_contratos_empleado` FOREIGN KEY (`empleado_id`) REFERENCES `app_rrhh_empleado` (`empleado_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_contratos_usuario_creacion` FOREIGN KEY (`usuario_creacion_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE SET NULL,
    CONSTRAINT `fk_contratos_usuario_modificacion` FOREIGN KEY (`usuario_modificacion_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Contratos y adendas de empleados';

-- =====================================================
-- TABLAS DE HISTORIAL Y UBICACIONES
-- =====================================================

-- Tabla: historial_ubicaciones
-- Gestiona el historial de ubicaciones y movimientos de empleados
CREATE TABLE IF NOT EXISTS `historial_ubicaciones` (
    `historial_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del historial',
    `empleado_id` int(11) NOT NULL COMMENT 'ID del empleado',
    `area_origen_id` int(11) DEFAULT NULL COMMENT 'ID del área de origen',
    `area_destino_id` int(11) NOT NULL COMMENT 'ID del área de destino',
    `cargo_origen` varchar(150) DEFAULT NULL COMMENT 'Cargo de origen',
    `cargo_destino` varchar(150) NOT NULL COMMENT 'Cargo de destino',
    `tipo_movimiento` varchar(30) NOT NULL COMMENT 'Tipo de movimiento (INGRESO, TRASLADO, PROMOCION, ROTACION, CESE)',
    `motivo_movimiento` varchar(200) DEFAULT NULL COMMENT 'Motivo del movimiento',
    `fecha_movimiento` date NOT NULL COMMENT 'Fecha del movimiento',
    `fecha_efectiva` date NOT NULL COMMENT 'Fecha efectiva del movimiento',
    `sueldo_anterior` decimal(10,2) DEFAULT NULL COMMENT 'Sueldo anterior',
    `sueldo_nuevo` decimal(10,2) DEFAULT NULL COMMENT 'Sueldo nuevo',
    `documento_sustento` varchar(200) DEFAULT NULL COMMENT 'Documento que sustenta el movimiento',
    `archivo_documento` varchar(500) DEFAULT NULL COMMENT 'Ruta del archivo del documento',
    `observaciones_movimiento` text COMMENT 'Observaciones del movimiento',
    `autorizado_por_usuario_id` int(11) DEFAULT NULL COMMENT 'ID del usuario que autorizó',
    `estado_movimiento` varchar(20) NOT NULL DEFAULT 'efectivo' COMMENT 'Estado del movimiento (pendiente, efectivo, cancelado)',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del registro',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`historial_id`),
    KEY `historial_empleado_id_idx` (`empleado_id`),
    KEY `historial_area_origen_idx` (`area_origen_id`),
    KEY `historial_area_destino_idx` (`area_destino_id`),
    KEY `historial_tipo_movimiento_idx` (`tipo_movimiento`),
    KEY `historial_fecha_movimiento_idx` (`fecha_movimiento`),
    KEY `historial_estado_idx` (`estado_movimiento`),
    CONSTRAINT `fk_historial_empleado` FOREIGN KEY (`empleado_id`) REFERENCES `app_rrhh_empleado` (`empleado_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_historial_area_origen` FOREIGN KEY (`area_origen_id`) REFERENCES `area` (`area_id`) ON DELETE SET NULL,
    CONSTRAINT `fk_historial_area_destino` FOREIGN KEY (`area_destino_id`) REFERENCES `area` (`area_id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_historial_autorizado_por` FOREIGN KEY (`autorizado_por_usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Historial de ubicaciones y movimientos de empleados';

-- =====================================================
-- TABLAS DE DATOS FAMILIARES
-- =====================================================

-- Tabla: datos_familiares
-- Gestiona la información familiar de los empleados
CREATE TABLE IF NOT EXISTS `datos_familiares` (
    `familiar_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del familiar',
    `empleado_id` int(11) NOT NULL COMMENT 'ID del empleado',
    `numero_documento_familiar` varchar(20) NOT NULL COMMENT 'Número de documento del familiar',
    `tipo_documento_familiar` varchar(15) NOT NULL DEFAULT 'DNI' COMMENT 'Tipo de documento del familiar',
    `nombres_familiar` varchar(100) NOT NULL COMMENT 'Nombres del familiar',
    `apellido_paterno_familiar` varchar(100) NOT NULL COMMENT 'Apellido paterno del familiar',
    `apellido_materno_familiar` varchar(100) NOT NULL COMMENT 'Apellido materno del familiar',
    `fecha_nacimiento_familiar` date DEFAULT NULL COMMENT 'Fecha de nacimiento del familiar',
    `genero_familiar` varchar(15) DEFAULT 'no_especifica' COMMENT 'Género del familiar',
    `relacion_familiar` varchar(30) NOT NULL COMMENT 'Relación con el empleado (CONYUGE, HIJO, PADRE, MADRE, HERMANO, etc.)',
    `estado_civil_familiar` varchar(15) DEFAULT 'soltero' COMMENT 'Estado civil del familiar',
    `nivel_educativo` varchar(50) DEFAULT NULL COMMENT 'Nivel educativo del familiar',
    `ocupacion_familiar` varchar(100) DEFAULT NULL COMMENT 'Ocupación del familiar',
    `telefono_familiar` varchar(20) DEFAULT NULL COMMENT 'Teléfono del familiar',
    `email_familiar` varchar(254) DEFAULT NULL COMMENT 'Email del familiar',
    `direccion_familiar` text COMMENT 'Dirección del familiar',
    `es_dependiente` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si es dependiente económico',
    `es_beneficiario_seguro` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si es beneficiario del seguro',
    `porcentaje_beneficio` decimal(5,2) DEFAULT NULL COMMENT 'Porcentaje de beneficio (para seguros/pensiones)',
    `es_contacto_emergencia` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si es contacto de emergencia',
    `observaciones_familiar` text COMMENT 'Observaciones adicionales del familiar',
    `estado_registro` varchar(15) NOT NULL DEFAULT 'activo' COMMENT 'Estado del registro (activo, inactivo)',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del registro',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`familiar_id`),
    KEY `datos_familiares_empleado_id_idx` (`empleado_id`),
    KEY `datos_familiares_numero_documento_idx` (`numero_documento_familiar`),
    KEY `datos_familiares_relacion_idx` (`relacion_familiar`),
    KEY `datos_familiares_es_dependiente_idx` (`es_dependiente`),
    KEY `datos_familiares_es_beneficiario_idx` (`es_beneficiario_seguro`),
    KEY `datos_familiares_estado_idx` (`estado_registro`),
    CONSTRAINT `fk_datos_familiares_empleado` FOREIGN KEY (`empleado_id`) REFERENCES `app_rrhh_empleado` (`empleado_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Datos familiares de empleados';

-- =====================================================
-- TABLAS DE DATOS ACADÉMICOS
-- =====================================================

-- Tabla: datos_academicos
-- Gestiona la información académica de los empleados
CREATE TABLE IF NOT EXISTS `datos_academicos` (
    `academico_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del registro académico',
    `empleado_id` int(11) NOT NULL COMMENT 'ID del empleado',
    `nivel_educativo` varchar(50) NOT NULL COMMENT 'Nivel educativo (PRIMARIA, SECUNDARIA, TECNICO, UNIVERSITARIO, POSTGRADO)',
    `grado_academico` varchar(50) DEFAULT NULL COMMENT 'Grado académico específico',
    `institucion_educativa` varchar(200) NOT NULL COMMENT 'Nombre de la institución educativa',
    `carrera_especialidad` varchar(150) DEFAULT NULL COMMENT 'Carrera o especialidad estudiada',
    `titulo_obtenido` varchar(200) DEFAULT NULL COMMENT 'Título obtenido',
    `fecha_inicio_estudios` date DEFAULT NULL COMMENT 'Fecha de inicio de estudios',
    `fecha_fin_estudios` date DEFAULT NULL COMMENT 'Fecha de fin de estudios',
    `fecha_graduacion` date DEFAULT NULL COMMENT 'Fecha de graduación',
    `estado_estudios` varchar(20) NOT NULL DEFAULT 'completo' COMMENT 'Estado de estudios (completo, incompleto, en_curso, abandonado)',
    `pais_estudios` varchar(50) DEFAULT 'Perú' COMMENT 'País donde realizó los estudios',
    `ciudad_estudios` varchar(100) DEFAULT NULL COMMENT 'Ciudad donde realizó los estudios',
    `modalidad_estudios` varchar(30) DEFAULT 'presencial' COMMENT 'Modalidad de estudios (presencial, virtual, semipresencial)',
    `numero_registro_titulo` varchar(50) DEFAULT NULL COMMENT 'Número de registro del título',
    `colegio_profesional` varchar(100) DEFAULT NULL COMMENT 'Colegio profesional al que pertenece',
    `numero_colegiatura` varchar(30) DEFAULT NULL COMMENT 'Número de colegiatura',
    `fecha_colegiatura` date DEFAULT NULL COMMENT 'Fecha de colegiatura',
    `estado_colegiatura` varchar(20) DEFAULT NULL COMMENT 'Estado de la colegiatura (habilitado, inhabilitado)',
    `archivo_titulo` varchar(500) DEFAULT NULL COMMENT 'Ruta del archivo del título',
    `archivo_certificado` varchar(500) DEFAULT NULL COMMENT 'Ruta del archivo del certificado',
    `observaciones_academicas` text COMMENT 'Observaciones adicionales',
    `validado` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si la información fue validada',
    `fecha_validacion` datetime(6) DEFAULT NULL COMMENT 'Fecha de validación',
    `validado_por_usuario_id` int(11) DEFAULT NULL COMMENT 'ID del usuario que validó',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del registro',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`academico_id`),
    KEY `datos_academicos_empleado_id_idx` (`empleado_id`),
    KEY `datos_academicos_nivel_educativo_idx` (`nivel_educativo`),
    KEY `datos_academicos_institucion_idx` (`institucion_educativa`),
    KEY `datos_academicos_estado_estudios_idx` (`estado_estudios`),
    KEY `datos_academicos_validado_idx` (`validado`),
    CONSTRAINT `fk_datos_academicos_empleado` FOREIGN KEY (`empleado_id`) REFERENCES `app_rrhh_empleado` (`empleado_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_datos_academicos_validado_por` FOREIGN KEY (`validado_por_usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Datos académicos de empleados';

-- =====================================================
-- TABLAS DE DOCUMENTOS DIGITALES
-- =====================================================

-- Tabla: documentos_digitales
-- Gestiona los documentos digitales de los empleados
CREATE TABLE IF NOT EXISTS `documentos_digitales` (
    `documento_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del documento',
    `empleado_id` int(11) NOT NULL COMMENT 'ID del empleado',
    `tipo_documento` varchar(50) NOT NULL COMMENT 'Tipo de documento (CV, TITULO, CERTIFICADO, CONTRATO, etc.)',
    `categoria_documento` varchar(50) DEFAULT NULL COMMENT 'Categoría del documento',
    `nombre_documento` varchar(200) NOT NULL COMMENT 'Nombre del documento',
    `descripcion_documento` text COMMENT 'Descripción del documento',
    `ruta_archivo` varchar(500) NOT NULL COMMENT 'Ruta del archivo en el sistema',
    `nombre_archivo_original` varchar(255) NOT NULL COMMENT 'Nombre original del archivo',
    `extension_archivo` varchar(10) NOT NULL COMMENT 'Extensión del archivo',
    `tamaño_archivo` bigint(20) NOT NULL COMMENT 'Tamaño del archivo en bytes',
    `hash_archivo` varchar(64) DEFAULT NULL COMMENT 'Hash MD5 del archivo para verificación',
    `version_documento` int(11) NOT NULL DEFAULT 1 COMMENT 'Versión del documento',
    `es_version_actual` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Indica si es la versión actual',
    `fecha_documento` date DEFAULT NULL COMMENT 'Fecha del documento',
    `fecha_vencimiento` date DEFAULT NULL COMMENT 'Fecha de vencimiento del documento',
    `estado_documento` varchar(20) NOT NULL DEFAULT 'activo' COMMENT 'Estado del documento (activo, inactivo, vencido, reemplazado)',
    `confidencial` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si el documento es confidencial',
    `requiere_aprobacion` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si requiere aprobación',
    `aprobado` tinyint(1) DEFAULT NULL COMMENT 'Estado de aprobación (NULL=pendiente, 0=rechazado, 1=aprobado)',
    `fecha_aprobacion` datetime(6) DEFAULT NULL COMMENT 'Fecha de aprobación',
    `aprobado_por_usuario_id` int(11) DEFAULT NULL COMMENT 'ID del usuario que aprobó',
    `observaciones_aprobacion` text COMMENT 'Observaciones de la aprobación',
    `subido_por_usuario_id` int(11) NOT NULL COMMENT 'ID del usuario que subió el documento',
    `tags_documento` text COMMENT 'Tags del documento separados por comas',
    `metadatos_adicionales` json DEFAULT NULL COMMENT 'Metadatos adicionales en formato JSON',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del registro',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`documento_id`),
    KEY `documentos_empleado_id_idx` (`empleado_id`),
    KEY `documentos_tipo_documento_idx` (`tipo_documento`),
    KEY `documentos_categoria_idx` (`categoria_documento`),
    KEY `documentos_estado_idx` (`estado_documento`),
    KEY `documentos_fecha_vencimiento_idx` (`fecha_vencimiento`),
    KEY `documentos_confidencial_idx` (`confidencial`),
    KEY `documentos_aprobado_idx` (`aprobado`),
    KEY `documentos_version_actual_idx` (`es_version_actual`),
    CONSTRAINT `fk_documentos_empleado` FOREIGN KEY (`empleado_id`) REFERENCES `app_rrhh_empleado` (`empleado_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_documentos_subido_por` FOREIGN KEY (`subido_por_usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_documentos_aprobado_por` FOREIGN KEY (`aprobado_por_usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Documentos digitales de empleados';

-- =====================================================
-- TABLAS DEL MÓDULO DE VACACIONES
-- =====================================================

-- Tabla: periodos_vacacionales
-- Gestiona los períodos vacacionales de los empleados
CREATE TABLE IF NOT EXISTS `periodos_vacacionales` (
    `periodo_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del período vacacional',
    `empleado_id` int(11) NOT NULL COMMENT 'ID del empleado',
    `año_periodo` int(4) NOT NULL COMMENT 'Año del período vacacional',
    `fecha_inicio_periodo` date NOT NULL COMMENT 'Fecha de inicio del período',
    `fecha_fin_periodo` date NOT NULL COMMENT 'Fecha de fin del período',
    `dias_correspondientes` int(11) NOT NULL DEFAULT 30 COMMENT 'Días de vacaciones correspondientes',
    `dias_adicionales` int(11) NOT NULL DEFAULT 0 COMMENT 'Días adicionales otorgados',
    `dias_totales` int(11) NOT NULL COMMENT 'Total de días disponibles',
    `dias_gozados` int(11) NOT NULL DEFAULT 0 COMMENT 'Días ya gozados',
    `dias_pendientes` int(11) NOT NULL COMMENT 'Días pendientes por gozar',
    `estado_periodo` varchar(20) NOT NULL DEFAULT 'activo' COMMENT 'Estado del período (activo, vencido, cerrado)',
    `fecha_vencimiento` date DEFAULT NULL COMMENT 'Fecha de vencimiento del período',
    `observaciones_periodo` text COMMENT 'Observaciones del período',
    `creado_por_usuario_id` int(11) NOT NULL COMMENT 'ID del usuario que creó el período',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del registro',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`periodo_id`),
    UNIQUE KEY `periodos_empleado_año_unique` (`empleado_id`, `año_periodo`),
    KEY `periodos_empleado_id_idx` (`empleado_id`),
    KEY `periodos_año_idx` (`año_periodo`),
    KEY `periodos_estado_idx` (`estado_periodo`),
    KEY `periodos_fecha_vencimiento_idx` (`fecha_vencimiento`),
    CONSTRAINT `fk_periodos_empleado` FOREIGN KEY (`empleado_id`) REFERENCES `app_rrhh_empleado` (`empleado_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_periodos_creado_por` FOREIGN KEY (`creado_por_usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Períodos vacacionales de empleados';

-- Tabla: solicitudes_vacaciones
-- Gestiona las solicitudes de vacaciones
CREATE TABLE IF NOT EXISTS `solicitudes_vacaciones` (
    `solicitud_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único de la solicitud',
    `empleado_id` int(11) NOT NULL COMMENT 'ID del empleado solicitante',
    `periodo_id` int(11) NOT NULL COMMENT 'ID del período vacacional',
    `codigo_solicitud` varchar(20) NOT NULL COMMENT 'Código único de la solicitud',
    `tipo_solicitud` varchar(30) NOT NULL DEFAULT 'vacaciones' COMMENT 'Tipo de solicitud (vacaciones, adelanto, fraccionamiento)',
    `fecha_inicio_solicitud` date NOT NULL COMMENT 'Fecha de inicio de vacaciones solicitadas',
    `fecha_fin_solicitud` date NOT NULL COMMENT 'Fecha de fin de vacaciones solicitadas',
    `dias_solicitados` int(11) NOT NULL COMMENT 'Número de días solicitados',
    `fecha_retorno` date NOT NULL COMMENT 'Fecha de retorno al trabajo',
    `motivo_solicitud` text COMMENT 'Motivo de la solicitud',
    `direccion_durante_vacaciones` text COMMENT 'Dirección durante las vacaciones',
    `telefono_contacto` varchar(20) DEFAULT NULL COMMENT 'Teléfono de contacto durante vacaciones',
    `estado_solicitud` varchar(20) NOT NULL DEFAULT 'pendiente' COMMENT 'Estado de la solicitud (pendiente, aprobada, rechazada, cancelada)',
    `fecha_solicitud` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de la solicitud',
    `aprobada_por_usuario_id` int(11) DEFAULT NULL COMMENT 'ID del usuario que aprobó',
    `fecha_aprobacion` datetime(6) DEFAULT NULL COMMENT 'Fecha de aprobación',
    `observaciones_aprobacion` text COMMENT 'Observaciones de la aprobación',
    `rechazada_por_usuario_id` int(11) DEFAULT NULL COMMENT 'ID del usuario que rechazó',
    `fecha_rechazo` datetime(6) DEFAULT NULL COMMENT 'Fecha de rechazo',
    `motivo_rechazo` text COMMENT 'Motivo del rechazo',
    `cancelada_por_usuario_id` int(11) DEFAULT NULL COMMENT 'ID del usuario que canceló',
    `fecha_cancelacion` datetime(6) DEFAULT NULL COMMENT 'Fecha de cancelación',
    `motivo_cancelacion` text COMMENT 'Motivo de la cancelación',
    `requiere_reemplazo` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si requiere reemplazo',
    `empleado_reemplazo_id` int(11) DEFAULT NULL COMMENT 'ID del empleado que hará el reemplazo',
    `observaciones_reemplazo` text COMMENT 'Observaciones del reemplazo',
    `archivo_adjunto` varchar(500) DEFAULT NULL COMMENT 'Ruta del archivo adjunto',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del registro',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`solicitud_id`),
    UNIQUE KEY `solicitudes_codigo_unique` (`codigo_solicitud`),
    KEY `solicitudes_empleado_id_idx` (`empleado_id`),
    KEY `solicitudes_periodo_id_idx` (`periodo_id`),
    KEY `solicitudes_estado_idx` (`estado_solicitud`),
    KEY `solicitudes_fecha_inicio_idx` (`fecha_inicio_solicitud`),
    KEY `solicitudes_fecha_solicitud_idx` (`fecha_solicitud`),
    KEY `solicitudes_tipo_idx` (`tipo_solicitud`),
    CONSTRAINT `fk_solicitudes_empleado` FOREIGN KEY (`empleado_id`) REFERENCES `app_rrhh_empleado` (`empleado_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_solicitudes_periodo` FOREIGN KEY (`periodo_id`) REFERENCES `periodos_vacacionales` (`periodo_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_solicitudes_aprobada_por` FOREIGN KEY (`aprobada_por_usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE SET NULL,
    CONSTRAINT `fk_solicitudes_rechazada_por` FOREIGN KEY (`rechazada_por_usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE SET NULL,
    CONSTRAINT `fk_solicitudes_cancelada_por` FOREIGN KEY (`cancelada_por_usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE SET NULL,
    CONSTRAINT `fk_solicitudes_reemplazo` FOREIGN KEY (`empleado_reemplazo_id`) REFERENCES `app_rrhh_empleado` (`empleado_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Solicitudes de vacaciones';

-- Tabla: historial_solicitudes_vacaciones
-- Gestiona el historial de cambios en las solicitudes
CREATE TABLE IF NOT EXISTS `historial_solicitudes_vacaciones` (
    `historial_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del historial',
    `solicitud_id` int(11) NOT NULL COMMENT 'ID de la solicitud',
    `estado_anterior` varchar(20) DEFAULT NULL COMMENT 'Estado anterior de la solicitud',
    `estado_nuevo` varchar(20) NOT NULL COMMENT 'Nuevo estado de la solicitud',
    `accion_realizada` varchar(50) NOT NULL COMMENT 'Acción realizada (crear, aprobar, rechazar, cancelar, modificar)',
    `observaciones_accion` text COMMENT 'Observaciones de la acción',
    `realizada_por_usuario_id` int(11) NOT NULL COMMENT 'ID del usuario que realizó la acción',
    `fecha_accion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de la acción',
    `datos_anteriores` json DEFAULT NULL COMMENT 'Datos anteriores en formato JSON',
    `datos_nuevos` json DEFAULT NULL COMMENT 'Datos nuevos en formato JSON',
    PRIMARY KEY (`historial_id`),
    KEY `historial_solicitud_id_idx` (`solicitud_id`),
    KEY `historial_fecha_accion_idx` (`fecha_accion`),
    KEY `historial_accion_idx` (`accion_realizada`),
    CONSTRAINT `fk_historial_solicitud` FOREIGN KEY (`solicitud_id`) REFERENCES `solicitudes_vacaciones` (`solicitud_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_historial_realizada_por` FOREIGN KEY (`realizada_por_usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Historial de solicitudes de vacaciones';

-- Tabla: goces_vacaciones
-- Gestiona los goces efectivos de vacaciones
CREATE TABLE IF NOT EXISTS `goces_vacaciones` (
    `goce_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del goce',
    `solicitud_id` int(11) NOT NULL COMMENT 'ID de la solicitud aprobada',
    `empleado_id` int(11) NOT NULL COMMENT 'ID del empleado',
    `periodo_id` int(11) NOT NULL COMMENT 'ID del período vacacional',
    `fecha_inicio_goce` date NOT NULL COMMENT 'Fecha de inicio del goce',
    `fecha_fin_goce` date NOT NULL COMMENT 'Fecha de fin del goce',
    `dias_gozados` int(11) NOT NULL COMMENT 'Días efectivamente gozados',
    `fecha_retorno_efectiva` date DEFAULT NULL COMMENT 'Fecha efectiva de retorno',
    `estado_goce` varchar(20) NOT NULL DEFAULT 'programado' COMMENT 'Estado del goce (programado, en_curso, finalizado, interrumpido)',
    `motivo_interrupcion` text COMMENT 'Motivo de interrupción si aplica',
    `fecha_interrupcion` date DEFAULT NULL COMMENT 'Fecha de interrupción si aplica',
    `observaciones_goce` text COMMENT 'Observaciones del goce',
    `registrado_por_usuario_id` int(11) NOT NULL COMMENT 'ID del usuario que registró el goce',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del registro',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`goce_id`),
    KEY `goces_solicitud_id_idx` (`solicitud_id`),
    KEY `goces_empleado_id_idx` (`empleado_id`),
    KEY `goces_periodo_id_idx` (`periodo_id`),
    KEY `goces_fecha_inicio_idx` (`fecha_inicio_goce`),
    KEY `goces_estado_idx` (`estado_goce`),
    CONSTRAINT `fk_goces_solicitud` FOREIGN KEY (`solicitud_id`) REFERENCES `solicitudes_vacaciones` (`solicitud_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_goces_empleado` FOREIGN KEY (`empleado_id`) REFERENCES `app_rrhh_empleado` (`empleado_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_goces_periodo` FOREIGN KEY (`periodo_id`) REFERENCES `periodos_vacacionales` (`periodo_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_goces_registrado_por` FOREIGN KEY (`registrado_por_usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Goces efectivos de vacaciones';

-- Tabla: configuracion_vacaciones
-- Configuración del módulo de vacaciones
CREATE TABLE IF NOT EXISTS `configuracion_vacaciones` (
    `config_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único de la configuración',
    `parametro` varchar(100) NOT NULL COMMENT 'Nombre del parámetro',
    `valor` text NOT NULL COMMENT 'Valor del parámetro',
    `tipo_dato` varchar(20) NOT NULL DEFAULT 'string' COMMENT 'Tipo de dato (string, integer, boolean, date, json)',
    `descripcion` text COMMENT 'Descripción del parámetro',
    `categoria` varchar(50) DEFAULT 'general' COMMENT 'Categoría del parámetro',
    `es_editable` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Indica si el parámetro es editable',
    `valor_por_defecto` text COMMENT 'Valor por defecto del parámetro',
    `validacion_regex` varchar(255) DEFAULT NULL COMMENT 'Expresión regular para validación',
    `orden_visualizacion` int(11) DEFAULT 0 COMMENT 'Orden de visualización',
    `activo` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Indica si la configuración está activa',
    `modificado_por_usuario_id` int(11) DEFAULT NULL COMMENT 'ID del usuario que modificó',
    `fecha_creacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha de creación del registro',
    `fecha_actualizacion` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Fecha de última actualización',
    PRIMARY KEY (`config_id`),
    UNIQUE KEY `configuracion_parametro_unique` (`parametro`),
    KEY `configuracion_categoria_idx` (`categoria`),
    KEY `configuracion_activo_idx` (`activo`),
    CONSTRAINT `fk_configuracion_modificado_por` FOREIGN KEY (`modificado_por_usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Configuración del módulo de vacaciones';

-- =====================================================
-- TABLAS DE AUDITORÍA
-- =====================================================

-- Tabla: auditoria_accesos
-- Registra los accesos al sistema
CREATE TABLE IF NOT EXISTS `auditoria_accesos` (
    `acceso_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del acceso',
    `usuario_id` int(11) DEFAULT NULL COMMENT 'ID del usuario (NULL para intentos fallidos)',
    `username_intento` varchar(150) DEFAULT NULL COMMENT 'Username utilizado en el intento',
    `tipo_acceso` varchar(20) NOT NULL COMMENT 'Tipo de acceso (login, logout, login_fallido)',
    `ip_address` varchar(45) NOT NULL COMMENT 'Dirección IP del cliente',
    `user_agent` text COMMENT 'User Agent del navegador',
    `dispositivo` varchar(100) DEFAULT NULL COMMENT 'Información del dispositivo',
    `navegador` varchar(50) DEFAULT NULL COMMENT 'Navegador utilizado',
    `sistema_operativo` varchar(50) DEFAULT NULL COMMENT 'Sistema operativo',
    `ubicacion_geografica` varchar(100) DEFAULT NULL COMMENT 'Ubicación geográfica aproximada',
    `exitoso` tinyint(1) NOT NULL COMMENT 'Indica si el acceso fue exitoso',
    `motivo_fallo` varchar(100) DEFAULT NULL COMMENT 'Motivo del fallo si aplica',
    `session_id` varchar(40) DEFAULT NULL COMMENT 'ID de la sesión',
    `duracion_sesion` int(11) DEFAULT NULL COMMENT 'Duración de la sesión en segundos',
    `modulo_accedido` varchar(50) DEFAULT NULL COMMENT 'Módulo al que se accedió',
    `url_accedida` varchar(500) DEFAULT NULL COMMENT 'URL accedida',
    `metodo_http` varchar(10) DEFAULT NULL COMMENT 'Método HTTP utilizado',
    `codigo_respuesta` int(11) DEFAULT NULL COMMENT 'Código de respuesta HTTP',
    `fecha_acceso` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha y hora del acceso',
    `fecha_logout` datetime(6) DEFAULT NULL COMMENT 'Fecha y hora del logout',
    PRIMARY KEY (`acceso_id`),
    KEY `auditoria_accesos_usuario_id_idx` (`usuario_id`),
    KEY `auditoria_accesos_tipo_idx` (`tipo_acceso`),
    KEY `auditoria_accesos_ip_idx` (`ip_address`),
    KEY `auditoria_accesos_fecha_idx` (`fecha_acceso`),
    KEY `auditoria_accesos_exitoso_idx` (`exitoso`),
    KEY `auditoria_accesos_session_idx` (`session_id`),
    CONSTRAINT `fk_auditoria_accesos_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Auditoría de accesos al sistema';

-- Tabla: auditoria_cambios
-- Registra los cambios realizados en el sistema
CREATE TABLE IF NOT EXISTS `auditoria_cambios` (
    `cambio_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del cambio',
    `usuario_id` int(11) NOT NULL COMMENT 'ID del usuario que realizó el cambio',
    `tabla_afectada` varchar(100) NOT NULL COMMENT 'Nombre de la tabla afectada',
    `registro_id` varchar(50) NOT NULL COMMENT 'ID del registro afectado',
    `tipo_operacion` varchar(20) NOT NULL COMMENT 'Tipo de operación (INSERT, UPDATE, DELETE)',
    `campo_modificado` varchar(100) DEFAULT NULL COMMENT 'Campo específico modificado (para UPDATE)',
    `valor_anterior` longtext COMMENT 'Valor anterior del campo',
    `valor_nuevo` longtext COMMENT 'Valor nuevo del campo',
    `datos_completos_anteriores` json DEFAULT NULL COMMENT 'Datos completos anteriores en formato JSON',
    `datos_completos_nuevos` json DEFAULT NULL COMMENT 'Datos completos nuevos en formato JSON',
    `ip_address` varchar(45) NOT NULL COMMENT 'Dirección IP del cliente',
    `user_agent` text COMMENT 'User Agent del navegador',
    `modulo_origen` varchar(50) DEFAULT NULL COMMENT 'Módulo desde donde se realizó el cambio',
    `url_origen` varchar(500) DEFAULT NULL COMMENT 'URL desde donde se realizó el cambio',
    `metodo_http` varchar(10) DEFAULT NULL COMMENT 'Método HTTP utilizado',
    `razon_cambio` text COMMENT 'Razón o justificación del cambio',
    `es_cambio_masivo` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si es parte de un cambio masivo',
    `lote_cambio_id` varchar(36) DEFAULT NULL COMMENT 'ID del lote para cambios masivos',
    `nivel_criticidad` varchar(20) DEFAULT 'medio' COMMENT 'Nivel de criticidad (bajo, medio, alto, critico)',
    `requiere_aprobacion` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indica si el cambio requería aprobación',
    `aprobado_por_usuario_id` int(11) DEFAULT NULL COMMENT 'ID del usuario que aprobó el cambio',
    `fecha_aprobacion` datetime(6) DEFAULT NULL COMMENT 'Fecha de aprobación del cambio',
    `observaciones` text COMMENT 'Observaciones adicionales',
    `fecha_cambio` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha y hora del cambio',
    PRIMARY KEY (`cambio_id`),
    KEY `auditoria_cambios_usuario_id_idx` (`usuario_id`),
    KEY `auditoria_cambios_tabla_idx` (`tabla_afectada`),
    KEY `auditoria_cambios_registro_idx` (`registro_id`),
    KEY `auditoria_cambios_tipo_operacion_idx` (`tipo_operacion`),
    KEY `auditoria_cambios_fecha_idx` (`fecha_cambio`),
    KEY `auditoria_cambios_lote_idx` (`lote_cambio_id`),
    KEY `auditoria_cambios_criticidad_idx` (`nivel_criticidad`),
    KEY `auditoria_cambios_ip_idx` (`ip_address`),
    CONSTRAINT `fk_auditoria_cambios_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_auditoria_cambios_aprobado_por` FOREIGN KEY (`aprobado_por_usuario_id`) REFERENCES `app_rrhh_usuario` (`usuario_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Auditoría de cambios en el sistema';

-- =====================================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- =====================================================

-- Índices compuestos para consultas frecuentes
CREATE INDEX `idx_empleado_estado_activo` ON `app_rrhh_empleado` (`estado_empleado`, `activo`);
CREATE INDEX `idx_usuario_activo_tipo` ON `app_rrhh_usuario` (`is_active`, `tipo_usuario`);
CREATE INDEX `idx_datos_laborales_empleado_activo` ON `datos_laborales` (`empleado_id`, `estado_laboral`);
CREATE INDEX `idx_contratos_empleado_vigente` ON `contratos_adendas` (`empleado_id`, `estado_contrato`);
CREATE INDEX `idx_solicitudes_empleado_estado` ON `solicitudes_vacaciones` (`empleado_id`, `estado_solicitud`);
CREATE INDEX `idx_documentos_empleado_tipo` ON `documentos_digitales` (`empleado_id`, `tipo_documento`);
CREATE INDEX `idx_auditoria_fecha_usuario` ON `auditoria_cambios` (`fecha_cambio`, `usuario_id`);
CREATE INDEX `idx_auditoria_accesos_fecha_tipo` ON `auditoria_accesos` (`fecha_acceso`, `tipo_acceso`);

-- =====================================================
-- COMENTARIOS FINALES
-- =====================================================

/*
Estructura de Base de Datos Refactorizada para Django
=====================================================

Esta estructura ha sido refactorizada para alinearse con:
1. Convenciones de nomenclatura de Django
2. Tipos de datos compatibles con Django ORM
3. Relaciones y constraints apropiadas
4. Índices optimizados para consultas frecuentes
5. Tablas de auditoría para trazabilidad
6. Configuración flexible del sistema

Características principales:
- Soporte completo para autenticación Django
- Gestión integral de empleados y RRHH
- Módulo de vacaciones completo
- Sistema de documentos digitales
- Auditoría completa de accesos y cambios
- Estructura modular y escalable

Compatibilidad:
- Django 4.x+
- MySQL 8.0+
- Charset: utf8mb4
- Collation: utf8mb4_unicode_ci
*/