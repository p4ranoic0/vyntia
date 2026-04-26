/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoCivilEnum } from './EstadoCivilEnum';
import type { EstadoEmpleadoEnum } from './EstadoEmpleadoEnum';
import type { GeneroEmpleadoCafEnum } from './GeneroEmpleadoCafEnum';
import type { TipoDocumento45aEnum } from './TipoDocumento45aEnum';
/**
 * Simplified serializer for Empleado list views.
 */
export type EmpleadoListRequest = {
    nombres_empleado: string;
    apellido_paterno: string;
    apellido_materno: string;
    numero_documento: string;
    tipo_documento?: TipoDocumento45aEnum;
    genero_empleado: GeneroEmpleadoCafEnum;
    estado_empleado?: EstadoEmpleadoEnum;
    telefono_celular: string;
    correo_personal: string;
    estado_civil: EstadoCivilEnum;
    fecha_nacimiento: string;
    direccion_domicilio: string;
    distrito_domicilio: string;
    provincia_domicilio: string;
    departamento_domicilio: string;
    ruta_fotografia?: string | null;
};

