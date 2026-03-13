-- ========================================
-- SISTEMA DE INTRANET RRHH - TRIGGERS
-- Versión: 2.0
-- Fecha: 2025
-- Descripción: Triggers del sistema para automatización y auditoría
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
-- TRIGGERS DEL MÓDULO DE VACACIONES
-- ========================================

DELIMITER //

-- Trigger para actualizar días gozados al insertar un goce
DROP TRIGGER IF EXISTS `tr_actualizar_dias_gozados_insert`//
CREATE TRIGGER `tr_actualizar_dias_gozados_insert`
AFTER INSERT ON `goces_vacaciones`
FOR EACH ROW
BEGIN
    UPDATE `periodos_vacacionales` 
    SET `dias_gozados` = `dias_gozados` + NEW.`dias_gozados`
    WHERE `periodo_id` = NEW.`periodo_id`;
END//

-- Trigger para actualizar días gozados al modificar un goce
DROP TRIGGER IF EXISTS `tr_actualizar_dias_gozados_update`//
CREATE TRIGGER `tr_actualizar_dias_gozados_update`
AFTER UPDATE ON `goces_vacaciones`
FOR EACH ROW
BEGIN
    UPDATE `periodos_vacacionales` 
    SET `dias_gozados` = `dias_gozados` - OLD.`dias_gozados` + NEW.`dias_gozados`
    WHERE `periodo_id` = NEW.`periodo_id`;
END//

-- Trigger para actualizar días gozados al eliminar un goce
DROP TRIGGER IF EXISTS `tr_actualizar_dias_gozados_delete`//
CREATE TRIGGER `tr_actualizar_dias_gozados_delete`
AFTER DELETE ON `goces_vacaciones`
FOR EACH ROW
BEGIN
    UPDATE `periodos_vacacionales` 
    SET `dias_gozados` = `dias_gozados` - OLD.`dias_gozados`
    WHERE `periodo_id` = OLD.`periodo_id`;
END//

-- Trigger para generar número correlativo de solicitud
DROP TRIGGER IF EXISTS `tr_generar_numero_solicitud`//
CREATE TRIGGER `tr_generar_numero_solicitud`
BEFORE INSERT ON `solicitudes_vacaciones`
FOR EACH ROW
BEGIN
    DECLARE siguiente_numero INT;
    DECLARE anio_actual YEAR;
    
    SET anio_actual = YEAR(CURDATE());
    
    SELECT COALESCE(MAX(CAST(SUBSTRING_INDEX(numero_solicitud, '-', -1) AS UNSIGNED)), 0) + 1
    INTO siguiente_numero
    FROM solicitudes_vacaciones
    WHERE numero_solicitud LIKE CONCAT('VAC-', anio_actual, '-%');
    
    SET NEW.numero_solicitud = CONCAT('VAC-', anio_actual, '-', LPAD(siguiente_numero, 4, '0'));
END//

-- Trigger para registrar historial de cambios de estado
DROP TRIGGER IF EXISTS `tr_historial_estado_solicitud`//
CREATE TRIGGER `tr_historial_estado_solicitud`
AFTER UPDATE ON `solicitudes_vacaciones`
FOR EACH ROW
BEGIN
    IF OLD.estado_solicitud != NEW.estado_solicitud THEN
        INSERT INTO `historial_solicitudes_vacaciones` (
            `solicitud_id`,
            `estado_anterior`,
            `estado_nuevo`,
            `usuario_cambio_id`
        ) VALUES (
            NEW.solicitud_id,
            OLD.estado_solicitud,
            NEW.estado_solicitud,
            NEW.revisado_por_usuario_id
        );
    END IF;
END//

-- ========================================
-- TRIGGERS DE AUDITORÍA GENERAL
-- ========================================

-- Trigger para auditar cambios en empleados
DROP TRIGGER IF EXISTS `tr_auditoria_empleados_update`//
CREATE TRIGGER `tr_auditoria_empleados_update`
AFTER UPDATE ON `empleados`
FOR EACH ROW
BEGIN
    INSERT INTO `auditoria_cambios` (
        `tabla_afectada`,
        `registro_id`,
        `tipo_operacion`,
        `valores_anteriores`,
        `valores_nuevos`,
        `usuario_id`,
        `direccion_ip`
    ) VALUES (
        'empleados',
        NEW.empleado_id,
        'UPDATE',
        JSON_OBJECT(
            'numero_documento', OLD.numero_documento,
            'nombres_empleado', OLD.nombres_empleado,
            'apellido_paterno', OLD.apellido_paterno,
            'apellido_materno', OLD.apellido_materno,
            'estado_empleado', OLD.estado_empleado
        ),
        JSON_OBJECT(
            'numero_documento', NEW.numero_documento,
            'nombres_empleado', NEW.nombres_empleado,
            'apellido_paterno', NEW.apellido_paterno,
            'apellido_materno', NEW.apellido_materno,
            'estado_empleado', NEW.estado_empleado
        ),
        @current_user_id,
        @current_user_ip
    );
END//

