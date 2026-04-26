/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoAreaEnum } from './EstadoAreaEnum';
export type PatchedAreaDetailRequest = {
    nombre_organo?: string;
    nombre_unidad_organica?: string;
    siglas_area?: string;
    descripcion_area?: string | null;
    jefe_area?: string | null;
    nivel_jerarquico?: number;
    codigo_presupuestal?: string | null;
    total_empleados?: number;
    estado_area?: EstadoAreaEnum;
    area_padre?: number | null;
};

