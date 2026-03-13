/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoEnum } from './EstadoEnum';
import type { JornadaLaboral5ebEnum } from './JornadaLaboral5ebEnum';
/**
 * Serializer para actualizar contratos y adendas.
 */
export type ContratosAdendasUpdate = {
    /**
     * Fecha de inicio del contrato/adenda
     */
    fecha_inicio: string;
    /**
     * Fecha de fin del contrato (NULL para indefinidos)
     */
    fecha_fin?: string | null;
    /**
     * Fecha de firma del documento
     */
    fecha_firma?: string | null;
    /**
     * Salario bruto mensual
     */
    salario_bruto: string;
    /**
     * Cargo o puesto de trabajo
     */
    cargo: string;
    /**
     * Tipo de jornada laboral
     *
     * * `COMPLETA` - Jornada Completa
     * * `PARCIAL` - Jornada Parcial
     * * `REDUCIDA` - Jornada Reducida
     * * `FLEXIBLE` - Jornada Flexible
     */
    jornada_laboral?: JornadaLaboral5ebEnum;
    /**
     * Descripción de funciones y responsabilidades
     */
    funciones?: string | null;
    /**
     * Lugar de trabajo
     */
    lugar_trabajo?: string | null;
    /**
     * Horario de trabajo
     */
    horario_trabajo?: string | null;
    /**
     * Observaciones adicionales
     */
    observaciones?: string | null;
    /**
     * Estado actual del contrato/adenda
     *
     * * `BORRADOR` - Borrador
     * * `PENDIENTE` - Pendiente de Firma
     * * `ACTIVO` - Activo
     * * `VENCIDO` - Vencido
     * * `TERMINADO` - Terminado
     * * `ANULADO` - Anulado
     */
    estado?: EstadoEnum;
};

