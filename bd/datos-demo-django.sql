-- ========================================
-- DATOS DEMO E INICIALIZACIÓN - ESTRUCTURA DJANGO REFACTORIZADA
-- ========================================
-- Archivo: datos-demo-django.sql
-- Descripción: Datos de demostración y configuración inicial
-- Compatible con: estructura-django-refactorizada.sql
-- Fecha: 2024
-- ========================================

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- ========================================
-- CONFIGURACIÓN INICIAL DE BASE DE DATOS
-- ========================================

USE `bd_rrhh_intranet`;

-- ========================================
-- DATOS INICIALES DJANGO - CONTENT TYPES
-- ========================================

-- Insertar content types para Django
INSERT IGNORE INTO `django_content_type` (`app_label`, `model`) VALUES
('auth', 'group'),
('auth', 'permission'),
('contenttypes', 'contenttype'),
('sessions', 'session'),
('rrhh', 'modulos'),
('rrhh', 'rol'),
('rrhh', 'permiso'),
('rrhh', 'rolpermisos'),
('rrhh', 'area'),
('rrhh', 'empleado'),
('rrhh', 'usuario'),
('rrhh', 'usuarioroles'),
('rrhh', 'datoslaborales'),
('rrhh', 'contratosadendas'),
('rrhh', 'historialubicaciones'),
('rrhh', 'datosfamiliares'),
('rrhh', 'datosacademicos'),
('rrhh', 'documentosdigitales'),
('rrhh', 'periodosvacacionales'),
('rrhh', 'solicitudesvacaciones'),
('rrhh', 'historialsolicitudesvacaciones'),
('rrhh', 'gocesvacaciones'),
('rrhh', 'configuracionvacaciones'),
('rrhh', 'auditoriaaccesos'),
('rrhh', 'auditoriacambios');

-- ========================================
-- DATOS INICIALES DJANGO - PERMISSIONS
-- ========================================

-- Insertar permisos básicos de Django para cada modelo
INSERT IGNORE INTO `auth_permission` (`name`, `content_type_id`, `codename`) VALUES
-- Permisos para modulos
('Can add modulos', (SELECT id FROM django_content_type WHERE app_label='rrhh' AND model='modulos'), 'add_modulos'),
('Can change modulos', (SELECT id FROM django_content_type WHERE app_label='rrhh' AND model='modulos'), 'change_modulos'),
('Can delete modulos', (SELECT id FROM django_content_type WHERE app_label='rrhh' AND model='modulos'), 'delete_modulos'),
('Can view modulos', (SELECT id FROM django_content_type WHERE app_label='rrhh' AND model='modulos'), 'view_modulos'),
-- Permisos para empleado
('Can add empleado', (SELECT id FROM django_content_type WHERE app_label='rrhh' AND model='empleado'), 'add_empleado'),
('Can change empleado', (SELECT id FROM django_content_type WHERE app_label='rrhh' AND model='empleado'), 'change_empleado'),
('Can delete empleado', (SELECT id FROM django_content_type WHERE app_label='rrhh' AND model='empleado'), 'delete_empleado'),
('Can view empleado', (SELECT id FROM django_content_type WHERE app_label='rrhh' AND model='empleado'), 'view_empleado'),
-- Permisos para usuario
('Can add usuario', (SELECT id FROM django_content_type WHERE app_label='rrhh' AND model='usuario'), 'add_usuario'),
('Can change usuario', (SELECT id FROM django_content_type WHERE app_label='rrhh' AND model='usuario'), 'change_usuario'),
('Can delete usuario', (SELECT id FROM django_content_type WHERE app_label='rrhh' AND model='usuario'), 'delete_usuario'),
('Can view usuario', (SELECT id FROM django_content_type WHERE app_label='rrhh' AND model='usuario'), 'view_usuario');

-- ========================================
-- DATOS INICIALES - MÓDULOS DEL SISTEMA
-- ========================================

-- Insertar módulos del sistema (usar INSERT IGNORE para evitar duplicados)
INSERT IGNORE INTO `modulos` (`nombre_modulo`, `descripcion_modulo`, `icono_modulo`, `ruta_modulo`, `orden_visualizacion`, `estado_modulo`, `fecha_creacion`, `fecha_actualizacion`) VALUES
('Dashboard', 'Panel principal con estadísticas y resumen general del sistema', 'fas fa-tachometer-alt', '/dashboard', 1, 'activo', NOW(), NOW()),
('Empleados', 'Gestión completa de información de empleados y personal', 'fas fa-users', '/empleados', 2, 'activo', NOW(), NOW()),
('Vacaciones', 'Módulo de gestión de vacaciones, solicitudes y períodos', 'fas fa-calendar-alt', '/vacaciones', 3, 'activo', NOW(), NOW()),
('Administración', 'Configuración del sistema, usuarios, roles y permisos', 'fas fa-cogs', '/administracion', 4, 'activo', NOW(), NOW()),
('Reportes', 'Generación de reportes y estadísticas del sistema', 'fas fa-chart-bar', '/reportes', 5, 'activo', NOW(), NOW());

-- ========================================
-- DATOS INICIALES - ROLES DEL SISTEMA
-- ========================================

-- Insertar roles del sistema (usar INSERT IGNORE para evitar duplicados)
INSERT IGNORE INTO `rol` (`nombre_rol`, `descripcion_rol`, `nivel_jerarquico`, `es_rol_sistema`, `estado_rol`, `fecha_creacion`, `fecha_actualizacion`) VALUES
('Super Administrador', 'Acceso completo a todas las funcionalidades del sistema', 1, true, 'activo', NOW(), NOW()),
('Administrador RRHH', 'Gestión completa del módulo de recursos humanos', 2, true, 'activo', NOW(), NOW()),
('Jefe de Área', 'Gestión de empleados de su área y aprobación de solicitudes', 3, false, 'activo', NOW(), NOW()),
('Analista RRHH', 'Operaciones de consulta y gestión básica de RRHH', 4, false, 'activo', NOW(), NOW()),
('Empleado', 'Acceso básico para consultar información personal y realizar solicitudes', 5, false, 'activo', NOW(), NOW());

-- ========================================
-- DATOS INICIALES - PERMISOS DEL SISTEMA
-- ========================================

