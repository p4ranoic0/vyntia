/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoEstudiosEnum } from './EstadoEstudiosEnum';
import type { ModalidadEstudioEnum } from './ModalidadEstudioEnum';
import type { NivelEducativoA5dEnum } from './NivelEducativoA5dEnum';
import type { TipoInstitucionEnum } from './TipoInstitucionEnum';
/**
 * Serializer for DatosAcademicos model.
 */
export type DatosAcademicos = {
    readonly academico_id: number;
    empleado: number;
    nivel_educativo: NivelEducativoA5dEnum;
    nombre_institucion: string;
    tipo_institucion: TipoInstitucionEnum;
    modalidad_estudio?: ModalidadEstudioEnum;
    nombre_carrera: string;
    codigo_carrera?: string | null;
    area_conocimiento?: string | null;
    duracion_anos?: string | null;
    duracion_semestres?: number | null;
    fecha_inicio: string;
    fecha_fin?: string | null;
    fecha_graduacion?: string | null;
    estado_estudios: EstadoEstudiosEnum;
    promedio_ponderado?: string | null;
    creditos_aprobados?: number | null;
    creditos_totales?: number | null;
    numero_titulo?: string | null;
    numero_diploma?: string | null;
    numero_colegiatura?: string | null;
    colegio_profesional?: string | null;
    pais_institucion?: string;
    mencion_especialidad?: string | null;
    tesis_titulo?: string | null;
    verificado_sunedu?: boolean;
};

