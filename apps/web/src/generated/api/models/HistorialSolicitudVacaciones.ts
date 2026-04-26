/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TipoAccionEnum } from './TipoAccionEnum';
export type HistorialSolicitudVacaciones = {
    readonly historial_id: number;
    solicitud_vacaciones: number;
    tipo_accion: TipoAccionEnum;
    readonly tipo_accion_display: string;
    descripcion_accion: string;
    estado_anterior?: string | null;
    estado_nuevo?: string | null;
    usuario_accion?: number | null;
    readonly usuario_nombre: string;
    observaciones?: string | null;
    datos_adicionales?: any;
    readonly fecha_accion: string;
    ip_usuario?: string | null;
};