-- Insertar permisos del sistema (usar INSERT IGNORE para evitar duplicados)
INSERT IGNORE INTO `permiso` (`nombre_permiso`, `descripcion_permiso`, `modulo_id`, `tipo_permiso`, `estado_permiso`, `fecha_creacion`) VALUES
-- Permisos del Dashboard
('ver_dashboard', 'Visualizar el panel principal del sistema', 1, 'leer', 'activo', NOW()),
('ver_estadisticas_generales', 'Ver estadísticas generales del sistema', 1, 'leer', 'activo', NOW()),
-- Permisos de Empleados
('crear_empleado', 'Crear nuevos registros de empleados', 2, 'crear', 'activo', NOW()),
('ver_empleados', 'Visualizar información de todos los empleados', 2, 'leer', 'activo', NOW()),
('editar_empleado', 'Modificar información de empleados', 2, 'actualizar', 'activo', NOW()),
('eliminar_empleado', 'Eliminar registros de empleados', 2, 'eliminar', 'activo', NOW()),
('ver_empleado_propio', 'Ver información personal propia', 2, 'leer', 'activo', NOW()),
('editar_empleado_propio', 'Editar información personal propia', 2, 'actualizar', 'activo', NOW()),
-- Permisos de Vacaciones
('crear_solicitud_vacaciones', 'Crear solicitudes de vacaciones', 3, 'crear', 'activo', NOW()),
('ver_solicitudes_vacaciones', 'Ver todas las solicitudes de vacaciones', 3, 'leer', 'activo', NOW()),
('aprobar_solicitudes_vacaciones', 'Aprobar o rechazar solicitudes de vacaciones', 3, 'aprobar', 'activo', NOW()),
('ver_reportes_vacaciones', 'Visualizar reportes del módulo de vacaciones', 3, 'leer', 'activo', NOW()),
('administrar_periodos_vacaciones', 'Gestionar períodos vacacionales', 3, 'ejecutar', 'activo', NOW()),
('configurar_modulo_vacaciones', 'Configurar parámetros del módulo de vacaciones', 3, 'ejecutar', 'activo', NOW()),
('ver_vacaciones_propias', 'Ver solicitudes y períodos vacacionales propios', 3, 'leer', 'activo', NOW()),
-- Permisos de Administración
('gestionar_usuarios', 'Crear, editar y eliminar usuarios del sistema', 4, 'ejecutar', 'activo', NOW()),
('gestionar_roles', 'Administrar roles y permisos del sistema', 4, 'ejecutar', 'activo', NOW()),
('ver_auditoria', 'Visualizar registros de auditoría del sistema', 4, 'leer', 'activo', NOW()),
('configurar_sistema', 'Configurar parámetros generales del sistema', 4, 'ejecutar', 'activo', NOW()),
-- Permisos de Reportes
('generar_reportes', 'Generar reportes del sistema', 5, 'ejecutar', 'activo', NOW()),
('exportar_datos', 'Exportar información del sistema', 5, 'ejecutar', 'activo', NOW());

-- ========================================
-- ASIGNACIÓN DE PERMISOS A ROLES
-- ========================================

-- Asignar permisos al rol Super Administrador (todos los permisos)
INSERT IGNORE INTO `rol_permisos` (`rol_id`, `permiso_id`, `fecha_asignacion`) VALUES
(1, 1, NOW()), (1, 2, NOW()), (1, 3, NOW()), (1, 4, NOW()), (1, 5, NOW()), (1, 6, NOW()), (1, 7, NOW()), (1, 8, NOW()), (1, 9, NOW()), (1, 10, NOW()),
(1, 11, NOW()), (1, 12, NOW()), (1, 13, NOW()), (1, 14, NOW()), (1, 15, NOW()), (1, 16, NOW()), (1, 17, NOW()), (1, 18, NOW()), (1, 19, NOW()), (1, 20, NOW()), (1, 21, NOW());

-- Asignar permisos al rol Administrador RRHH
INSERT IGNORE INTO `rol_permisos` (`rol_id`, `permiso_id`, `fecha_asignacion`) VALUES
(2, 1, NOW()), (2, 2, NOW()), (2, 3, NOW()), (2, 4, NOW()), (2, 5, NOW()), (2, 7, NOW()), (2, 8, NOW()), (2, 9, NOW()), (2, 10, NOW()),
(2, 11, NOW()), (2, 12, NOW()), (2, 13, NOW()), (2, 14, NOW()), (2, 15, NOW()), (2, 16, NOW()), (2, 17, NOW()), (2, 18, NOW()), (2, 20, NOW()), (2, 21, NOW());

-- Asignar permisos al rol Jefe de Área
INSERT IGNORE INTO `rol_permisos` (`rol_id`, `permiso_id`, `fecha_asignacion`) VALUES
(3, 1, NOW()), (3, 2, NOW()), (3, 4, NOW()), (3, 5, NOW()), (3, 7, NOW()), (3, 8, NOW()), (3, 9, NOW()), (3, 10, NOW()),
(3, 11, NOW()), (3, 12, NOW()), (3, 15, NOW()), (3, 20, NOW());

-- Asignar permisos al rol Analista RRHH
INSERT IGNORE INTO `rol_permisos` (`rol_id`, `permiso_id`, `fecha_asignacion`) VALUES
(4, 1, NOW()), (4, 2, NOW()), (4, 3, NOW()), (4, 4, NOW()), (4, 5, NOW()), (4, 7, NOW()), (4, 8, NOW()), (4, 9, NOW()), (4, 10, NOW()),
(4, 12, NOW()), (4, 13, NOW()), (4, 15, NOW()), (4, 20, NOW());

-- Asignar permisos al rol Empleado
INSERT IGNORE INTO `rol_permisos` (`rol_id`, `permiso_id`, `fecha_asignacion`) VALUES
(5, 1, NOW()), (5, 7, NOW()), (5, 8, NOW()), (5, 9, NOW()), (5, 15, NOW());

-- ========================================
-- CONFIGURACIÓN DEL MÓDULO DE VACACIONES
-- ========================================

-- Insertar configuración inicial del módulo de vacaciones
INSERT IGNORE INTO `configuracion_vacaciones` (
    `tipo_configuracion`, `dias_por_ano`, `dias_adicionales_antiguedad`, `anos_para_adicional`,
    `permite_acumulacion`, `max_dias_acumulables`, `dias_minimos_solicitud`, `dias_maximos_solicitud`,
    `dias_anticipacion_minima`, `tipo_calculo`, `incluye_feriados`, `incluye_fines_semana`,
    `requiere_aprobacion_jefe`, `requiere_aprobacion_rrhh`, `niveles_aprobacion`, `permite_fraccionamiento`,
    `min_dias_por_fraccion`, `max_fracciones_por_ano`, `activo`, `fecha_inicio_vigencia`,
    `observaciones`, `fecha_creacion`, `fecha_actualizacion`
) VALUES (
    'general', 30, 2, 5, 1, 60, 5, 30, 15, 'calendario', 0, 1, 1, 1, 2, 1, 5, 3, 1, '2024-01-01',
    'Configuración general del módulo de vacaciones', NOW(), NOW()
);

-- ========================================
-- DATOS DE EJEMPLO PARA DEMOSTRACIÓN
-- ========================================

-- Insertar áreas de ejemplo
INSERT IGNORE INTO `area` (`nombre_organo`, `nombre_unidad_organica`, `siglas_area`, `descripcion_area`, `jefe_area`, `estado_area`, `nivel_jerarquico`, `total_empleados`, `fecha_creacion`, `fecha_actualizacion`) VALUES
('Gerencia General', 'Oficina de Tecnologías de la Información', 'OTI', 'Área encargada de la gestión tecnológica', 'Ing. Carlos Mendoza', 'activo', 2, 5, NOW(), NOW()),
('Gerencia General', 'Oficina de Recursos Humanos', 'RRHH', 'Área encargada de la gestión del talento humano', 'Lic. Roberto Flores', 'activo', 2, 8, NOW(), NOW()),
('Gerencia General', 'Oficina de Administración y Finanzas', 'OAF', 'Área encargada de la gestión administrativa y financiera', 'CPC. Ana Torres', 'activo', 2, 6, NOW(), NOW()),
('Gerencia General', 'Oficina de Planificación y Presupuesto', 'OPP', 'Área encargada de la planificación estratégica', 'Eco. María Rodríguez', 'activo', 2, 4, NOW(), NOW());

