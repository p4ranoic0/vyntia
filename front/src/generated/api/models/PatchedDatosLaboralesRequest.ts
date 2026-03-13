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
export type PatchedDatosLaboralesRequest = {
    empleado?: number;
    area?: number;
    fecha_ingreso?: string;
    cargo_empleado?: string;
    tipo_contrato?: TipoContratoEnum;
    regimen_laboral?: RegimenLaboralEnum;
    modalidad_trabajo?: ModalidadTrabajoEnum;
    jornada_laboral?: JornadaLaboral6a2Enum;
    fecha_cese?: string | null;
    categoria?: Categoria3d1Enum;
    sueldo_basico?: string;
};

