/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Serializer para restablecer contraseña con token.
 */
export type ResetPasswordRequest = {
    /**
     * Token de recuperación de contraseña
     */
    token: string;
    /**
     * Nueva contraseña
     */
    new_password: string;
};