-- ========================================
-- EMPLEADOS DE EJEMPLO
-- ========================================

-- Insertar empleados de ejemplo
INSERT IGNORE INTO `empleado` (
    `numero_documento`, `tipo_documento`, `nombres_empleado`, 
    `apellido_paterno`, `apellido_materno`, `numero_ruc`, `genero_empleado`, 
    `fecha_nacimiento`, `es_padre_familia`, `sistema_pensiones`, 
    `telefono_celular`, `correo_personal`, `estado_civil`, 
    `direccion_domicilio`, `distrito_domicilio`, `provincia_domicilio`, 
    `departamento_domicilio`, `entidad_bancaria`, `numero_cuenta_bancaria`, 
    `numero_cci`, `estado_empleado`, `es_militar`, `tipo_comision`, 
    `tipo_seguro_salud`, `vigencia_estado_seguro`, `fecha_registro`, `fecha_actualizacion`
) VALUES 
('12345678', 'DNI', 'Juan Carlos', 'García', 'López', '10123456781', 'masculino', '1985-03-15', false, 'AFP', '987654321', 'juan.garcia@email.com', 'soltero', 'Av. Principal 123', 'Lima', 'Lima', 'Lima', 'Banco de Crédito', '1234567890123456', '00212345678901234567', 'activo', false, 'ninguna', 'essalud', '2024-12-31', NOW(), NOW()),
('87654321', 'DNI', 'María Elena', 'Rodríguez', 'Pérez', '10876543211', 'femenino', '1990-07-22', true, 'ONP', '987654322', 'maria.rodriguez@email.com', 'casado', 'Jr. Secundario 456', 'Lima', 'Lima', 'Lima', 'Banco Continental', '2345678901234567', '00223456789012345678', 'activo', false, 'ninguna', 'essalud', '2024-12-31', NOW(), NOW()),
('11223344', 'DNI', 'Carlos Alberto', 'Mendoza', 'Silva', '10112233441', 'masculino', '1988-11-10', true, 'AFP', '987654323', 'carlos.mendoza@email.com', 'casado', 'Calle Tercera 789', 'Lima', 'Lima', 'Lima', 'Banco de la Nación', '3456789012345678', '00234567890123456789', 'activo', false, 'ninguna', 'essalud', '2024-12-31', NOW(), NOW()),
('44332211', 'DNI', 'Ana Sofía', 'Torres', 'Vega', '10443322111', 'femenino', '1992-05-18', false, 'AFP', '987654324', 'ana.torres@email.com', 'soltero', 'Av. Cuarta 321', 'Lima', 'Lima', 'Lima', 'Interbank', '4567890123456789', '00245678901234567890', 'activo', false, 'ninguna', 'essalud', '2024-12-31', NOW(), NOW()),
('55667788', 'DNI', 'Roberto Miguel', 'Flores', 'Castillo', '10556677881', 'masculino', '1983-09-03', true, 'ONP', '987654325', 'roberto.flores@email.com', 'casado', 'Jr. Quinta 654', 'Lima', 'Lima', 'Lima', 'Scotiabank', '5678901234567890', '00256789012345678901', 'activo', false, 'ninguna', 'essalud', '2024-12-31', NOW(), NOW());

-- ========================================
-- USUARIOS DEL SISTEMA
-- ========================================

-- Insertar usuarios del sistema
INSERT IGNORE INTO `usuarios` (
    `password`, `last_login`, `is_superuser`, `username`, `nombres_usuario`, `apellidos_usuario`, 
    `email`, `is_staff`, `is_active`, `date_joined`, `empleado_id`, 
    `tipo_usuario`, `nivel_acceso`, `intentos_fallidos`, 
    `fecha_bloqueo`, `requiere_cambio_password`, `estado_usuario`, `sesiones_simultaneas_permitidas`,
    `recibir_notificaciones_email`, `recibir_notificaciones_sistema`, `fecha_creacion`, `fecha_actualizacion`
) VALUES
('pbkdf2_sha256$600000$randomsalt1$hashedpassword1', NULL, true, 'admin', 'Super', 'Admin', 'admin@institucion.gob.pe', true, true, NOW(), NULL, 'administrador', 'alto', 0, NULL, false, 'activo', 5, true, true, NOW(), NOW()),
('pbkdf2_sha256$600000$randomsalt2$hashedpassword2', NULL, false, 'jgarcia', 'Juan Carlos', 'García López', 'jgarcia@institucion.gob.pe', false, true, NOW(), 1, 'empleado', 'medio', 0, NULL, false, 'activo', 1, true, true, NOW(), NOW()),
('pbkdf2_sha256$600000$randomsalt3$hashedpassword3', NULL, false, 'mrodriguez', 'María Elena', 'Rodríguez Pérez', 'mrodriguez@institucion.gob.pe', false, true, NOW(), 2, 'empleado', 'medio', 0, NULL, false, 'activo', 1, true, true, NOW(), NOW()),
('pbkdf2_sha256$600000$randomsalt4$hashedpassword4', NULL, false, 'cmendoza', 'Carlos Alberto', 'Mendoza Silva', 'cmendoza@institucion.gob.pe', false, true, NOW(), 3, 'empleado', 'medio', 0, NULL, false, 'activo', 1, true, true, NOW(), NOW()),
('pbkdf2_sha256$600000$randomsalt5$hashedpassword5', NULL, false, 'atorres', 'Ana Sofía', 'Torres Vega', 'atorres@institucion.gob.pe', false, true, NOW(), 4, 'empleado', 'medio', 0, NULL, false, 'activo', 1, true, true, NOW(), NOW()),
('pbkdf2_sha256$600000$randomsalt6$hashedpassword6', NULL, false, 'rflores', 'Roberto Miguel', 'Flores Castillo', 'rflores@institucion.gob.pe', false, true, NOW(), 5, 'empleado', 'medio', 0, NULL, false, 'activo', 1, true, true, NOW(), NOW());

-- ========================================
-- ASIGNACIÓN DE ROLES A USUARIOS
-- ========================================

-- Asignar roles a usuarios
INSERT IGNORE INTO `usuario_roles` (`usuario_id`, `rol_id`, `fecha_asignacion`, `estado_asignacion`) VALUES
(1, 1, NOW(), 'activo'), -- Admin - Super Administrador
(2, 5, NOW(), 'activo'), -- Juan García - Empleado
(3, 4, NOW(), 'activo'), -- María Rodríguez - Analista RRHH
(4, 3, NOW(), 'activo'), -- Carlos Mendoza - Jefe de Área
(5, 4, NOW(), 'activo'), -- Ana Torres - Analista RRHH
(6, 2, NOW(), 'activo'); -- Roberto Flores - Administrador RRHH

-- ========================================
-- DATOS LABORALES DE EJEMPLO
-- ========================================

