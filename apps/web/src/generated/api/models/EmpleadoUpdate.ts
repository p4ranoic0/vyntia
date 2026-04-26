/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoCivilEnum } from './EstadoCivilEnum';
import type { EstadoEmpleadoEnum } from './EstadoEmpleadoEnum';
/**
 * Specialized serializer for updating employees.
 */
export type EmpleadoUpdate = {
    nombres_empleado: string;
    apellido_paterno: string;
    apellido_materno: string;
    correo_personal: string;
    telefono_celular: string;
    direccion_domicilio: string;
    distrito_domicilio: string;
    estado_civil: EstadoCivilEnum;
    entidad_bancaria: string;
    numero_cuenta_bancaria: string;
    estado_empleado?: EstadoEmpleadoEnum;
};

