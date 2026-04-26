/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoModuloEnum } from './EstadoModuloEnum';
/**
 * Serializer for Modulos model.
 */
export type PatchedModulosRequest = {
    nombre_modulo?: string;
    descripcion_modulo?: string | null;
    icono_modulo?: string | null;
    ruta_modulo?: string | null;
    orden_visualizacion?: number;
    estado_modulo?: EstadoModuloEnum;
};

