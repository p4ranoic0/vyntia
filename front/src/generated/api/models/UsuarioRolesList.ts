/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoAsignacionEnum } from './EstadoAsignacionEnum';
/**
 * Serializer for listing user role assignments.
 */
export type UsuarioRolesList = {
    readonly usuario_rol_id: number;
    usuario: number;
    rol: number;
    readonly fecha_asignacion: string;
    fecha_expiracion?: string | null;
    estado_asignacion?: EstadoAsignacionEnum;
    readonly usuario_nombre: string;
    readonly rol_nombre: string;
    readonly rol_descripcion: string;
    readonly es_activo: string;
};

