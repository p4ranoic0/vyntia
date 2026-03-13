-- ========================================
-- SISTEMA DE INTRANET RRHH - VISTAS Y FUNCIONES
-- Versión: 2.0
-- Fecha: 2025
-- Descripción: Vistas para reportes y funciones auxiliares del sistema
-- ========================================

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

USE `bd_rrhh_intranet`;

-- ========================================
-- VISTAS DEL MÓDULO DE VACACIONES
-- ========================================

-- Vista para reporte de saldos vacacionales por empleado
DROP VIEW IF EXISTS `v_saldos_vacacionales`;
CREATE VIEW `v_saldos_vacacionales` AS
SELECT 
    e.empleado_id,
    e.numero_documento,
    e.nombres_empleado,
    e.apellido_paterno,
    e.apellido_materno,
    CONCAT(e.nombres_empleado, ' ', e.apellido_paterno, ' ', e.apellido_materno) as nombre_completo,
    dl.puesto_trabajo,
    a.nombre_unidad_organica as area,
    pv.anio_periodo,
    pv.fecha_inicio_periodo,
    pv.fecha_fin_periodo,
    pv.dias_generados,
    pv.dias_gozados,
    pv.dias_pendientes,
    pv.fecha_vencimiento,
    pv.estado_periodo,
    DATEDIFF(pv.fecha_vencimiento, CURDATE()) as dias_para_vencer
FROM empleados e
INNER JOIN datos_laborales dl ON e.empleado_id = dl.empleado_id
INNER JOIN areas a ON dl.area_id = a.area_id
INNER JOIN periodos_vacacionales pv ON e.empleado_id = pv.empleado_id
WHERE e.estado_empleado = 'activo'
AND dl.estado_laboral = 'activo'
ORDER BY e.apellido_paterno, e.apellido_materno, e.nombres_empleado, pv.anio_periodo;

-- Vista para reporte de solicitudes de vacaciones
DROP VIEW IF EXISTS `v_solicitudes_vacaciones`;
CREATE VIEW `v_solicitudes_vacaciones` AS
SELECT 
    sv.solicitud_id,
    sv.numero_solicitud,
    e.numero_documento,
    CONCAT(e.nombres_empleado, ' ', e.apellido_paterno, ' ', e.apellido_materno) as nombre_completo,
    dl.puesto_trabajo,
    a.nombre_unidad_organica as area,
    pv.anio_periodo,
    sv.tipo_solicitud,
    sv.fecha_inicio_solicitud,
    sv.fecha_fin_solicitud,
    sv.dias_solicitados,
    sv.dias_habiles_solicitados,
    sv.incluye_fines_semana,
    sv.estado_solicitud,
    sv.fecha_envio,
    sv.fecha_respuesta,
    CONCAT(er.nombres_empleado, ' ', er.apellido_paterno) as revisado_por,
    sv.observaciones_jefe
FROM solicitudes_vacaciones sv
INNER JOIN empleados e ON sv.empleado_id = e.empleado_id
INNER JOIN datos_laborales dl ON e.empleado_id = dl.empleado_id
INNER JOIN areas a ON dl.area_id = a.area_id
INNER JOIN periodos_vacacionales pv ON sv.periodo_id = pv.periodo_id
LEFT JOIN usuarios u ON sv.revisado_por_usuario_id = u.usuario_id
LEFT JOIN empleados er ON u.empleado_id = er.empleado_id
ORDER BY sv.fecha_envio DESC;

-- Vista para reporte de goces de vacaciones
DROP VIEW IF EXISTS `v_goces_vacaciones`;
CREATE VIEW `v_goces_vacaciones` AS
SELECT 
    gv.goce_id,
    sv.numero_solicitud,
    e.numero_documento,
    CONCAT(e.nombres_empleado, ' ', e.apellido_paterno, ' ', e.apellido_materno) as nombre_completo,
    dl.puesto_trabajo,
    a.nombre_unidad_organica as area,
    pv.anio_periodo,
    gv.fecha_inicio_goce,
    gv.fecha_fin_goce,
    gv.dias_gozados,
    gv.tipo_goce,
    gv.incluyo_fines_semana,
    gv.documento_autorizacion,
    gv.numero_documento_autorizacion,
    gv.fecha_registro
