/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoUbicacionEnum } from './EstadoUbicacionEnum';
import type { TipoMovimientoEnum } from './TipoMovimientoEnum';
export type HistorialUbicacionesRequest = {
    /**
     * Tipo de movimiento
     *
     * * `ingreso` - Ingreso
     * * `traslado` - Traslado
     * * `rotacion` - Rotación
     * * `comision` - Comisión
     * * `destacamento` - Destacamento
     * * `retorno` - Retorno
     */
    tipo_movimiento: TipoMovimientoEnum;
    /**
     * Fecha de inicio del movimiento
     */
    fecha_inicio: string;
    /**
     * Fecha de término del movimiento
     */
    fecha_termino?: string | null;
    /**
     * Motivo del movimiento
     */
    motivo_movimiento?: string | null;
    /**
     * Documento que sustenta el movimiento
     */
    documento_sustento?: string | null;
    /**
     * Número del documento de sustento
     */
    numero_documento_sustento?: string | null;
    /**
     * Observaciones adicionales
     */
    observaciones?: string | null;
    /**
     * Estado de la ubicación
     *
     * * `activo` - Activo
     * * `inactivo` - Inactivo
     * * `temporal` - Temporal
     */
    estado_ubicacion?: EstadoUbicacionEnum;
    /**
     * ID del empleado
     */
    empleado: number;
    /**
     * ID del área de origen
     */
    area_origen?: number | null;
    /**
     * ID del área de destino
     */
    area_destino: number;
    /**
     * ID del documento adjunto
     */
    documento?: number | null;
    /**
     * Usuario que registró el movimiento
     */
    registrado_por_usuario?: number | null;
};

