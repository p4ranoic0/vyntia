/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BlankEnum } from './BlankEnum';
import type { EstadoGoceEnum } from './EstadoGoceEnum';
import type { MotivoInterrupcionEnum } from './MotivoInterrupcionEnum';
import type { NullEnum } from './NullEnum';
export type GoceVacacionesRequest = {
    empleado: number;
    solicitud_vacaciones: number;
    periodo_vacacional: number;
    fecha_inicio_real: string;
    fecha_fin_real: string;
    fecha_reincorporacion?: string | null;
    dias_gozados: string;
    estado_goce?: EstadoGoceEnum;
    fecha_interrupcion?: string | null;
    motivo_interrupcion?: (MotivoInterrupcionEnum | BlankEnum | NullEnum) | null;
    descripcion_interrupcion?: string | null;
    dias_no_gozados?: string;
    reincorporado?: boolean;
    fecha_reincorporacion_real?: string | null;
    observaciones_reincorporacion?: string | null;
    observaciones?: string | null;
    registrado_por?: number | null;
};