FROM goces_vacaciones gv
INNER JOIN solicitudes_vacaciones sv ON gv.solicitud_id = sv.solicitud_id
INNER JOIN empleados e ON gv.empleado_id = e.empleado_id
INNER JOIN datos_laborales dl ON e.empleado_id = dl.empleado_id
INNER JOIN areas a ON dl.area_id = a.area_id
INNER JOIN periodos_vacacionales pv ON gv.periodo_id = pv.periodo_id
ORDER BY gv.fecha_inicio_goce DESC;

-- ========================================
-- VISTAS PARA REPORTES ADMINISTRATIVOS
-- ========================================

-- Vista para reporte de empleados activos
DROP VIEW IF EXISTS `v_empleados_activos`;
CREATE VIEW `v_empleados_activos` AS
SELECT 
    e.empleado_id,
    e.numero_documento,
    e.tipo_documento,
    CONCAT(e.nombres_empleado, ' ', e.apellido_paterno, ' ', e.apellido_materno) as nombre_completo,
    e.fecha_nacimiento,
    TIMESTAMPDIFF(YEAR, e.fecha_nacimiento, CURDATE()) as edad,
    e.genero_empleado,
    e.telefono_celular,
    e.correo_personal,
    dl.fecha_ingreso,
dl.puesto_trabajo,
    TIMESTAMPDIFF(YEAR, dl.fecha_ingreso, CURDATE()) as anos_servicio,
    dl.regimen_laboral,
    dl.condicion_laboral,
    a.nombre_unidad_organica as area,
    dl.estado_laboral,
    e.estado_empleado
FROM empleados e
INNER JOIN datos_laborales dl ON e.empleado_id = dl.empleado_id
INNER JOIN areas a ON dl.area_id = a.area_id
WHERE e.estado_empleado = 'activo'
AND dl.estado_laboral = 'activo'
ORDER BY e.apellido_paterno, e.apellido_materno, e.nombres_empleado;

-- Vista para reporte de usuarios del sistema
DROP VIEW IF EXISTS `v_usuarios_sistema`;
CREATE VIEW `v_usuarios_sistema` AS
SELECT 
    u.usuario_id,
    u.nombre_usuario,
    CONCAT(e.nombres_empleado, ' ', e.apellido_paterno, ' ', e.apellido_materno) as nombre_completo,
    u.correo_institucional,
    u.estado_usuario,
    u.fecha_creacion,
    u.ultimo_acceso,
    GROUP_CONCAT(r.nombre_rol SEPARATOR ', ') as roles_asignados,
    a.nombre_unidad_organica as area
FROM usuarios u
INNER JOIN empleados e ON u.empleado_id = e.empleado_id
INNER JOIN datos_laborales dl ON e.empleado_id = dl.empleado_id
INNER JOIN areas a ON dl.area_id = a.area_id
LEFT JOIN usuario_roles ur ON u.usuario_id = ur.usuario_id
LEFT JOIN roles r ON ur.rol_id = r.rol_id
GROUP BY u.usuario_id, u.nombre_usuario, nombre_completo, u.correo_institucional, 
         u.estado_usuario, u.fecha_creacion, u.ultimo_acceso, a.nombre_unidad_organica
ORDER BY e.apellido_paterno, e.apellido_materno, e.nombres_empleado;

-- Vista para reporte de documentos digitales
DROP VIEW IF EXISTS `v_documentos_digitales`;
CREATE VIEW `v_documentos_digitales` AS
SELECT 
    dd.documento_id,
    CONCAT(e.nombres_empleado, ' ', e.apellido_paterno, ' ', e.apellido_materno) as nombre_completo,
    e.numero_documento,
    dd.tipo_documento,
    dd.nombre_archivo,
    dd.ruta_archivo,
    dd.tamano_archivo,
    ROUND(dd.tamano_archivo / 1024 / 1024, 2) as tamano_mb,
    dd.fecha_subida,
    dd.estado_documento,
    CONCAT(eu.nombres_empleado, ' ', eu.apellido_paterno) as subido_por
