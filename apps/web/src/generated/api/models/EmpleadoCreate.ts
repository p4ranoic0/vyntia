/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoCivilEnum } from './EstadoCivilEnum';
import type { EstadoEmpleadoEnum } from './EstadoEmpleadoEnum';
import type { GeneroEmpleadoCafEnum } from './GeneroEmpleadoCafEnum';
import type { SistemaPensionesEnum } from './SistemaPensionesEnum';
import type { TipoSeguroSaludEnum } from './TipoSeguroSaludEnum';
/**
 * Serializer for creating employees with related data.
 */
export type EmpleadoCreate = {
    readonly empleado_id: number;
    nombres_empleado: string;
    apellido_paterno: string;
    apellido_materno: string;
    numero_documento: string;
    fecha_nacimiento: string;
    genero_empleado: GeneroEmpleadoCafEnum;
    estado_civil: EstadoCivilEnum;
    direccion_domicilio: string;
    distrito_domicilio: string;
    provincia_domicilio: string;
    departamento_domicilio: string;
    telefono_celular: string;
    correo_personal: string;
    es_padre_familia?: boolean;
    sistema_pensiones?: SistemaPensionesEnum;
    tipo_seguro_salud?: TipoSeguroSaludEnum;
    entidad_bancaria: string;
    numero_cuenta_bancaria: string;
    numero_cci: string;
    estado_empleado?: EstadoEmpleadoEnum;
};

