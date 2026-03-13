/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Categoria7eaEnum } from './Categoria7eaEnum';
import type { EmpleadoList } from './EmpleadoList';
import type { EstadoDocumentoEnum } from './EstadoDocumentoEnum';
import type { FormatoArchivoEnum } from './FormatoArchivoEnum';
import type { NivelAccesoEnum } from './NivelAccesoEnum';
import type { TipoDocumento922Enum } from './TipoDocumento922Enum';
/**
 * Serializer for DocumentosDigitales model.
 */
export type DocumentosDigitales = {
    readonly documento_id: number;
    empleado: number;
    readonly empleado_detalle: EmpleadoList;
    tipo_documento: TipoDocumento922Enum;
    readonly tipo_documento_texto: string;
    categoria: Categoria7eaEnum;
    readonly categoria_texto: string;
    nombre_documento: string;
    descripcion?: string | null;
    archivo: string;
    readonly nombre_archivo_original: string;
    readonly formato_archivo: FormatoArchivoEnum;
    /**
     * Tamaño en bytes
     */
    tamano_archivo: number;
    readonly tamano_mb: string;
    fecha_emision?: string | null;
    fecha_vencimiento?: string | null;
    readonly fecha_subida: string;
    subido_por?: number | null;
    estado_documento?: EstadoDocumentoEnum;
    readonly estado_texto: string;
    nivel_acceso?: NivelAccesoEnum;
    readonly dias_para_vencimiento: string;
    validado_por?: number | null;
    fecha_validacion?: string | null;
    observaciones_validacion?: string | null;
};

