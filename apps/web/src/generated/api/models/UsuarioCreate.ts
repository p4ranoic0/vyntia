/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoUsuarioEnum } from './EstadoUsuarioEnum';
import type { TipoUsuarioEnum } from './TipoUsuarioEnum';
/**
 * Serializer for creating users.
 */
export type UsuarioCreate = {
    username: string;
    nombres_usuario: string;
    apellidos_usuario: string;
    email: string;
    tipo_usuario: TipoUsuarioEnum;
    empleado?: number | null;
    estado_usuario?: EstadoUsuarioEnum;
};