FROM documentos_digitales dd
INNER JOIN empleados e ON dd.empleado_id = e.empleado_id
LEFT JOIN usuarios u ON dd.subido_por_usuario_id = u.usuario_id
LEFT JOIN empleados eu ON u.empleado_id = eu.empleado_id
ORDER BY dd.fecha_subida DESC;

-- Vista de auditoría de accesos al sistema
DROP VIEW IF EXISTS `v_auditoria_accesos`;
CREATE VIEW `v_auditoria_accesos` AS
SELECT 
    aa.acceso_id,
    u.nombre_usuario,
    CONCAT(e.nombres_empleado, ' ', e.apellido_paterno, ' ', e.apellido_materno) as nombre_completo,
    aa.fecha_acceso,
    aa.direccion_ip,
    aa.user_agent,
    aa.modulo_accedido,
    aa.accion_realizada,
    aa.resultado_acceso,
    aa.detalles_adicionales
FROM auditoria_accesos aa
LEFT JOIN usuarios u ON aa.usuario_id = u.usuario_id
LEFT JOIN empleados e ON u.empleado_id = e.empleado_id
ORDER BY aa.fecha_acceso DESC;

-- Vista para dashboard de vacaciones próximas a vencer
DROP VIEW IF EXISTS `v_vacaciones_por_vencer`;
CREATE VIEW `v_vacaciones_por_vencer` AS
SELECT 
    e.empleado_id,
    e.numero_documento,
    CONCAT(e.nombres_empleado, ' ', e.apellido_paterno, ' ', e.apellido_materno) as nombre_completo,
    a.nombre_unidad_organica as area,
    pv.anio_periodo,
    pv.dias_pendientes,
    pv.fecha_vencimiento,
    DATEDIFF(pv.fecha_vencimiento, CURDATE()) as dias_para_vencer
FROM empleados e
INNER JOIN datos_laborales dl ON e.empleado_id = dl.empleado_id
INNER JOIN areas a ON dl.area_id = a.area_id
INNER JOIN periodos_vacacionales pv ON e.empleado_id = pv.empleado_id
WHERE e.estado_empleado = 'activo'
AND dl.estado_laboral = 'activo'
AND pv.estado_periodo = 'vigente'
AND pv.dias_pendientes > 0
AND DATEDIFF(pv.fecha_vencimiento, CURDATE()) <= 90
ORDER BY dias_para_vencer ASC;

-- Vista para solicitudes pendientes de aprobación
DROP VIEW IF EXISTS `v_solicitudes_pendientes`;
CREATE VIEW `v_solicitudes_pendientes` AS
SELECT 
    sv.solicitud_id,
    sv.numero_solicitud,
    CONCAT(e.nombres_empleado, ' ', e.apellido_paterno, ' ', e.apellido_materno) as nombre_completo,
    a.nombre_unidad_organica as area,
    sv.fecha_inicio_solicitud,
    sv.fecha_fin_solicitud,
    sv.dias_solicitados,
    sv.fecha_envio,
    DATEDIFF(CURDATE(), sv.fecha_envio) as dias_pendientes,
    sv.estado_solicitud
FROM solicitudes_vacaciones sv
INNER JOIN empleados e ON sv.empleado_id = e.empleado_id
INNER JOIN datos_laborales dl ON e.empleado_id = dl.empleado_id
INNER JOIN areas a ON dl.area_id = a.area_id
WHERE sv.estado_solicitud IN ('enviada', 'en_revision')
ORDER BY sv.fecha_envio ASC;



/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

-- ========================================
-- FIN DE VISTAS DEL SISTEMA
-- ========================================