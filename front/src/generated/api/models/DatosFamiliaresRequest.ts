/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoFamiliarEnum } from './EstadoFamiliarEnum';
import type { GeneroFamiliarEnum } from './GeneroFamiliarEnum';
import type { ParentescoEnum } from './ParentescoEnum';
import type { TipoDocumento8eeEnum } from './TipoDocumento8eeEnum';
/**
 * Serializer for DatosFamiliares model.
 */
export type DatosFamiliaresRequest = {
    empleado: number;
    parentesco: ParentescoEnum;
    nombres_familiar: string;
    apellido_paterno: string;
    apellido_materno: string;
    fecha_nacimiento: string;
    genero_familiar: GeneroFamiliarEnum;
    numero_documento: string;
    tipo_documento?: TipoDocumento8eeEnum;
    es_beneficiario?: boolean;
    es_dependiente?: boolean;
    estado_familiar?: EstadoFamiliarEnum;
};

