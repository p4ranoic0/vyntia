/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TipoCalculoEnum } from './TipoCalculoEnum';
import type { TipoConfiguracionEnum } from './TipoConfiguracionEnum';
export type ConfiguracionVacaciones = {
    readonly configuracion_id: number;
    tipo_configuracion: TipoConfiguracionEnum;
    readonly tipo_configuracion_display: string;
    area?: number | null;
    readonly area_nombre: string;
    empleado?: number | null;
    readonly empleado_nombre: string;
    dias_por_ano?: number;
    dias_adicionales_antiguedad?: number;
    anos_para_adicional?: number;
    permite_acumulacion?: boolean;
    max_dias_acumulables?: number;
    dias_minimos_solicitud?: number;
    dias_maximos_solicitud?: number;
    dias_anticipacion_minima?: number;
    tipo_calculo?: TipoCalculoEnum;
    readonly tipo_calculo_display: string;
    incluye_feriados?: boolean;
    incluye_fines_semana?: boolean;
    requiere_aprobacion_jefe?: boolean;
    requiere_aprobacion_rrhh?: boolean;
    niveles_aprobacion?: number;
    permite_fraccionamiento?: boolean;
    min_dias_por_fraccion?: number;
    max_fracciones_por_ano?: number;
    activo?: boolean;
    fecha_inicio_vigencia: string;
    fecha_fin_vigencia?: string | null;
    observaciones?: string | null;
    readonly creado_por: number | null;
    readonly creado_por_nombre: string;
    readonly fecha_creacion: string;
    readonly fecha_actualizacion: string;
};

