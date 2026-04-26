/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BlankEnum } from './BlankEnum';
import type { EstadoGoceEnum } from './EstadoGoceEnum';
import type { MotivoInterrupcionEnum } from './MotivoInterrupcionEnum';
import type { NullEnum } from './NullEnum';
export type GoceVacaciones = {
    readonly goce_id: number;
    empleado: number;
    readonly empleado_nombre: string;
    solicitud_vacaciones: number;
    readonly solicitud_id: number;
    periodo_vacacional: number;
    readonly contrato_id: number;
    readonly contrato_numero: string;
    fecha_inicio_real: string;
    fecha_fin_real: string;
    fecha_reincorporacion?: string | null;
    dias_gozados: string;
    estado_goce?: EstadoGoceEnum;
    readonly estado_goce_display: string;
    fecha_interrupcion?: string | null;
    motivo_interrupcion?: (MotivoInterrupcionEnum | BlankEnum | NullEnum) | null;
    descripcion_interrupcion?: string | null;
    dias_no_gozados?: string;
    reincorporado?: boolean;
    fecha_reincorporacion_real?: string | null;
    observaciones_reincorporacion?: string | null;
    observaciones?: string | null;
    registrado_por?: number | null;
    readonly fecha_creacion: string;
    readonly fecha_actualizacion: string;
};

