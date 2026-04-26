/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoUsuarioEnum } from './EstadoUsuarioEnum';
export type UsuarioDetail = {
    readonly usuario_id: number;
    nombres_usuario: string;
    date_joined?: string;
    last_login?: string | null;
    estado_usuario?: EstadoUsuarioEnum;
};