-- Insertar datos laborales de ejemplo
INSERT IGNORE INTO `datos_laborales` (
    `empleado_id`, `area_id`, `fecha_ingreso`, `cargo_empleado`, `categoria`,
    `tipo_contrato`, `regimen_laboral`, `modalidad_trabajo`, 
    `jornada_laboral`, `fecha_inicio_contrato`, `sueldo_basico`, 
    `asignacion_familiar`, `bonificacion_especial`, `otras_bonificaciones`, 
    `horas_semanales`, `estado_datos`, `fecha_registro`, `fecha_actualizacion`
) VALUES 
(1, 1, '2021-03-15', 'Analista de Sistemas', 'PROFESIONAL', 'CAS', 'CAS', 'presencial', 'completa', '2021-03-15', 3500.00, 93.00, 0.00, 0.00, 40.00, 'activo', NOW(), NOW()),
(2, 4, '2020-01-10', 'Especialista en Planificación', 'PROFESIONAL', 'CAS', 'CAS', 'presencial', 'completa', '2020-01-10', 4000.00, 93.00, 0.00, 0.00, 40.00, 'activo', NOW(), NOW()),
(3, 1, '2019-06-01', 'Jefe de OTI', 'DIRECTIVO', 'CAP', 'CAP', 'presencial', 'completa', '2019-06-01', 4500.00, 93.00, 0.00, 0.00, 40.00, 'activo', NOW(), NOW()),
(4, 3, '2022-08-15', 'Especialista en Finanzas', 'PROFESIONAL', 'CAS', 'CAS', 'presencial', 'completa', '2022-08-15', 3800.00, 93.00, 0.00, 0.00, 40.00, 'activo', NOW(), NOW()),
(5, 2, '2018-02-20', 'Jefe de RRHH', 'DIRECTIVO', 'CAP', 'CAP', 'presencial', 'completa', '2018-02-20', 5500.00, 93.00, 0.00, 0.00, 40.00, 'activo', NOW(), NOW());

-- ========================================
-- DATOS FAMILIARES DE EJEMPLO
-- ========================================

-- Insertar algunos datos familiares de ejemplo
INSERT IGNORE INTO `datos_familiares` (
    `empleado_id`, `nombres_familiar`, `apellido_paterno`, 
    `apellido_materno`, `numero_documento`, `tipo_documento`,
    `genero_familiar`, `parentesco`, `fecha_nacimiento`, 
    `es_beneficiario`, `es_dependiente`
) VALUES 
(2, 'Pedro Luis', 'Rodríguez', 'Pérez', '12345679', 'DNI', 'masculino', 'conyuge', '1988-03-10', true, false),
(2, 'Sofía', 'Rodríguez', 'Pérez', '12345680', 'DNI', 'femenino', 'hija', '2015-08-22', true, true),
(3, 'Carmen Rosa', 'Silva', 'Mendoza', '12345681', 'DNI', 'femenino', 'conyuge', '1990-12-05', true, false),
(3, 'Diego', 'Mendoza', 'Silva', '12345682', 'DNI', 'masculino', 'hijo', '2018-06-15', true, true),
(5, 'Elena Patricia', 'Castillo', 'Flores', '12345683', 'DNI', 'femenino', 'conyuge', '1985-04-18', true, false);

-- ========================================
-- MENSAJE DE CONFIRMACIÓN PARCIAL
-- ========================================

SELECT 
    'DATOS DEMO DJANGO - PARTE 1 COMPLETADA!' as mensaje,
    'Sistema configurado con estructura Django' as estado,
    'Usuarios, roles, permisos y empleados creados' as contenido_parte1;

-- ========================================
-- DATOS DE EJEMPLO DEL MÓDULO DE VACACIONES
-- ========================================

-- Insertar períodos vacacionales de ejemplo
INSERT IGNORE INTO `periodos_vacacionales` (
    `empleado_id`, `ano_periodo`, `fecha_inicio_periodo`, `fecha_fin_periodo`, `fecha_vencimiento`, 
    `dias_correspondientes`, `dias_adicionales`, `dias_totales`, `dias_gozados`, `dias_pendientes`, 
    `dias_vencidos`, `estado_periodo`, `observaciones`, `configuracion_id`, `fecha_creacion`, `fecha_actualizacion`
) VALUES 
-- Períodos de Juan García
(1, 2021, '2021-03-15', '2022-03-14', '2023-03-15', 30, 0, 30, 25, 5, 0, 'vencido', 'Período parcialmente gozado', 1, NOW(), NOW()),
(1, 2022, '2022-03-15', '2023-03-14', '2024-03-15', 30, 0, 30, 30, 0, 0, 'cerrado', 'Período completamente gozado', 1, NOW(), NOW()),
(1, 2023, '2023-03-15', '2024-03-14', '2025-03-15', 30, 0, 30, 20, 10, 0, 'vigente', 'Período en curso', 1, NOW(), NOW()),
(1, 2024, '2024-03-15', '2025-03-14', '2026-03-15', 30, 0, 30, 5, 25, 0, 'vigente', 'Período actual - vacaciones de julio gozadas', 1, NOW(), NOW()),
-- Períodos de María Rodríguez
(2, 2020, '2020-01-10', '2021-01-09', '2022-01-10', 30, 0, 30, 30, 0, 0, 'cerrado', 'Período completamente gozado', 1, NOW(), NOW()),
(2, 2021, '2021-01-10', '2022-01-09', '2023-01-10', 30, 0, 30, 25, 5, 0, 'vencido', 'Período parcialmente gozado', 1, NOW(), NOW()),
(2, 2022, '2022-01-10', '2023-01-09', '2024-01-10', 30, 0, 30, 30, 0, 0, 'cerrado', 'Período completamente gozado', 1, NOW(), NOW()),
(2, 2023, '2023-01-10', '2024-01-09', '2025-01-10', 30, 0, 30, 15, 15, 0, 'vigente', 'Período en curso', 1, NOW(), NOW()),
(2, 2024, '2024-01-10', '2025-01-09', '2026-01-10', 30, 0, 30, 0, 30, 0, 'vigente', 'Período actual - solicitud en revisión', 1, NOW(), NOW()),
-- Períodos de Carlos Mendoza
(3, 2019, '2019-06-01', '2020-05-31', '2021-06-01', 30, 0, 30, 30, 0, 0, 'cerrado', 'Período completamente gozado', 1, NOW(), NOW()),
(3, 2020, '2020-06-01', '2021-05-31', '2022-06-01', 30, 0, 30, 28, 2, 0, 'cerrado', 'Período casi completamente gozado', 1, NOW(), NOW()),
(3, 2021, '2021-06-01', '2022-05-31', '2023-06-01', 30, 0, 30, 30, 0, 0, 'cerrado', 'Período completamente gozado', 1, NOW(), NOW()),
(3, 2022, '2022-06-01', '2023-05-31', '2024-06-01', 30, 0, 30, 25, 5, 0, 'cerrado', 'Período parcialmente gozado', 1, NOW(), NOW()),
(3, 2023, '2023-06-01', '2024-05-31', '2025-06-01', 30, 0, 30, 18, 12, 0, 'vigente', 'Período en curso', 1, NOW(), NOW()),
(3, 2024, '2024-06-01', '2025-05-31', '2026-06-01', 30, 0, 30, 0, 30, 0, 'vigente', 'Período actual', 1, NOW(), NOW()),
-- Períodos de Ana Torres
(4, 2022, '2022-08-15', '2023-08-14', '2024-08-15', 30, 0, 30, 20, 10, 0, 'vigente', 'Período en curso', 1, NOW(), NOW()),
(4, 2023, '2023-08-15', '2024-08-14', '2025-08-15', 30, 0, 30, 10, 20, 0, 'vigente', 'Período en curso', 1, NOW(), NOW()),
(4, 2024, '2024-08-15', '2025-08-14', '2026-08-15', 30, 0, 30, 0, 30, 0, 'vigente', 'Período actual', 1, NOW(), NOW()),
-- Períodos de Roberto Flores
(5, 2018, '2018-02-20', '2019-02-19', '2020-02-20', 30, 0, 30, 30, 0, 0, 'cerrado', 'Período completamente gozado', 1, NOW(), NOW()),
(5, 2019, '2019-02-20', '2020-02-19', '2021-02-20', 30, 0, 30, 30, 0, 0, 'cerrado', 'Período completamente gozado', 1, NOW(), NOW()),
(5, 2020, '2020-02-20', '2021-02-19', '2022-02-20', 30, 0, 30, 25, 5, 0, 'cerrado', 'Período parcialmente gozado', 1, NOW(), NOW()),
(5, 2021, '2021-02-20', '2022-02-19', '2023-02-20', 30, 0, 30, 30, 0, 0, 'cerrado', 'Período completamente gozado', 1, NOW(), NOW()),
(5, 2022, '2022-02-20', '2023-02-19', '2024-02-20', 30, 0, 30, 28, 2, 0, 'cerrado', 'Período casi completamente gozado', 1, NOW(), NOW()),
(5, 2023, '2023-02-20', '2024-02-19', '2025-02-20', 30, 0, 30, 22, 8, 0, 'vigente', 'Período en curso', 1, NOW(), NOW()),
(5, 2024, '2024-02-20', '2025-02-19', '2026-02-20', 30, 0, 30, 0, 30, 0, 'vigente', 'Período actual', 1, NOW(), NOW());

