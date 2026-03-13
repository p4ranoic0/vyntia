/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoAsignacionEnum } from './EstadoAsignacionEnum';
/**
 * Serializer for UsuarioRoles model.
 */
export type PatchedUsuarioRolesRequest = {
    usuario?: number;
    rol?: number;
    fecha_expiracion?: string | null;
    asignado_por_usuario?: number | null;
    estado_asignacion?: EstadoAsignacionEnum;
};

