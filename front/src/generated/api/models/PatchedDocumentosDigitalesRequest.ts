/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Categoria7eaEnum } from './Categoria7eaEnum';
import type { EstadoDocumentoEnum } from './EstadoDocumentoEnum';
import type { NivelAccesoEnum } from './NivelAccesoEnum';
import type { TipoDocumento922Enum } from './TipoDocumento922Enum';
/**
 * Serializer for DocumentosDigitales model.
 */
export type PatchedDocumentosDigitalesRequest = {
    empleado?: number;
    tipo_documento?: TipoDocumento922Enum;
    categoria?: Categoria7eaEnum;
    nombre_documento?: string;
    descripcion?: string | null;
    archivo?: Blob;
    /**
     * Tamaño en bytes
     */
    tamano_archivo?: number;
    fecha_emision?: string | null;
    fecha_vencimiento?: string | null;
    subido_por?: number | null;
    estado_documento?: EstadoDocumentoEnum;
    nivel_acceso?: NivelAccesoEnum;
    validado_por?: number | null;
    fecha_validacion?: string | null;
    observaciones_validacion?: string | null;
};

