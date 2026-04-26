/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Area } from './Area';
import type { EmpleadoList } from './EmpleadoList';
import type { EstadoEnum } from './EstadoEnum';
import type { JornadaLaboral5ebEnum } from './JornadaLaboral5ebEnum';
import type { TipoDocumento51aEnum } from './TipoDocumento51aEnum';
/**
 * Serializer principal para contratos y adendas.
 */
export type ContratosAdendas = {
    readonly contrato_id: number;
    /**
     * Empleado asociado al contrato/adenda
     */
    empleado: number;
    readonly empleado_detalle: EmpleadoList;
    /**
     * Área donde se ejecuta el contrato
     */
    area: number;
    readonly area_detalle: Area;
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
     * Salario neto calculado
     */
    salario_neto?: string | null;
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
    /**
     * Indica si se ha generado el documento PDF
     */
    documento_generado?: boolean;
    /**
     * Fecha de creación del registro
     */
    readonly fecha_creacion: string;
    /**
     * Fecha de última modificación
     */
    readonly fecha_modificacion: string;
    /**
     * Usuario que creó el registro
     */
    readonly creado_por: number | null;
    /**
     * Usuario que modificó el registro
     */
    readonly modificado_por: number | null;
    readonly dias_hasta_vencimiento: string;
    readonly esta_vigente: string;
    readonly esta_vencido: string;
    readonly duracion_dias: string;
    readonly duracion_meses: string;
    readonly es_contrato_inicial: string;
    readonly es_adenda: string;
    readonly tipo_documento_texto: string;
    readonly estado_texto: string;
    readonly jornada_texto: string;
};

