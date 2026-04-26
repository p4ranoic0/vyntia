/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Optimized serializer for area list view.
 */
export type AreaList = {
    readonly area_id: number;
    nombre_organo?: string;
    nombre_unidad_organica?: string;
    siglas_area?: string;
    descripcion_area?: string | null;
    /**
     * Get total number of employees in area.
     */
    readonly empleados_count: number;
};

