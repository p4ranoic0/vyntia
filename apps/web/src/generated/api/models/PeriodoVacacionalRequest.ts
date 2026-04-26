/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoPeriodoEnum } from './EstadoPeriodoEnum';
export type PeriodoVacacionalRequest = {
    empleado: number;
    contrato?: number | null;
    ano_periodo: number;
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
    observaciones?: string | null;
};

