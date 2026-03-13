/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EstadoEnum } from './EstadoEnum';
import type { TipoDocumento51aEnum } from './TipoDocumento51aEnum';
/**
 * Serializer simplificado para listados de contratos.
 */
export type ContratosAdendasList = {
    readonly contrato_id: number;
    /**
     * Número del contrato principal
     */
    numero_contrato: string;
    /**
     * Número de adenda (NULL si es contrato inicial)
     */
    numero_adenda?: string | null;
    /**
     * Empleado asociado al contrato/adenda
     */
    empleado: number;
    readonly empleado_nombre: string;
    readonly area_nombre: string;
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
    readonly tipo_documento_texto: string;
    /**
     * Fecha de inicio del contrato/adenda
     */
    fecha_inicio: string;
    /**
     * Fecha de fin del contrato (NULL para indefinidos)
     */
    fecha_fin?: string | null;
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
    readonly estado_texto: string;
    readonly dias_hasta_vencimiento: string;
    readonly esta_vigente: string;
};

