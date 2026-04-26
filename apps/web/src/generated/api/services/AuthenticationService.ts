/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChangePasswordRequest } from '../models/ChangePasswordRequest';
import type { ForgotPasswordRequest } from '../models/ForgotPasswordRequest';
import type { LoginRequest } from '../models/LoginRequest';
import type { ResetPasswordRequest } from '../models/ResetPasswordRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthenticationService {
    /**
     * Iniciar sesión
     * Autentica un usuario y devuelve tokens JWT de acceso y actualización.
     * @param requestBody
     * @returns any Autenticación exitosa
     * @throws ApiError
     */
    public static authLoginCreate(
        requestBody: LoginRequest,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/login/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Payload inválido o credenciales incompletas`,
                401: `Credenciales inválidas o usuario no autorizado`,
                429: `Demasiados intentos de autenticación (rate limit)`,
            },
        });
    }
    /**
     * Cambiar contraseña
     * Permite al usuario autenticado cambiar su contraseña.
     * @param requestBody
     * @returns any
     * @throws ApiError
     */
    public static authUserProfileChangePasswordCreate(
        requestBody: ChangePasswordRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/user-profile/change-password/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Solicitar recuperación de contraseña
     * Envía un email con un enlace para recuperar la contraseña.
     * @param requestBody
     * @returns any
     * @throws ApiError
     */
    public static authForgotPasswordCreate(
        requestBody: ForgotPasswordRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/forgot-password/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Restablecer contraseña
     * Restablece la contraseña del usuario usando un token de recuperación.
     * @param requestBody
     * @returns any
     * @throws ApiError
     */
    public static authResetPasswordCreate(
        requestBody: ResetPasswordRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/reset-password/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
