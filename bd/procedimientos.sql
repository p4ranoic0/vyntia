-- ========================================
-- SISTEMA DE INTRANET RRHH - PROCEDIMIENTOS ALMACENADOS
-- Versión: 2.0
-- Fecha: 2025
-- Descripción: Procedimientos almacenados del sistema
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
-- PROCEDIMIENTOS DEL MÓDULO DE VACACIONES
-- ========================================

-- Procedimiento para generar períodos vacacionales por año
DELIMITER //
DROP PROCEDURE IF EXISTS `sp_generar_periodos_vacacionales`//
CREATE PROCEDURE `sp_generar_periodos_vacacionales`(
    IN p_anio YEAR
)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_empleado_id INT;
    DECLARE v_fecha_ingreso DATE;
    DECLARE v_anios_servicio INT;
    DECLARE v_fecha_inicio_periodo DATE;
    DECLARE v_fecha_fin_periodo DATE;
    DECLARE v_fecha_vencimiento DATE;
    
    DECLARE cur_empleados CURSOR FOR
        SELECT e.empleado_id, dl.fecha_ingreso
        FROM empleados e
        INNER JOIN datos_laborales dl ON e.empleado_id = dl.empleado_id
        WHERE e.estado_empleado = 'activo'
        AND dl.estado_laboral = 'activo'
        AND dl.fecha_ingreso <= CONCAT(p_anio, '-12-31');
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur_empleados;
    
    read_loop: LOOP
        FETCH cur_empleados INTO v_empleado_id, v_fecha_ingreso;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- Calcular años de servicio al final del año
        SET v_anios_servicio = YEAR(CONCAT(p_anio, '-12-31')) - YEAR(v_fecha_ingreso);
        
        -- Solo generar si tiene al menos 1 año de servicio
        IF v_anios_servicio >= 1 THEN
            -- Calcular fechas del período
            SET v_fecha_inicio_periodo = DATE_ADD(v_fecha_ingreso, INTERVAL v_anios_servicio YEAR);
            SET v_fecha_fin_periodo = DATE_ADD(v_fecha_inicio_periodo, INTERVAL 1 YEAR);
            SET v_fecha_vencimiento = DATE_ADD(v_fecha_fin_periodo, INTERVAL 1 YEAR);
            
            -- Insertar período si no existe
            INSERT IGNORE INTO periodos_vacacionales (
                empleado_id,
                anio_periodo,
                fecha_inicio_periodo,
                fecha_fin_periodo,
                dias_generados,
                fecha_vencimiento
            ) VALUES (
                v_empleado_id,
                p_anio,
                v_fecha_inicio_periodo,
                v_fecha_fin_periodo,
                30,
                v_fecha_vencimiento
            );
        END IF;
    END LOOP;
    
    CLOSE cur_empleados;
END//

