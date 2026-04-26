/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoSolicitudEnum } from './EstadoSolicitudEnum';
import type { TipoSolicitudEnum } from './TipoSolicitudEnum';
export type SolicitudVacaciones = {
    readonly solicitud_id: number;
    empleado: number;
    readonly empleado_nombre: string;
    readonly empleado_rut: string;
    readonly area_nombre: string;
    periodo_vacacional: number;
    readonly periodo_label: string;
    readonly contrato_id: string;
    readonly contrato_numero: string;
    tipo_solicitud?: TipoSolicitudEnum;
    readonly tipo_solicitud_display: string;
    fecha_inicio: string;
    fecha_fin: string;
    dias_solicitados: string;
    medio_dia?: boolean;
    readonly dias_calendario: string;
    readonly dias_habiles: string;
    motivo_solicitud: string;
    observaciones_empleado?: string | null;
    readonly estado_solicitud: EstadoSolicitudEnum;
    readonly estado_solicitud_display: string;
    readonly fecha_envio: string | null;
    readonly aprobado_por_jefe: boolean;
    readonly jefe_aprobador: number | null;
    readonly jefe_aprobador_nombre: string;
    readonly fecha_aprobacion_jefe: string | null;
    observaciones_jefe?: string | null;
    readonly aprobado_por_rrhh: boolean;
    readonly rrhh_aprobador: number | null;
    readonly rrhh_aprobador_nombre: string;
    readonly fecha_aprobacion_rrhh: string | null;
    observaciones_rrhh?: string | null;
    motivo_rechazo?: string | null;
    readonly rechazado_por: number | null;
    readonly fecha_rechazo: string | null;
    motivo_cancelacion?: string | null;
    readonly cancelado_por: number | null;
    readonly fecha_cancelacion: string | null;
    readonly fecha_creacion: string;
    readonly fecha_actualizacion: string;
};

