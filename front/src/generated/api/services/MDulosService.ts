/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Modulos } from '../models/Modulos';
import type { ModulosRequest } from '../models/ModulosRequest';
import type { PaginatedModulosList } from '../models/PaginatedModulosList';
import type { PatchedModulosRequest } from '../models/PatchedModulosRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class MDulosService {
    /**
     * Crear módulo
     * Crea un nuevo módulo en el sistema.
     * @param requestBody
     * @returns Modulos
     * @throws ApiError
     */
    public static rrhhModulosCreate(
        requestBody: ModulosRequest,
    ): CancelablePromise<Modulos> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/modulos/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar módulos
     * Obtiene una lista paginada de todos los módulos del sistema con filtros opcionales.
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @returns PaginatedModulosList
     * @throws ApiError
     */
    public static rrhhModulosList(
        ordering?: string,
        page?: number,
        pageSize?: number,
        search?: string,
    ): CancelablePromise<PaginatedModulosList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/modulos/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }
    /**
     * Eliminar módulo
     * Elimina un módulo del sistema.
     * @param moduloId Un valor de entero único que identifique este modulos.
     * @returns void
     * @throws ApiError
     */
    public static rrhhModulosDestroy(
        moduloId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/modulos/{modulo_id}/',
            path: {
                'modulo_id': moduloId,
            },
        });
    }
    /**
     * Obtener módulo
     * Obtiene los detalles de un módulo específico por su ID.
     * @param moduloId Un valor de entero único que identifique este modulos.
     * @returns Modulos
     * @throws ApiError
     */
    public static rrhhModulosRetrieve(
        moduloId: number,
    ): CancelablePromise<Modulos> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/modulos/{modulo_id}/',
            path: {
                'modulo_id': moduloId,
            },
        });
    }
    /**
     * Actualizar módulo parcialmente
     * Actualiza parcialmente un módulo existente.
     * @param moduloId Un valor de entero único que identifique este modulos.
     * @param requestBody
     * @returns Modulos
     * @throws ApiError
     */
    public static rrhhModulosPartialUpdate(
        moduloId: number,
        requestBody?: PatchedModulosRequest,
    ): CancelablePromise<Modulos> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/rrhh/modulos/{modulo_id}/',
            path: {
                'modulo_id': moduloId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Actualizar módulo
     * Actualiza completamente un módulo existente.
     * @param moduloId Un valor de entero único que identifique este modulos.
     * @param requestBody
     * @returns Modulos
     * @throws ApiError
     */
    public static rrhhModulosUpdate(
        moduloId: number,
        requestBody: ModulosRequest,
    ): CancelablePromise<Modulos> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/rrhh/modulos/{modulo_id}/',
            path: {
                'modulo_id': moduloId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
