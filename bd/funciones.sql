-- ========================================
-- FUNCIONES AUXILIARES PARA SISTEMA DE INTRANET RRHH
-- ========================================
-- Descripción: Funciones auxiliares utilizadas por procedimientos almacenados
-- Autor: Sistema de Intranet RRHH
-- Fecha: 2024
-- ========================================

-- Función para calcular días hábiles entre dos fechas
DELIMITER //
DROP FUNCTION IF EXISTS `fn_calcular_dias_habiles`//
CREATE FUNCTION `fn_calcular_dias_habiles`(
    fecha_inicio DATE,
    fecha_fin DATE
) RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE dias_habiles INT DEFAULT 0;
    DECLARE fecha_actual DATE;
    DECLARE dia_semana INT;
    
    SET fecha_actual = fecha_inicio;
    
    WHILE fecha_actual <= fecha_fin DO
        SET dia_semana = DAYOFWEEK(fecha_actual);
        -- Lunes=2, Martes=3, Miércoles=4, Jueves=5, Viernes=6
        IF dia_semana BETWEEN 2 AND 6 THEN
            SET dias_habiles = dias_habiles + 1;
        END IF;
        SET fecha_actual = DATE_ADD(fecha_actual, INTERVAL 1 DAY);
    END WHILE;
    
    RETURN dias_habiles;
END//

-- Función para validar si una solicitud incluye viernes
DROP FUNCTION IF EXISTS `fn_incluye_viernes`//
CREATE FUNCTION `fn_incluye_viernes`(
    fecha_inicio DATE,
    fecha_fin DATE
) RETURNS BOOLEAN
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE fecha_actual DATE;
    DECLARE dia_semana INT;
    
    SET fecha_actual = fecha_inicio;
    
    WHILE fecha_actual <= fecha_fin DO
        SET dia_semana = DAYOFWEEK(fecha_actual);
        -- Viernes = 6
        IF dia_semana = 6 THEN
            RETURN TRUE;
        END IF;
        SET fecha_actual = DATE_ADD(fecha_actual, INTERVAL 1 DAY);
    END WHILE;
    
    RETURN FALSE;
END//

-- Función para calcular años de servicio de un empleado
DROP FUNCTION IF EXISTS `fn_calcular_anos_servicio`//
CREATE FUNCTION `fn_calcular_anos_servicio`(
    fecha_ingreso DATE
) RETURNS DECIMAL(4,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE anos_servicio DECIMAL(4,2);
    
    SET anos_servicio = TIMESTAMPDIFF(MONTH, fecha_ingreso, CURDATE()) / 12;
    
    RETURN anos_servicio;
END//

-- Función para generar siguiente número de documento
DROP FUNCTION IF EXISTS `fn_siguiente_numero_documento`//
CREATE FUNCTION `fn_siguiente_numero_documento`(
    tipo_documento VARCHAR(10)
) RETURNS VARCHAR(20)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE siguiente_numero INT DEFAULT 1;
    DECLARE numero_formateado VARCHAR(20);
    
    -- Obtener el último número usado para este tipo de documento
    SELECT COALESCE(MAX(CAST(SUBSTRING(numero_documento, 4) AS UNSIGNED)), 0) + 1
    INTO siguiente_numero
    FROM documentos_digitales
    WHERE tipo_documento = tipo_documento
    AND numero_documento REGEXP CONCAT('^', tipo_documento, '[0-9]+$');
    
    -- Formatear el número con ceros a la izquierda
    SET numero_formateado = CONCAT(tipo_documento, LPAD(siguiente_numero, 6, '0'));
    
    RETURN numero_formateado;
END//

DELIMITER ;

-- ========================================
-- FIN DE FUNCIONES AUXILIARES
-- ========================================