-- Insertar solicitudes de vacaciones de ejemplo
INSERT IGNORE INTO `solicitudes_vacaciones` (
    `empleado_id`, `periodo_vacacional_id`, `tipo_solicitud`, 
    `fecha_inicio`, `fecha_fin`, `dias_solicitados`, 
    `motivo_solicitud`, `observaciones_empleado`, `observaciones_jefe`,
    `estado_solicitud`, `fecha_envio`, 
    `aprobado_por_jefe`, `aprobado_por_rrhh`, 
    `usuario_aprobacion_jefe_id`, `usuario_aprobacion_rrhh_id`,
    `fecha_aprobacion_jefe`, `fecha_aprobacion_rrhh`,
    `fecha_creacion`, `fecha_actualizacion`
) VALUES 
-- Solicitud aprobada de Juan García
(1, 4, 'fraccionada', '2024-07-15', '2024-07-19', 5, 'Vacaciones familiares', 'Solicito estos días para un viaje familiar', 'Aprobado. Que disfrute sus vacaciones.', 'aprobada', '2024-06-15 09:30:00', true, false, 6, NULL, '2024-06-16 14:20:00', NULL, '2024-06-15 09:30:00', '2024-06-16 14:20:00'),
-- Solicitud en revisión de María Rodríguez
(2, 9, 'completa', '2024-08-01', '2024-08-30', 30, 'Vacaciones anuales programadas', 'Solicito mis vacaciones anuales para el mes de agosto', NULL, 'en_revision', '2024-07-01 10:15:00', false, false, NULL, NULL, NULL, NULL, '2024-07-01 10:15:00', '2024-07-01 10:15:00'),
-- Solicitud enviada de Carlos Mendoza
(3, 15, 'fraccionada', '2024-09-02', '2024-09-06', 5, 'Descanso personal', 'Necesito estos días para asuntos personales', NULL, 'enviada', '2024-07-15 16:45:00', false, false, NULL, NULL, NULL, NULL, '2024-07-15 16:45:00', '2024-07-15 16:45:00'),
-- Solicitud en borrador de Ana Torres
(4, 18, 'fraccionada', '2024-10-14', '2024-10-18', 5, 'Vacaciones de cumpleaños', 'Quiero tomarme unos días por mi cumpleaños', NULL, 'borrador', NULL, false, false, NULL, NULL, NULL, NULL, NOW(), NOW());

-- Insertar historial de cambios de estado
INSERT IGNORE INTO `historial_solicitudes_vacaciones` (
    `solicitud_vacaciones_id`, `tipo_accion`, `descripcion_accion`, `estado_anterior`, `estado_nuevo`, 
    `usuario_accion_id`, `fecha_accion`
) VALUES 
(1, 'cambio_estado', 'Solicitud enviada para revisión', 'borrador', 'enviada', 2, NOW()),
(1, 'cambio_estado', 'Solicitud en proceso de revisión', 'enviada', 'en_revision', 6, NOW()),
(1, 'cambio_estado', 'Solicitud aprobada por jefe directo', 'en_revision', 'aprobada', 6, NOW()),
(2, 'cambio_estado', 'Solicitud enviada para revisión', 'borrador', 'enviada', 3, NOW()),
(2, 'cambio_estado', 'Solicitud en proceso de revisión', 'enviada', 'en_revision', 6, NOW()),
(3, 'cambio_estado', 'Solicitud enviada para revisión', 'borrador', 'enviada', 4, NOW());

-- Insertar goces de vacaciones de ejemplo
INSERT IGNORE INTO `goces_vacaciones` (
    `solicitud_vacaciones_id`, `empleado_id`, `periodo_vacacional_id`, `fecha_inicio_real`, 
    `fecha_fin_real`, `dias_gozados`, `estado_goce`, `dias_no_gozados`, `reincorporado`,
    `observaciones`, `fecha_creacion`, `fecha_actualizacion`
) VALUES 
(1, 1, 4, '2024-07-15', '2024-07-19', 5, 'completado', 0, true, 'Vacaciones familiares - Viaje a Cusco', NOW(), NOW());

-- ========================================
-- DOCUMENTOS DIGITALES DE EJEMPLO
-- ========================================