-- Procedimiento para validar solicitud de vacaciones
DROP PROCEDURE IF EXISTS `sp_validar_solicitud_vacaciones`//
CREATE PROCEDURE `sp_validar_solicitud_vacaciones`(
    IN p_empleado_id INT,
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE,
    IN p_dias_solicitados INT,
    OUT p_es_valida BOOLEAN,
    OUT p_mensaje_error VARCHAR(500),
    OUT p_periodo_id INT,
    OUT p_incluye_fines_semana BOOLEAN
)
sp_validar_solicitud_vacaciones: BEGIN
    DECLARE v_dias_disponibles INT DEFAULT 0;
    DECLARE v_dias_habiles INT;
    DECLARE v_diferencia_dias INT;
    
    SET p_es_valida = FALSE;
    SET p_mensaje_error = '';
    SET p_periodo_id = NULL;
    SET p_incluye_fines_semana = FALSE;
    
    -- Validar que las fechas sean coherentes
    IF p_fecha_inicio > p_fecha_fin THEN
        SET p_mensaje_error = 'La fecha de inicio no puede ser mayor a la fecha de fin';
        LEAVE sp_validar_solicitud_vacaciones;
    END IF;
    
    -- Calcular días entre fechas
    SET v_diferencia_dias = DATEDIFF(p_fecha_fin, p_fecha_inicio) + 1;
    
    -- Validar fraccionamiento máximo de 7 días
    IF v_diferencia_dias > 7 AND v_diferencia_dias < 30 THEN
        SET p_mensaje_error = 'Las vacaciones fraccionadas no pueden exceder 7 días';
        LEAVE sp_validar_solicitud_vacaciones;
    END IF;
    
    -- Calcular días hábiles
    SET v_dias_habiles = fn_calcular_dias_habiles(p_fecha_inicio, p_fecha_fin);
    
    -- Verificar si incluye viernes (y por tanto fines de semana)
    SET p_incluye_fines_semana = fn_incluye_viernes(p_fecha_inicio, p_fecha_fin);
    
    -- Buscar período con días disponibles
    SELECT pv.periodo_id, pv.dias_pendientes
    INTO p_periodo_id, v_dias_disponibles
    FROM periodos_vacacionales pv
    WHERE pv.empleado_id = p_empleado_id
    AND pv.estado_periodo = 'vigente'
    AND pv.dias_pendientes >= p_dias_solicitados
    ORDER BY pv.anio_periodo ASC
    LIMIT 1;
    
    -- Validar que hay días disponibles
    IF p_periodo_id IS NULL THEN
        SET p_mensaje_error = 'No tiene días de vacaciones disponibles suficientes';
        LEAVE sp_validar_solicitud_vacaciones;
    END IF;
    
    -- Validar que no hay solapamiento con otras solicitudes aprobadas
    IF EXISTS (
        SELECT 1 FROM solicitudes_vacaciones sv
        WHERE sv.empleado_id = p_empleado_id
        AND sv.estado_solicitud IN ('aprobada', 'en_revision')
        AND (
            (p_fecha_inicio BETWEEN sv.fecha_inicio_solicitud AND sv.fecha_fin_solicitud)
            OR (p_fecha_fin BETWEEN sv.fecha_inicio_solicitud AND sv.fecha_fin_solicitud)
            OR (sv.fecha_inicio_solicitud BETWEEN p_fecha_inicio AND p_fecha_fin)
        )
    ) THEN
        SET p_mensaje_error = 'Ya tiene una solicitud aprobada o en revisión para esas fechas';
        LEAVE sp_validar_solicitud_vacaciones;
    END IF;
    
    -- Si llegamos aquí, la solicitud es válida
    SET p_es_valida = TRUE;
END//

-- Procedimiento para aprobar solicitud de vacaciones
DROP PROCEDURE IF EXISTS `sp_aprobar_solicitud_vacaciones`//
CREATE PROCEDURE `sp_aprobar_solicitud_vacaciones`(
    IN p_solicitud_id INT,
    IN p_usuario_aprobador_id INT,
    IN p_observaciones TEXT
)
BEGIN
    DECLARE v_empleado_id INT;
    DECLARE v_periodo_id INT;
    DECLARE v_dias_solicitados INT;
    DECLARE v_estado_actual VARCHAR(50);
    
    -- Obtener datos de la solicitud
    SELECT empleado_id, periodo_id, dias_solicitados, estado_solicitud
    INTO v_empleado_id, v_periodo_id, v_dias_solicitados, v_estado_actual
    FROM solicitudes_vacaciones
    WHERE solicitud_id = p_solicitud_id;
    
    -- Validar que la solicitud existe y está en estado válido para aprobar
    IF v_estado_actual NOT IN ('enviada', 'en_revision') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La solicitud no está en estado válido para aprobar';
    END IF;
    
    -- Actualizar la solicitud
    UPDATE solicitudes_vacaciones
    SET estado_solicitud = 'aprobada',
        fecha_respuesta = NOW(),
        observaciones_jefe = p_observaciones,
        revisado_por_usuario_id = p_usuario_aprobador_id
    WHERE solicitud_id = p_solicitud_id;
    
    -- Registrar en el historial
    INSERT INTO historial_solicitudes_vacaciones (
        solicitud_id, estado_anterior, estado_nuevo, 
        motivo_cambio, usuario_cambio_id
    ) VALUES (
        p_solicitud_id, v_estado_actual, 'aprobada',
        CONCAT('Solicitud aprobada: ', IFNULL(p_observaciones, 'Sin observaciones')),
        p_usuario_aprobador_id
    );
