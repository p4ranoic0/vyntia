/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BlankEnum } from './BlankEnum';
import type { DatosFamiliaresListNivelEducativoEnum } from './DatosFamiliaresListNivelEducativoEnum';
import type { EstadoCivilEnum } from './EstadoCivilEnum';
import type { EstadoFamiliarEnum } from './EstadoFamiliarEnum';
import type { GeneroFamiliarEnum } from './GeneroFamiliarEnum';
import type { NullEnum } from './NullEnum';
import type { ParentescoEnum } from './ParentescoEnum';
import type { TipoDocumento8eeEnum } from './TipoDocumento8eeEnum';
export type DatosFamiliaresList = {
    readonly familiar_id: number;
    nombres_familiar: string;
    apellido_paterno: string;
    apellido_materno: string;
    tipo_documento?: TipoDocumento8eeEnum;
    numero_documento: string;
    fecha_nacimiento: string;
    genero_familiar: GeneroFamiliarEnum;
    parentesco: ParentescoEnum;
    es_dependiente?: boolean;
    es_beneficiario?: boolean;
    es_contacto_emergencia?: boolean;
    estado_civil?: (EstadoCivilEnum | BlankEnum | NullEnum) | null;
    nivel_educativo?: (DatosFamiliaresListNivelEducativoEnum | BlankEnum | NullEnum) | null;
    ocupacion?: string | null;
    centro_trabajo?: string | null;
    telefono_familiar?: string | null;
    correo_familiar?: string | null;
    direccion_familiar?: string | null;
    distrito_familiar?: string | null;
    provincia_familiar?: string | null;
    departamento_familiar?: string | null;
    tiene_seguro_salud?: boolean;
    tipo_seguro_salud?: string | null;
    numero_seguro?: string | null;
    centro_salud_asignado?: string | null;
    tiene_discapacidad?: boolean;
    tipo_discapacidad?: string | null;
    grado_discapacidad?: string | null;
    certificado_discapacidad?: string | null;
    fecha_inicio_dependencia?: string | null;
    fecha_fin_dependencia?: string | null;
    estado_familiar?: EstadoFamiliarEnum;
    observaciones?: string | null;
    readonly fecha_registro: string;
    readonly fecha_actualizacion: string;
    empleado: number;
};