-- Insertar algunos documentos digitales de ejemplo
INSERT IGNORE INTO `documentos_digitales` (
    `empleado_id`, `tipo_documento`, `categoria`, `nombre_documento`, 
    `archivo`, `nombre_archivo_original`, `formato_archivo`, `tamano_archivo`, 
    `descripcion`, `fecha_emision`, `fecha_vencimiento`, 
    `nivel_acceso`, `requiere_autorizacion`, `es_documento_oficial`, `es_copia_certificada`,
    `version`, `es_version_actual`, `estado_documento`, `fecha_digitalizacion`, 
    `calidad_digitalizacion`, `fecha_subida`, `fecha_actualizacion`, 
    `es_confidencial`, `requiere_firma_digital`, `subido_por_id`
) VALUES 
(1, 'CONTRATO', 'laboral', 'contrato_jgarcia_2021.pdf', '/documentos/contratos/contrato_jgarcia_2021.pdf', 'contrato_jgarcia_2021.pdf', 'pdf', 245760, 'Contrato CAS de Juan García', '2021-03-15', '2024-03-15', 'publico', false, true, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), false, false, 2),
(1, 'CURRICULUM', 'personal', 'cv_jgarcia.pdf', '/documentos/cv/cv_jgarcia.pdf', 'cv_jgarcia.pdf', 'pdf', 189440, 'Curriculum Vitae de Juan García', '2021-03-10', NULL, 'publico', false, true, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), false, false, 2),
(1, 'FOTO', 'personal', 'foto_jgarcia.jpg', '/documentos/fotos/foto_jgarcia.jpg', 'foto_jgarcia.jpg', 'jpg', 156720, 'Fotografía de Juan García', '2021-03-10', NULL, 'publico', false, false, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), false, false, 2),
(2, 'CONTRATO', 'laboral', 'contrato_mrodriguez_2020.pdf', '/documentos/contratos/contrato_mrodriguez_2020.pdf', 'contrato_mrodriguez_2020.pdf', 'pdf', 251904, 'Contrato CAS de María Rodríguez', '2020-01-10', '2023-01-10', 'publico', false, true, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), false, false, 3),
(2, 'CURRICULUM', 'personal', 'cv_mrodriguez.pdf', '/documentos/cv/cv_mrodriguez.pdf', 'cv_mrodriguez.pdf', 'pdf', 198560, 'Curriculum Vitae de María Rodríguez', '2020-01-05', NULL, 'publico', false, true, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), false, false, 3),
(2, 'CERTIFICADO', 'academico', 'certificado_estudios_mrodriguez.pdf', '/documentos/certificados/certificado_estudios_mrodriguez.pdf', 'certificado_estudios_mrodriguez.pdf', 'pdf', 167890, 'Certificado de estudios superiores', '2020-01-05', NULL, 'publico', false, true, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), false, false, 3),
(3, 'CONTRATO', 'laboral', 'contrato_cmendoza_2019.pdf', '/documentos/contratos/contrato_cmendoza_2019.pdf', 'contrato_cmendoza_2019.pdf', 'pdf', 267264, 'Contrato CAP de Carlos Mendoza', '2019-06-01', '2022-06-01', 'publico', false, true, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), false, false, 4),
(3, 'CURRICULUM', 'personal', 'cv_cmendoza.pdf', '/documentos/cv/cv_cmendoza.pdf', 'cv_cmendoza.pdf', 'pdf', 203840, 'Curriculum Vitae de Carlos Mendoza', '2019-05-25', NULL, 'publico', false, true, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), false, false, 4),
(3, 'EVALUACION', 'evaluacion', 'evaluacion_desempeno_cmendoza_2023.pdf', '/documentos/evaluaciones/evaluacion_desempeno_cmendoza_2023.pdf', 'evaluacion_desempeno_cmendoza_2023.pdf', 'pdf', 145600, 'Evaluación de desempeño 2023', '2023-12-15', NULL, 'confidencial', false, true, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), true, false, 6),
(4, 'CONTRATO', 'laboral', 'contrato_atorres_2022.pdf', '/documentos/contratos/contrato_atorres_2022.pdf', 'contrato_atorres_2022.pdf', 'pdf', 234496, 'Contrato CAS de Ana Torres', '2022-08-15', '2025-08-15', 'publico', false, true, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), false, false, 5),
(4, 'CURRICULUM', 'personal', 'cv_atorres.pdf', '/documentos/cv/cv_atorres.pdf', 'cv_atorres.pdf', 'pdf', 187320, 'Curriculum Vitae de Ana Torres', '2022-08-10', NULL, 'publico', false, true, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), false, false, 5),
(5, 'CONTRATO', 'laboral', 'contrato_rflores_2018.pdf', '/documentos/contratos/contrato_rflores_2018.pdf', 'contrato_rflores_2018.pdf', 'pdf', 278528, 'Contrato CAP de Roberto Flores', '2018-02-20', '2021-02-20', 'publico', false, true, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), false, false, 6),
(5, 'CURRICULUM', 'personal', 'cv_rflores.pdf', '/documentos/cv/cv_rflores.pdf', 'cv_rflores.pdf', 'pdf', 212480, 'Curriculum Vitae de Roberto Flores', '2018-02-15', NULL, 'publico', false, true, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), false, false, 6),
(5, 'CERTIFICADO', 'academico', 'certificado_capacitacion_rflores.pdf', '/documentos/certificados/certificado_capacitacion_rflores.pdf', 'certificado_capacitacion_rflores.pdf', 'pdf', 134560, 'Certificado de capacitación en gestión de RRHH', '2023-06-20', NULL, 'publico', false, true, false, '1', true, 'activo', NOW(), 'alta', NOW(), NOW(), false, false, 6);

-- ========================================
-- DATOS ACADÉMICOS DE EJEMPLO
-- ========================================

