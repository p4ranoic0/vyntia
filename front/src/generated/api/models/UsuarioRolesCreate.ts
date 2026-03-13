/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoAsignacionEnum } from './EstadoAsignacionEnum';
/**
 * Serializer for creating user role assignments.
 */
export type UsuarioRolesCreate = {
    usuario: number;
    rol: number;
    fecha_expiracion?: string | null;
    estado_asignacion?: EstadoAsignacionEnum;
};

