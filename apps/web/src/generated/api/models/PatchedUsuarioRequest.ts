/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoUsuarioEnum } from './EstadoUsuarioEnum';
import type { TipoUsuarioEnum } from './TipoUsuarioEnum';
/**
 * Serializer for Usuario model.
 */
export type PatchedUsuarioRequest = {
    username?: string;
    nombres_usuario?: string;
    apellidos_usuario?: string;
    email?: string;
    tipo_usuario?: TipoUsuarioEnum;
    empleado?: number | null;
    last_login?: string | null;
    estado_usuario?: EstadoUsuarioEnum;
};

