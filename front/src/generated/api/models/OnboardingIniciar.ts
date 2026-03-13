/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OnboardingIniciarGeneroEmpleadoEnum } from './OnboardingIniciarGeneroEmpleadoEnum';
/**
 * Serializer para que RRHH inicie un onboarding.
 */
export type OnboardingIniciar = {
    nombres_empleado: string;
    apellido_paterno: string;
    apellido_materno?: string;
    numero_documento: string;
    correo_personal: string;
    genero_empleado?: OnboardingIniciarGeneroEmpleadoEnum;
    fecha_nacimiento?: string | null;
};

