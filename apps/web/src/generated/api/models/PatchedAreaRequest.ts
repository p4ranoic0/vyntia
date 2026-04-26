/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoAreaEnum } from './EstadoAreaEnum';
/**
 * Serializer for Area model.
 */
export type PatchedAreaRequest = {
    nombre_organo?: string;
    nombre_unidad_organica?: string;
    siglas_area?: string;
    descripcion_area?: string | null;
    estado_area?: EstadoAreaEnum;
};

