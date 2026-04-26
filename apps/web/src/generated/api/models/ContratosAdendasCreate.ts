/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { JornadaLaboral5ebEnum } from './JornadaLaboral5ebEnum';
import type { TipoDocumento51aEnum } from './TipoDocumento51aEnum';
/**
 * Serializer para crear contratos y adendas.
 */
export type ContratosAdendasCreate = {
    /**
     * Empleado asociado al contrato/adenda
     */
    empleado: number;
    /**
     * Área donde se ejecuta el contrato
     */
    area: number;
    /**
     * Número del contrato principal
     */
    numero_contrato: string;
    /**
     * Número de adenda (NULL si es contrato inicial)
     */
    numero_adenda?: string | null;
    /**
     * Tipo de documento contractual
     *
     * * `CONTRATO_INDEFINIDO` - Contrato Indefinido
     * * `CONTRATO_FIJO` - Contrato a Plazo Fijo
     * * `CONTRATO_OBRA` - Contrato por Obra o Servicio
     * * `CONTRATO_HONORARIOS` - Contrato de Honorarios
     * * `CONTRATO_PRACTICA` - Contrato de Prácticas
     * * `ADENDA_SALARIAL` - Adenda Salarial
     * * `ADENDA_CARGO` - Adenda de Cambio de Cargo
     * * `ADENDA_HORARIO` - Adenda de Cambio de Horario
     * * `ADENDA_EXTENSION` - Adenda de Extensión
     */
    tipo_documento: TipoDocumento51aEnum;
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
};

