/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoPeriodoEnum } from './EstadoPeriodoEnum';
export type PeriodoVacacional = {
    readonly periodo_id: number;
    empleado: number;
    readonly empleado_nombre: string;
    readonly empleado_rut: string;
    readonly area_nombre: string;
    contrato?: number | null;
    readonly contrato_id: number;
    readonly contrato_numero: string;
    readonly contrato_fecha_inicio: string;
    readonly contrato_fecha_fin: string;
    readonly contrato_estado: string;
    ano_periodo: number;
    readonly periodo_label: string;
    fecha_inicio_periodo: string;
    fecha_fin_periodo: string;
    fecha_vencimiento: string;
    dias_correspondientes: string;
    dias_adicionales?: string;
    dias_totales: string;
    dias_gozados?: string;
    dias_pendientes: string;
    dias_vencidos?: string;
    estado_periodo?: EstadoPeriodoEnum;
    configuracion: number;
    readonly configuracion_tipo: string;
    readonly porcentaje_uso: string;
    readonly esta_vencido: string;
    readonly dias_para_vencimiento: string;
    observaciones?: string | null;
    readonly fecha_creacion: string;
    readonly fecha_actualizacion: string;
};