END//

-- Procedimiento para rechazar solicitud de vacaciones
DROP PROCEDURE IF EXISTS `sp_rechazar_solicitud_vacaciones`//
CREATE PROCEDURE `sp_rechazar_solicitud_vacaciones`(
    IN p_solicitud_id INT,
    IN p_usuario_revisor_id INT,
    IN p_motivo_rechazo TEXT
)
BEGIN
    DECLARE v_estado_actual VARCHAR(50);
    
    -- Obtener estado actual
    SELECT estado_solicitud
    INTO v_estado_actual
    FROM solicitudes_vacaciones
    WHERE solicitud_id = p_solicitud_id;
    
    -- Validar que la solicitud existe y está en estado válido para rechazar
    IF v_estado_actual NOT IN ('enviada', 'en_revision') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La solicitud no está en estado válido para rechazar';
    END IF;
    
    -- Actualizar la solicitud
    UPDATE solicitudes_vacaciones
    SET estado_solicitud = 'rechazada',
        fecha_respuesta = NOW(),
        observaciones_jefe = p_motivo_rechazo,
        revisado_por_usuario_id = p_usuario_revisor_id
    WHERE solicitud_id = p_solicitud_id;
    
    -- Registrar en el historial
    INSERT INTO historial_solicitudes_vacaciones (
        solicitud_id, estado_anterior, estado_nuevo, 
        motivo_cambio, usuario_cambio_id
    ) VALUES (
        p_solicitud_id, v_estado_actual, 'rechazada',
        CONCAT('Solicitud rechazada: ', p_motivo_rechazo),
        p_usuario_revisor_id
    );
END//

-- Procedimiento para registrar goce de vacaciones
DROP PROCEDURE IF EXISTS `sp_registrar_goce_vacaciones`//
CREATE PROCEDURE `sp_registrar_goce_vacaciones`(
    IN p_solicitud_id INT,
    IN p_fecha_inicio_goce DATE,
    IN p_fecha_fin_goce DATE,
    IN p_dias_gozados INT,
    IN p_documento_autorizacion VARCHAR(100),
    IN p_numero_documento VARCHAR(50),
    IN p_observaciones TEXT,
    IN p_usuario_registro_id INT
)
BEGIN
    DECLARE v_empleado_id INT;
    DECLARE v_periodo_id INT;
    DECLARE v_estado_solicitud VARCHAR(50);
    DECLARE v_incluye_fines_semana BOOLEAN;
    DECLARE v_tipo_goce VARCHAR(50);
    
    -- Obtener datos de la solicitud
    SELECT empleado_id, periodo_id, estado_solicitud, incluye_fines_semana
    INTO v_empleado_id, v_periodo_id, v_estado_solicitud, v_incluye_fines_semana
    FROM solicitudes_vacaciones
    WHERE solicitud_id = p_solicitud_id;
    
    -- Validar que la solicitud está aprobada
    IF v_estado_solicitud != 'aprobada' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Solo se pueden registrar goces de solicitudes aprobadas';
    END IF;
    
    -- Determinar tipo de goce
    IF p_dias_gozados >= 30 THEN
        SET v_tipo_goce = 'completo';
    ELSE
        SET v_tipo_goce = 'fraccionado';
    END IF;
    
    -- Insertar el goce
    INSERT INTO goces_vacaciones (
        solicitud_id, empleado_id, periodo_id,
        fecha_inicio_goce, fecha_fin_goce, dias_gozados,
        tipo_goce, incluyo_fines_semana,
        documento_autorizacion, numero_documento_autorizacion,
        observaciones_goce, registrado_por_usuario_id
    ) VALUES (
        p_solicitud_id, v_empleado_id, v_periodo_id,
        p_fecha_inicio_goce, p_fecha_fin_goce, p_dias_gozados,
        v_tipo_goce, v_incluye_fines_semana,
        p_documento_autorizacion, p_numero_documento,
        p_observaciones, p_usuario_registro_id
    );
END//