-- Trigger para auditar cambios en usuarios
DROP TRIGGER IF EXISTS `tr_auditoria_usuarios_update`//
CREATE TRIGGER `tr_auditoria_usuarios_update`
AFTER UPDATE ON `usuarios`
FOR EACH ROW
BEGIN
    INSERT INTO `auditoria_cambios` (
        `tabla_afectada`,
        `registro_id`,
        `tipo_operacion`,
        `valores_anteriores`,
        `valores_nuevos`,
        `usuario_id`,
        `direccion_ip`
    ) VALUES (
        'usuarios',
        NEW.usuario_id,
        'UPDATE',
        JSON_OBJECT(
            'nombre_usuario', OLD.nombre_usuario,
            'correo_institucional', OLD.correo_institucional,
            'estado_usuario', OLD.estado_usuario,
            'ultimo_acceso', OLD.ultimo_acceso
        ),
        JSON_OBJECT(
            'nombre_usuario', NEW.nombre_usuario,
            'correo_institucional', NEW.correo_institucional,
            'estado_usuario', NEW.estado_usuario,
            'ultimo_acceso', NEW.ultimo_acceso
        ),
        @current_user_id,
        @current_user_ip
    );
END//

-- Trigger para auditar cambios en datos laborales
DROP TRIGGER IF EXISTS `tr_auditoria_datos_laborales_update`//
CREATE TRIGGER `tr_auditoria_datos_laborales_update`
AFTER UPDATE ON `datos_laborales`
FOR EACH ROW
BEGIN
    INSERT INTO `auditoria_cambios` (
        `tabla_afectada`,
        `registro_id`,
        `tipo_operacion`,
        `valores_anteriores`,
        `valores_nuevos`,
        `usuario_id`,
        `direccion_ip`
    ) VALUES (
        'datos_laborales',
        NEW.empleado_id,
        'UPDATE',
        JSON_OBJECT(
            'fecha_ingreso', OLD.fecha_ingreso,
            'puesto_trabajo', OLD.puesto_trabajo,
            'area_id', OLD.area_id,
            'estado_laboral', OLD.estado_laboral,
            'regimen_laboral', OLD.regimen_laboral,
            'condicion_laboral', OLD.condicion_laboral,
            'remuneracion_mensual', OLD.remuneracion_mensual
        ),
        JSON_OBJECT(
            'fecha_ingreso', NEW.fecha_ingreso,
            'puesto_trabajo', NEW.puesto_trabajo,
            'area_id', NEW.area_id,
            'estado_laboral', NEW.estado_laboral,
            'regimen_laboral', NEW.regimen_laboral,
            'condicion_laboral', NEW.condicion_laboral,
            'remuneracion_mensual', NEW.remuneracion_mensual
        ),
        @current_user_id,
        @current_user_ip
    );
END//

-- ========================================
-- TRIGGERS DE VALIDACIÓN Y CONTROL
-- ========================================

-- Trigger para validar fechas en solicitudes de vacaciones
DROP TRIGGER IF EXISTS `tr_validar_fechas_solicitud`//
CREATE TRIGGER `tr_validar_fechas_solicitud`
BEFORE INSERT ON `solicitudes_vacaciones`
FOR EACH ROW
BEGIN
    -- Validar que la fecha de inicio no sea mayor a la fecha de fin
    IF NEW.fecha_inicio_solicitud > NEW.fecha_fin_solicitud THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'La fecha de inicio no puede ser mayor a la fecha de fin';
    END IF;
    
    -- Validar que las fechas no sean en el pasado
    IF NEW.fecha_inicio_solicitud < CURDATE() THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'No se pueden solicitar vacaciones para fechas pasadas';
    END IF;
    
    -- Establecer fecha de envío si no se proporciona
    IF NEW.fecha_envio IS NULL THEN
        SET NEW.fecha_envio = NOW();
    END IF;
END//

-- Trigger para actualizar último acceso de usuario
DROP TRIGGER IF EXISTS `tr_actualizar_ultimo_acceso`//
CREATE TRIGGER `tr_actualizar_ultimo_acceso`
AFTER INSERT ON `auditoria_accesos`
FOR EACH ROW
BEGIN
    UPDATE `usuarios`
    SET `ultimo_acceso` = NEW.fecha_acceso
    WHERE `usuario_id` = NEW.usuario_id;
END//

-- Trigger para validar documentos digitales
DROP TRIGGER IF EXISTS `tr_validar_documento_digital`//
CREATE TRIGGER `tr_validar_documento_digital`
BEFORE INSERT ON `documentos_digitales`
FOR EACH ROW
BEGIN
    -- Validar que el tamaño del archivo no exceda el límite
    IF NEW.tamano_archivo > 10485760 THEN -- 10MB
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'El archivo no puede exceder 10MB';
    END IF;
    
    -- Establecer fecha de subida si no se proporciona
    IF NEW.fecha_subida IS NULL THEN
        SET NEW.fecha_subida = NOW();
    END IF;
END//

-- Trigger para controlar cambios en períodos vacacionales
DROP TRIGGER IF EXISTS `tr_controlar_periodos_vacacionales`//
CREATE TRIGGER `tr_controlar_periodos_vacacionales`
BEFORE UPDATE ON `periodos_vacacionales`
FOR EACH ROW
BEGIN
    -- Evitar que los días gozados excedan los días generados
    IF NEW.dias_gozados > NEW.dias_generados THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Los días gozados no pueden exceder los días generados';
    END IF;
    
    -- Los días pendientes se calculan automáticamente por la columna generada
    -- No es necesario asignar valor a dias_pendientes
    
    -- Actualizar fecha de modificación
    SET NEW.fecha_actualizacion = NOW();
END//

DELIMITER ;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

-- ========================================
-- FIN DE TRIGGERS
-- ========================================