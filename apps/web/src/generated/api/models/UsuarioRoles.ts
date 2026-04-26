/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoAsignacionEnum } from './EstadoAsignacionEnum';
/**
 * Serializer for UsuarioRoles model.
 */
export type UsuarioRoles = {
    readonly usuario_rol_id: number;
    usuario: number;
    rol: number;
    readonly fecha_asignacion: string;
    fecha_expiracion?: string | null;
    asignado_por_usuario?: number | null;
    estado_asignacion?: EstadoAsignacionEnum;
    readonly usuario_nombre: string;
    readonly rol_nombre: string;
    readonly asignado_por_nombre: string;
    readonly es_activo: string;
    readonly dias_hasta_expiracion: string;
};

