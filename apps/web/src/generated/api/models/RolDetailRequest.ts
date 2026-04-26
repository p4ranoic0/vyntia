/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoRolEnum } from './EstadoRolEnum';
export type RolDetailRequest = {
    nombre_rol: string;
    descripcion_rol?: string | null;
    nivel_jerarquico?: number;
    es_rol_sistema?: boolean;
    estado_rol?: EstadoRolEnum;
};

