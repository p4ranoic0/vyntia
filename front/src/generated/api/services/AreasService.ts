/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Area } from '../models/Area';
import type { AreaRequest } from '../models/AreaRequest';
import type { PaginatedAreaListList } from '../models/PaginatedAreaListList';
import type { PatchedAreaRequest } from '../models/PatchedAreaRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AreasService {
    /**
     * Crear área
     * Crea una nueva área organizacional.
     * @param requestBody
     * @returns Area
     * @throws ApiError
     */
    public static rrhhAreasCreate(
        requestBody?: AreaRequest,
    ): CancelablePromise<Area> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/areas/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar áreas
     * Obtiene una lista paginada de todas las áreas organizacionales con filtros opcionales.
     * @param estado * `activa` - Activa
     * * `inactiva` - Inactiva
     * @param estadoArea * `activo` - Activo
     * * `inactivo` - Inactivo
     * * `reestructuracion` - Reestructuración
     * @param maxEmpleados
     * @param minEmpleados
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param organo
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @param siglas
     * @param unidadOrganica
     * @returns PaginatedAreaListList
     * @throws ApiError
     */
    public static rrhhAreasList(
        estado?: 'activa' | 'inactiva',
        estadoArea?: 'activo' | 'inactivo' | 'reestructuracion',
        maxEmpleados?: number,
        minEmpleados?: number,
        ordering?: string,
        organo?: string,
        page?: number,
        pageSize?: number,
        search?: string,
        siglas?: string,
        unidadOrganica?: string,
    ): CancelablePromise<PaginatedAreaListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/areas/',
            query: {
                'estado': estado,
                'estado_area': estadoArea,
                'max_empleados': maxEmpleados,
                'min_empleados': minEmpleados,
                'ordering': ordering,
                'organo': organo,
                'page': page,
                'page_size': pageSize,
                'search': search,
                'siglas': siglas,
                'unidad_organica': unidadOrganica,
            },
        });
    }
    /**
     * Obtener resumen de todas las áreas
     * Obtiene un resumen estadístico de todas las áreas del sistema.
     * @returns Area
     * @throws ApiError
     */
    public static rrhhAreasResumenRetrieve(): CancelablePromise<Area> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/areas/resumen/',
        });
    }
    /**
     * Eliminar área
     * Elimina un área del sistema.
     * @param areaId Un valor de entero único que identifique este area.
     * @returns void
     * @throws ApiError
     */
    public static rrhhAreasDestroy(
        areaId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/areas/{area_id}/',
            path: {
                'area_id': areaId,
            },
        });
    }
    /**
     * Obtener área
     * Obtiene los detalles de un área específica por su ID.
     * @param areaId Un valor de entero único que identifique este area.
     * @returns Area
     * @throws ApiError
     */
    public static rrhhAreasRetrieve(
        areaId: number,
    ): CancelablePromise<Area> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/areas/{area_id}/',
            path: {
                'area_id': areaId,
            },
        });
    }
    /**
     * Actualizar área parcialmente
     * Actualiza parcialmente un área existente.
     * @param areaId Un valor de entero único que identifique este area.
     * @param requestBody
     * @returns Area
     * @throws ApiError
     */
    public static rrhhAreasPartialUpdate(
        areaId: number,
        requestBody?: PatchedAreaRequest,
    ): CancelablePromise<Area> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/rrhh/areas/{area_id}/',
            path: {
                'area_id': areaId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Actualizar área
     * Actualiza completamente un área existente.
     * @param areaId Un valor de entero único que identifique este area.
     * @param requestBody
     * @returns Area
     * @throws ApiError
     */
    public static rrhhAreasUpdate(
        areaId: number,
        requestBody?: AreaRequest,
    ): CancelablePromise<Area> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/rrhh/areas/{area_id}/',
            path: {
                'area_id': areaId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Obtener empleados del área
     * Obtiene una lista de todos los empleados que pertenecen a un área específica.
     * @param areaId Un valor de entero único que identifique este area.
     * @returns Area
     * @throws ApiError
     */
    public static rrhhAreasEmpleadosRetrieve(
        areaId: number,
    ): CancelablePromise<Area> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/areas/{area_id}/empleados/',
            path: {
                'area_id': areaId,
            },
        });
    }
    /**
     * Obtener estadísticas del área
     * Obtiene estadísticas detalladas de un área específica incluyendo métricas de empleados.
     * @param areaId Un valor de entero único que identifique este area.
     * @returns Area
     * @throws ApiError
     */
    public static rrhhAreasEstadisticasRetrieve(
        areaId: number,
    ): CancelablePromise<Area> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/areas/{area_id}/estadisticas/',
            path: {
                'area_id': areaId,
            },
        });
    }
}
