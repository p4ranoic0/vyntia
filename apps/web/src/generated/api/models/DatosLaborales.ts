/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Categoria3d1Enum } from './Categoria3d1Enum';
import type { JornadaLaboral6a2Enum } from './JornadaLaboral6a2Enum';
import type { ModalidadTrabajoEnum } from './ModalidadTrabajoEnum';
import type { RegimenLaboralEnum } from './RegimenLaboralEnum';
import type { TipoContratoEnum } from './TipoContratoEnum';
/**
 * Serializer for DatosLaborales model.
 */
export type DatosLaborales = {
    readonly dato_laboral_id: number;
    empleado: number;
    area: number;
    fecha_ingreso: string;
    cargo_empleado: string;
    tipo_contrato: TipoContratoEnum;
    regimen_laboral: RegimenLaboralEnum;
    modalidad_trabajo?: ModalidadTrabajoEnum;
    jornada_laboral?: JornadaLaboral6a2Enum;
    fecha_cese?: string | null;
    categoria: Categoria3d1Enum;
    sueldo_basico: string;
    readonly es_activo: string;
    readonly 'antiguedad_años': string;
    readonly antiguedad_meses: string;
    readonly tiempo_servicio: string;
    readonly empleado_nombre: string;
    readonly area_nombre: string;
    readonly ultimo_login_texto: string;
    readonly dias_sin_login: string;
};

