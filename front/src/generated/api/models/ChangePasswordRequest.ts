/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Serializer for changing user password.
 */
export type ChangePasswordRequest = {
    /**
     * Contraseña actual
     */
    old_password: string;
    /**
     * Nueva contraseña
     */
    new_password: string;
    /**
     * Confirmar nueva contraseña
     */
    confirm_password: string;
};

