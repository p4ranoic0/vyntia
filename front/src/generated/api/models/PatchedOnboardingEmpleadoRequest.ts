/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoOnboardingEnum } from './EstadoOnboardingEnum';
/**
 * Serializer de lectura para el estado de onboarding.
 */
export type PatchedOnboardingEmpleadoRequest = {
    empleado?: number;
    usuario?: number;
    estado_onboarding?: EstadoOnboardingEnum;
    datos_personales_completos?: boolean;
    datos_laborales_completos?: boolean;
    dni_subido?: boolean;
    declaraciones_juradas_subidas?: boolean;
    certificados_academicos_subidos?: boolean;
    certificados_trabajo_subidos?: boolean;
    documentos_familiares_subidos?: boolean;
    validado_por?: number | null;
    fecha_validacion?: string | null;
    observaciones?: string | null;
    email_bienvenida_enviado?: boolean;
    fecha_email_bienvenida?: string | null;
};