-- Procedimiento para actualizar saldos vacacionales
DROP PROCEDURE IF EXISTS `sp_actualizar_saldos_vacacionales`//
CREATE PROCEDURE `sp_actualizar_saldos_vacacionales`()
BEGIN
    -- Actualizar días gozados en períodos basado en goces registrados
    UPDATE periodos_vacacionales pv
    SET dias_gozados = (
        SELECT IFNULL(SUM(gv.dias_gozados), 0)
        FROM goces_vacaciones gv
        WHERE gv.periodo_id = pv.periodo_id
    );
    
    -- Marcar como vencidos los períodos que han superado su fecha de vencimiento
    UPDATE periodos_vacacionales
    SET estado_periodo = 'vencido'
    WHERE fecha_vencimiento < CURDATE()
    AND estado_periodo = 'vigente';
END//

-- Procedimiento para generar número de solicitud
DROP PROCEDURE IF EXISTS `sp_generar_numero_solicitud`//
CREATE PROCEDURE `sp_generar_numero_solicitud`(
    OUT p_numero_solicitud VARCHAR(20)
)
BEGIN
    DECLARE v_contador INT;
    DECLARE v_anio YEAR;
    
    SET v_anio = YEAR(CURDATE());
    
    -- Obtener el siguiente número correlativo del año
    SELECT IFNULL(MAX(CAST(SUBSTRING(numero_solicitud, -4) AS UNSIGNED)), 0) + 1
    INTO v_contador
    FROM solicitudes_vacaciones
    WHERE numero_solicitud LIKE CONCAT('SOL-VAC-', v_anio, '-%');
    
    -- Generar el número de solicitud
    SET p_numero_solicitud = CONCAT('SOL-VAC-', v_anio, '-', LPAD(v_contador, 4, '0'));
END//

DELIMITER ;

-- ========================================
-- PROCEDIMIENTOS DE ADMINISTRACIÓN GENERAL
-- ========================================

DELIMITER //

-- Procedimiento para crear usuario del sistema
DROP PROCEDURE IF EXISTS `sp_crear_usuario_sistema`//
CREATE PROCEDURE `sp_crear_usuario_sistema`(
    IN p_empleado_id INT,
    IN p_nombre_usuario VARCHAR(100),
    IN p_contrasena VARCHAR(255),
    IN p_correo_institucional VARCHAR(150),
    IN p_rol_id INT
)
BEGIN
    DECLARE v_usuario_id INT;
    
    -- Insertar usuario
    INSERT INTO usuarios (
        nombre_usuario, hash_contrasena, empleado_id, 
        correo_institucional, estado_usuario
    ) VALUES (
        p_nombre_usuario, p_contrasena, p_empleado_id,
        p_correo_institucional, 'activo'
    );
    
    SET v_usuario_id = LAST_INSERT_ID();
    
    -- Asignar rol
    INSERT INTO usuario_roles (usuario_id, rol_id)
    VALUES (v_usuario_id, p_rol_id);
END//

-- Procedimiento para auditar cambios
DROP PROCEDURE IF EXISTS `sp_registrar_auditoria_cambio`//
CREATE PROCEDURE `sp_registrar_auditoria_cambio`(
    IN p_tabla_afectada VARCHAR(100),
    IN p_registro_id INT,
    IN p_tipo_operacion ENUM('INSERT','UPDATE','DELETE'),
    IN p_usuario_id INT,
    IN p_valores_anteriores JSON,
    IN p_valores_nuevos JSON,
    IN p_direccion_ip VARCHAR(45),
    IN p_observaciones TEXT
)
BEGIN
    INSERT INTO auditoria_cambios (
        tabla_afectada, registro_id, tipo_operacion,
        usuario_id, valores_anteriores, valores_nuevos,
        direccion_ip, observaciones
    ) VALUES (
        p_tabla_afectada, p_registro_id, p_tipo_operacion,
        p_usuario_id, p_valores_anteriores, p_valores_nuevos,
        p_direccion_ip, p_observaciones
    );
END//

DELIMITER ;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;



-- ========================================
-- FIN DE PROCEDIMIENTOS ALMACENADOS
-- ========================================