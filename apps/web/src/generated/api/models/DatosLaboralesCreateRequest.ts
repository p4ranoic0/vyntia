/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Categoria3d1Enum } from './Categoria3d1Enum';
import type { EstadoDatosEnum } from './EstadoDatosEnum';
import type { JornadaLaboral6a2Enum } from './JornadaLaboral6a2Enum';
import type { ModalidadTrabajoEnum } from './ModalidadTrabajoEnum';
import type { RegimenLaboralEnum } from './RegimenLaboralEnum';
import type { TipoContratoEnum } from './TipoContratoEnum';
/**
 * Serializer for creating DatosLaborales without empleado and area fields.
 */
export type DatosLaboralesCreateRequest = {
    cargo_empleado: string;
    codigo_puesto?: string | null;
    nivel_puesto?: string | null;
    categoria: Categoria3d1Enum;
    tipo_contrato: TipoContratoEnum;
    regimen_laboral: RegimenLaboralEnum;
    modalidad_trabajo?: ModalidadTrabajoEnum;
    jornada_laboral?: JornadaLaboral6a2Enum;
    fecha_ingreso: string;
    fecha_inicio_contrato: string;
    fecha_fin_contrato?: string | null;
    fecha_cese?: string | null;
    sueldo_basico: string;
    asignacion_familiar?: string;
    bonificacion_especial?: string;
    otras_bonificaciones?: string;
    horario_entrada?: string | null;
    horario_salida?: string | null;
    horas_semanales?: string;
    estado_datos?: EstadoDatosEnum;
    observaciones?: string | null;
    jefe_directo?: number | null;
};

