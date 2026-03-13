/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoRolEnum } from './EstadoRolEnum';
/**
 * Serializer for Rol model.
 */
export type Rol = {
    readonly rol_id: number;
    nombre_rol: string;
    descripcion_rol?: string | null;
    estado_rol?: EstadoRolEnum;
    readonly es_activo: string;
    readonly total_usuarios: string;
    readonly total_permisos: string;
    readonly permisos: string;
};

