/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoRolEnum } from './EstadoRolEnum';
import type { TipoPermisoEnum } from './TipoPermisoEnum';
/**
 * Serializer for Permiso model.
 */
export type Permiso = {
    readonly permiso_id: number;
    nombre_permiso: string;
    descripcion_permiso?: string | null;
    /**
     * ID del módulo según MODULES_CONFIG (ej: empleados, vacaciones, etc)
     */
    modulo: string;
    tipo_permiso: TipoPermisoEnum;
    estado_permiso?: EstadoRolEnum;
    readonly es_activo: string;
};

