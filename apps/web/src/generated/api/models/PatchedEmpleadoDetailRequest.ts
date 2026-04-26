/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BlankEnum } from './BlankEnum';
import type { EstadoCivilEnum } from './EstadoCivilEnum';
import type { EstadoEmpleadoEnum } from './EstadoEmpleadoEnum';
import type { EstadoRolEnum } from './EstadoRolEnum';
import type { GeneroEmpleadoCafEnum } from './GeneroEmpleadoCafEnum';
import type { NullEnum } from './NullEnum';
import type { SistemaPensionesEnum } from './SistemaPensionesEnum';
import type { TipoComisionEnum } from './TipoComisionEnum';
import type { TipoDocumento45aEnum } from './TipoDocumento45aEnum';
import type { TipoSangreEnum } from './TipoSangreEnum';
import type { TipoSeguroSaludEnum } from './TipoSeguroSaludEnum';
export type PatchedEmpleadoDetailRequest = {
    numero_documento?: string;
    tipo_documento?: TipoDocumento45aEnum;
    nombres_empleado?: string;
    apellido_paterno?: string;
    apellido_materno?: string;
    numero_ruc?: string | null;
    genero_empleado?: GeneroEmpleadoCafEnum;
    fecha_nacimiento?: string;
    es_padre_familia?: boolean;
    es_militar?: boolean;
    sistema_pensiones?: SistemaPensionesEnum;
    tipo_comision?: TipoComisionEnum;
    codigo_cuspp?: string | null;
    tipo_seguro_salud?: TipoSeguroSaludEnum;
    centro_salud?: string | null;
    direccion_centro_salud?: string | null;
    departamento_centro_salud?: string | null;
    vigencia_estado_seguro?: EstadoRolEnum;
    telefono_fijo?: string | null;
    telefono_celular?: string;
    correo_personal?: string;
    estado_civil?: EstadoCivilEnum;
    direccion_domicilio?: string;
    distrito_domicilio?: string;
    provincia_domicilio?: string;
    departamento_domicilio?: string;
    entidad_bancaria?: string;
    numero_cuenta_bancaria?: string;
    numero_cci?: string;
    tipo_sangre?: (TipoSangreEnum | BlankEnum | NullEnum) | null;
    talla_empleado?: string | null;
    peso_empleado?: string | null;
    ruta_fotografia?: string | null;
    estado_empleado?: EstadoEmpleadoEnum;
};

