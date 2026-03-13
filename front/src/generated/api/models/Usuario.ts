/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Empleado } from './Empleado';
import type { EstadoUsuarioEnum } from './EstadoUsuarioEnum';
import type { TipoUsuarioEnum } from './TipoUsuarioEnum';
/**
 * Serializer for Usuario model.
 */
export type Usuario = {
    readonly usuario_id: number;
    username: string;
    nombres_usuario: string;
    apellidos_usuario: string;
    email: string;
    tipo_usuario: TipoUsuarioEnum;
    empleado?: number | null;
    readonly empleado_detalle: Empleado;
    last_login?: string | null;
    estado_usuario?: EstadoUsuarioEnum;
    readonly date_joined: string;
    readonly es_activo: string;
    readonly nombre_completo: string;
    readonly roles_activos: string;
    readonly ultimo_login_texto: string;
    readonly dias_sin_login: string;
};