-- Insertar información académica de ejemplo
INSERT IGNORE INTO `datos_academicos` (
    `empleado_id`, `nivel_educativo`, `nombre_institucion`, `tipo_institucion`, `modalidad_estudio`,
    `nombre_carrera`, `codigo_carrera`, `area_conocimiento`, `duracion_anos`, `duracion_semestres`,
    `fecha_inicio`, `fecha_fin`, `fecha_graduacion`, `estado_estudios`, `promedio_ponderado`,
    `creditos_aprobados`, `creditos_totales`, `numero_titulo`, `numero_diploma`, `numero_colegiatura`,
    `colegio_profesional`, `pais_institucion`, `departamento_institucion`, `provincia_institucion`,
    `distrito_institucion`, `mencion_especialidad`, `tesis_titulo`, `reconocimientos`, `ruta_certificado`,
    `ruta_titulo`, `ruta_diploma`, `verificado_sunedu`, `fecha_verificacion_sunedu`, `codigo_verificacion_sunedu`,
    `estado_registro`, `observaciones`, `fecha_registro`, `fecha_actualizacion`
) VALUES 
(1, 'UNIVERSITARIO', 'Universidad Nacional de Ingeniería', 'PUBLICA', 'PRESENCIAL', 'Ingeniería de Sistemas', 'IS-001', 'INGENIERIA', 5.0, 10, '2003-03-01', '2008-12-15', '2009-02-20', 'COMPLETADO', 15.50, 220, 220, 'T-2009-001234', 'D-2009-001234', 'CIP-123456', 'Colegio de Ingenieros del Perú', 'PERU', 'LIMA', 'LIMA', 'RIMAC', NULL, 'Sistema de Gestión de Recursos Humanos', NULL, '/docs/cert1.pdf', '/docs/titulo1.pdf', '/docs/diploma1.pdf', true, '2009-03-01', 'SUNEDU-001234', 'ACTIVO', NULL, NOW(), NOW()),
(1, 'TECNICO', 'TECSUP', 'PRIVADA', 'PRESENCIAL', 'Redes y Comunicaciones', 'RC-002', 'TECNOLOGIA', 2.0, 4, '2001-03-01', '2002-12-15', '2003-01-25', 'COMPLETADO', 16.20, 120, 120, 'T-2003-005678', 'D-2003-005678', NULL, NULL, 'PERU', 'LIMA', 'LIMA', 'LA MOLINA', NULL, 'Implementación de Red Corporativa', NULL, '/docs/cert2.pdf', '/docs/titulo2.pdf', '/docs/diploma2.pdf', false, NULL, NULL, 'ACTIVO', NULL, NOW(), NOW()),
(2, 'UNIVERSITARIO', 'Universidad Nacional Mayor de San Marcos', 'PUBLICA', 'PRESENCIAL', 'Administración', 'ADM-003', 'ADMINISTRACION', 5.0, 10, '2008-03-01', '2013-12-15', '2014-03-10', 'COMPLETADO', 14.80, 200, 200, 'T-2014-002345', 'D-2014-002345', NULL, NULL, 'PERU', 'LIMA', 'LIMA', 'CERCADO DE LIMA', NULL, 'Gestión Estratégica en Organizaciones Públicas', NULL, '/docs/cert3.pdf', '/docs/titulo3.pdf', '/docs/diploma3.pdf', true, '2014-04-01', 'SUNEDU-002345', 'ACTIVO', NULL, NOW(), NOW()),
(2, 'POSTGRADO', 'Universidad del Pacífico', 'PRIVADA', 'PRESENCIAL', 'Maestría en Gestión Pública', 'MGP-004', 'ADMINISTRACION', 2.0, 4, '2023-03-01', NULL, NULL, 'EN_CURSO', NULL, 45, 60, NULL, NULL, NULL, NULL, 'PERU', 'LIMA', 'LIMA', 'JESUS MARIA', NULL, NULL, NULL, NULL, NULL, NULL, false, NULL, NULL, 'ACTIVO', 'Estudios en curso', NOW(), NOW()),
(3, 'UNIVERSITARIO', 'Pontificia Universidad Católica del Perú', 'PRIVADA', 'PRESENCIAL', 'Ingeniería Informática', 'II-005', 'INGENIERIA', 5.0, 10, '2006-03-01', '2011-12-15', '2012-02-15', 'COMPLETADO', 16.80, 230, 230, 'T-2012-003456', 'D-2012-003456', 'CIP-234567', 'Colegio de Ingenieros del Perú', 'PERU', 'LIMA', 'LIMA', 'SAN MIGUEL', NULL, 'Sistema de Información Gerencial', NULL, '/docs/cert4.pdf', '/docs/titulo4.pdf', '/docs/diploma4.pdf', true, '2012-03-01', 'SUNEDU-003456', 'ACTIVO', NULL, NOW(), NOW()),
(3, 'POSTGRADO', 'Universidad ESAN', 'PRIVADA', 'PRESENCIAL', 'MBA Ejecutivo', 'MBA-006', 'ADMINISTRACION', 2.0, 4, '2015-03-01', '2017-12-15', '2018-01-20', 'COMPLETADO', 17.20, 48, 48, 'T-2018-001111', 'D-2018-001111', NULL, NULL, 'PERU', 'LIMA', 'LIMA', 'SURCO', NULL, 'Estrategias de Transformación Digital', NULL, '/docs/cert5.pdf', '/docs/titulo5.pdf', '/docs/diploma5.pdf', true, '2018-02-01', 'SUNEDU-001111', 'ACTIVO', NULL, NOW(), NOW()),
(4, 'UNIVERSITARIO', 'Universidad de Lima', 'PRIVADA', 'PRESENCIAL', 'Contabilidad', 'CONT-007', 'CONTABILIDAD', 5.0, 10, '2010-03-01', '2015-12-15', '2016-03-05', 'COMPLETADO', 15.90, 210, 210, 'T-2016-004567', 'D-2016-004567', 'CCPL-345678', 'Colegio de Contadores Públicos de Lima', 'PERU', 'LIMA', 'LIMA', 'SANTIAGO DE SURCO', NULL, 'Auditoría Financiera en el Sector Público', NULL, '/docs/cert6.pdf', '/docs/titulo6.pdf', '/docs/diploma6.pdf', true, '2016-04-01', 'SUNEDU-004567', 'ACTIVO', NULL, NOW(), NOW()),
(4, 'TECNICO', 'Instituto San Ignacio de Loyola', 'PRIVADA', 'PRESENCIAL', 'Finanzas Corporativas', 'FC-008', 'FINANZAS', 1.5, 3, '2016-06-01', '2017-12-15', '2018-02-10', 'COMPLETADO', 16.50, 90, 90, 'T-2018-002222', 'D-2018-002222', NULL, NULL, 'PERU', 'LIMA', 'LIMA', 'LA MOLINA', NULL, 'Análisis Financiero para PYMES', NULL, '/docs/cert7.pdf', '/docs/titulo7.pdf', '/docs/diploma7.pdf', false, NULL, NULL, 'ACTIVO', NULL, NOW(), NOW()),
(5, 'UNIVERSITARIO', 'Universidad Nacional Federico Villarreal', 'PUBLICA', 'PRESENCIAL', 'Psicología', 'PSI-009', 'PSICOLOGIA', 5.0, 10, '2000-03-01', '2005-12-15', '2006-02-28', 'COMPLETADO', 15.20, 240, 240, 'T-2006-005678', 'D-2006-005678', 'CPsP-456789', 'Colegio de Psicólogos del Perú', 'PERU', 'LIMA', 'LIMA', 'CERCADO DE LIMA', 'PSICOLOGIA ORGANIZACIONAL', 'Clima Organizacional y Productividad Laboral', NULL, '/docs/cert8.pdf', '/docs/titulo8.pdf', '/docs/diploma8.pdf', true, '2006-03-15', 'SUNEDU-005678', 'ACTIVO', NULL, NOW(), NOW()),
(5, 'POSTGRADO', 'Universidad Ricardo Palma', 'PRIVADA', 'PRESENCIAL', 'Maestría en Gestión del Talento Humano', 'MGTH-010', 'PSICOLOGIA', 2.0, 4, '2010-03-01', '2012-12-15', '2013-01-15', 'COMPLETADO', 17.80, 52, 52, 'T-2013-003333', 'D-2013-003333', NULL, NULL, 'PERU', 'LIMA', 'LIMA', 'SURCO', 'GESTION DE RECURSOS HUMANOS', 'Modelo de Competencias para el Sector Público', NULL, '/docs/cert9.pdf', '/docs/titulo9.pdf', '/docs/diploma9.pdf', true, '2013-02-01', 'SUNEDU-003333', 'ACTIVO', NULL, NOW(), NOW());

-- ========================================
-- EMPLEADOS ADICIONALES PARA DEMO COMPLETA
-- ========================================

-- Insertar más empleados para una demo más completa
INSERT IGNORE INTO `empleado` (
    `numero_documento`, `tipo_documento`, `nombres_empleado`, 
    `apellido_paterno`, `apellido_materno`, `numero_ruc`, `genero_empleado`, 
    `fecha_nacimiento`, `es_padre_familia`, `sistema_pensiones`, 
    `telefono_celular`, `correo_personal`, `estado_civil`, 
    `direccion_domicilio`, `distrito_domicilio`, `provincia_domicilio`, 
    `departamento_domicilio`, `entidad_bancaria`, `numero_cuenta_bancaria`, 
    `numero_cci`, `estado_empleado`
) VALUES 
('99887766', 'DNI', 'Luis Fernando', 'Vargas', 'Morales', '10998877661', 'masculino', '1987-12-08', false, 'AFP', '987654326', 'luis.vargas@email.com', 'soltero', 'Av. Sexta 987', 'Lima', 'Lima', 'Lima', 'Banco de Crédito', '6789012345678901', '00267890123456789012', 'activo'),
('66554433', 'DNI', 'Carmen Rosa', 'Jiménez', 'Herrera', '10665544331', 'femenino', '1991-04-25', true, 'ONP', '987654327', 'carmen.jimenez@email.com', 'casado', 'Jr. Séptima 654', 'Lima', 'Lima', 'Lima', 'Interbank', '7890123456789012', '00278901234567890123', 'activo'),
('33221100', 'DNI', 'Pedro Antonio', 'Salinas', 'Ramos', '10332211001', 'masculino', '1989-08-14', true, 'AFP', '987654328', 'pedro.salinas@email.com', 'casado', 'Calle Octava 321', 'Lima', 'Lima', 'Lima', 'Scotiabank', '8901234567890123', '00289012345678901234', 'inactivo');

