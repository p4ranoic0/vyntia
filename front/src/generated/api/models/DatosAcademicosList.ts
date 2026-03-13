/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoEstudiosEnum } from './EstadoEstudiosEnum';
import type { EstadoRegistroEnum } from './EstadoRegistroEnum';
import type { ModalidadEstudioEnum } from './ModalidadEstudioEnum';
import type { NivelEducativoA5dEnum } from './NivelEducativoA5dEnum';
import type { TipoInstitucionEnum } from './TipoInstitucionEnum';
export type DatosAcademicosList = {
    readonly academico_id: number;
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
    departamento_institucion?: string | null;
    provincia_institucion?: string | null;
    distrito_institucion?: string | null;
    mencion_especialidad?: string | null;
    tesis_titulo?: string | null;
    reconocimientos?: string | null;
    ruta_certificado?: string | null;
    ruta_titulo?: string | null;
    ruta_diploma?: string | null;
    verificado_sunedu?: boolean;
    fecha_verificacion_sunedu?: string | null;
    codigo_verificacion_sunedu?: string | null;
    estado_registro?: EstadoRegistroEnum;
    observaciones?: string | null;
    readonly fecha_registro: string;
    readonly fecha_actualizacion: string;
    empleado: number;
};

