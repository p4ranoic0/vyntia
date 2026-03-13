/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TipoSolicitudEnum } from './TipoSolicitudEnum';
export type SolicitudVacacionesRequest = {
    empleado: number;
    periodo_vacacional: number;
    tipo_solicitud?: TipoSolicitudEnum;
    fecha_inicio: string;
    fecha_fin: string;
    dias_solicitados: string;
    medio_dia?: boolean;
    motivo_solicitud: string;
    observaciones_empleado?: string | null;
    observaciones_jefe?: string | null;
    observaciones_rrhh?: string | null;
    motivo_rechazo?: string | null;
    motivo_cancelacion?: string | null;
};