-- Insertar usuarios adicionales
INSERT IGNORE INTO `usuarios` (
    `password`, `last_login`, `is_superuser`, `username`, `nombres_usuario`, `apellidos_usuario`, 
    `email`, `is_staff`, `is_active`, `date_joined`, `empleado_id`, 
    `tipo_usuario`, `nivel_acceso`, `intentos_fallidos`, 
    `fecha_bloqueo`, `requiere_cambio_password`, `estado_usuario`, 
    `sesiones_simultaneas_permitidas`, `recibir_notificaciones_email`, `recibir_notificaciones_sistema`,
    `fecha_creacion`, `fecha_actualizacion`
) VALUES
('pbkdf2_sha256$600000$randomsalt7$hashedpassword7', NULL, false, 'lvargas', 'Luis Fernando', 'Vargas Morales', 'lvargas@institucion.gob.pe', false, true, NOW(), 6, 'empleado', 'usuario', 0, NULL, false, 'activo', 1, true, true, NOW(), NOW()),
('pbkdf2_sha256$600000$randomsalt8$hashedpassword8', NULL, false, 'cjimenez', 'Carmen Rosa', 'Jiménez Herrera', 'cjimenez@institucion.gob.pe', false, true, NOW(), 7, 'empleado', 'usuario', 0, NULL, false, 'activo', 1, true, true, NOW(), NOW()),
('pbkdf2_sha256$600000$randomsalt9$hashedpassword9', NULL, false, 'psalinas', 'Pedro Antonio', 'Salinas Ramos', 'psalinas@institucion.gob.pe', false, true, NOW(), 8, 'empleado', 'usuario', 0, NULL, false, 'inactivo', 1, true, true, NOW(), NOW());

-- Asignar roles a nuevos usuarios (usando subconsultas para obtener IDs dinámicamente)
INSERT IGNORE INTO `usuario_roles` (`usuario_id`, `rol_id`, `fecha_asignacion`, `estado_asignacion`) 
SELECT u.usuario_id, r.rol_id, NOW(), 'activo'
FROM usuarios u, rol r
WHERE (u.username = 'lvargas' AND r.nombre_rol = 'Empleado')
   OR (u.username = 'cjimenez' AND r.nombre_rol = 'Analista RRHH')
   OR (u.username = 'psalinas' AND r.nombre_rol = 'Empleado');

-- Insertar datos laborales para nuevos empleados
INSERT IGNORE INTO `datos_laborales` (
    `empleado_id`, `area_id`, `cargo_empleado`, `codigo_puesto`, `nivel_puesto`,
    `categoria`, `tipo_contrato`, `regimen_laboral`, `modalidad_trabajo`, 
    `jornada_laboral`, `fecha_ingreso`, `fecha_inicio_contrato`, `fecha_fin_contrato`,
    `sueldo_basico`, `asignacion_familiar`, `bonificacion_especial`, `otras_bonificaciones`,
    `horario_entrada`, `horario_salida`, `horas_semanales`, `estado_datos`, 
    `observaciones`, `fecha_registro`, `fecha_actualizacion`, `jefe_directo_id`
) VALUES 
(6, 1, 'Desarrollador de Software', 'DEV001', 'I', 'SP-ES', 'CAS', 'CAS', 'presencial', 'completa', '2023-05-10', '2023-05-10', '2024-05-09', 3200.00, 93.00, 0.00, 0.00, '08:00:00', '17:00:00', 40.00, 'activo', 'Desarrollador especializado en aplicaciones web', NOW(), NOW(), 1),
(7, 2, 'Asistente de RRHH', 'RRHH002', 'I', 'SP-AP', 'CAS', 'CAS', 'presencial', 'completa', '2022-11-20', '2022-11-20', '2023-11-19', 2800.00, 93.00, 0.00, 0.00, '08:00:00', '17:00:00', 40.00, 'activo', 'Asistente administrativo en recursos humanos', NOW(), NOW(), 2),
(8, 3, 'Analista Contable', 'CONT001', 'I', 'SP-ES', 'CAS', 'CAS', 'presencial', 'completa', '2021-09-15', '2021-09-15', '2022-09-14', 3300.00, 93.00, 0.00, 0.00, '08:00:00', '17:00:00', 40.00, 'inactivo', 'Analista contable especializado en presupuesto público', NOW(), NOW(), 3);

-- Insertar historial de ubicaciones de ejemplo
INSERT IGNORE INTO `historial_ubicaciones` (
    `empleado_id`, `area_origen_id`, `area_destino_id`, `tipo_movimiento`, 
    `fecha_inicio`, `fecha_termino`, `motivo_movimiento`, `documento_sustento`,
    `numero_documento_sustento`, `observaciones`, `estado_ubicacion`, 
    `fecha_registro`, `registrado_por_usuario_id`
) VALUES 
-- Movimiento de Juan García de TI a Administración
(1, 1, 4, 'traslado', '2023-03-15', '2023-12-31', 'Apoyo temporal en proyectos administrativos', 'Memorándum', 'MEM-2023-045', 'Traslado temporal por necesidades del servicio', 'activo', '2023-03-10 10:30:00', 1),
-- Movimiento de María Rodríguez dentro de RRHH (cambio de ubicación física)
(2, 2, 2, 'reubicacion', '2023-06-01', NULL, 'Cambio de oficina por remodelación', 'Oficio', 'OF-2023-078', 'Reubicación temporal por obras de infraestructura', 'activo', '2023-05-25 14:20:00', 2),
-- Movimiento histórico de Carlos Mendoza
(3, 3, 1, 'traslado', '2022-01-10', '2022-12-31', 'Fortalecimiento del área de sistemas', 'Resolución', 'RES-2022-012', 'Traslado definitivo por reorganización institucional', 'finalizado', '2021-12-20 09:15:00', 1),
-- Retorno de Carlos Mendoza a Contabilidad
(3, 1, 3, 'traslado', '2023-01-02', NULL, 'Retorno al área de origen', 'Memorándum', 'MEM-2023-001', 'Culminación de apoyo en sistemas, retorno a contabilidad', 'activo', '2022-12-15 16:45:00', 1);

-- ========================================
-- MENSAJE DE CONFIRMACIÓN FINAL
-- ========================================

SELECT 
    'DATOS DEMO DJANGO COMPLETADOS!' as mensaje,
    'Sistema configurado con estructura Django refactorizada' as estado,
    'Usuarios creados con contraseñas Django hasheadas' as credenciales,
    'Base de datos lista para demostración con Django' as nota_final,
    '8 empleados, 4 áreas, múltiples solicitudes y períodos vacacionales' as contenido_demo,
    'Compatible con estructura-django-refactorizada.sql' as compatibilidad;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

-- ========================================
-- FIN DE DATOS DEMO DJANGO REFACTORIZADO
-- ========================================