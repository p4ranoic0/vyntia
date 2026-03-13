/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TipoSolicitudEnum } from './TipoSolicitudEnum';
export type SolicitudVacacionesCreateRequest = {
    empleado?: number;
    periodo_vacacional?: number;
    tipo_solicitud?: TipoSolicitudEnum;
    fecha_inicio: string;
    fecha_fin: string;
    motivo_solicitud?: string;
    observaciones_empleado?: string | null;
    medio_dia?: boolean;
};

