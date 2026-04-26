/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoCivilEnum } from './EstadoCivilEnum';
import type { EstadoEmpleadoEnum } from './EstadoEmpleadoEnum';
import type { GeneroEmpleadoCafEnum } from './GeneroEmpleadoCafEnum';
/**
 * Serializer for Empleado model.
 */
export type EmpleadoRequest = {
    nombres_empleado: string;
    apellido_paterno: string;
    apellido_materno: string;
    numero_documento: string;
    fecha_nacimiento: string;
    genero_empleado: GeneroEmpleadoCafEnum;
    estado_civil: EstadoCivilEnum;
    direccion_domicilio: string;
    distrito_domicilio: string;
    telefono_celular: string;
    correo_personal: string;
    es_padre_familia?: boolean;
    entidad_bancaria: string;
    numero_cuenta_bancaria: string;
    estado_empleado?: EstadoEmpleadoEnum;
};

