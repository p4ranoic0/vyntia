/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedRolPermisosList } from '../models/PaginatedRolPermisosList';
import type { RolPermisos } from '../models/RolPermisos';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class RolPermisosService {
    /**
     * Asignar permiso a rol
     * Asigna un permiso específico a un rol.
     * @returns RolPermisos
     * @throws ApiError
     */
    public static rrhhRolPermisosCreate(): CancelablePromise<RolPermisos> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/rol-permisos/',
        });
    }
    /**
     * Listar asignaciones rol-permiso
     * Obtiene una lista paginada de todas las asignaciones de permisos a roles.
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @returns PaginatedRolPermisosList
     * @throws ApiError
     */
    public static rrhhRolPermisosList(
        ordering?: string,
        page?: number,
        pageSize?: number,
        search?: string,
    ): CancelablePromise<PaginatedRolPermisosList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/rol-permisos/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }
    /**
     * Remover permiso de rol
     * Remueve un permiso específico de un rol.
     * @param rolPermisoId Un valor de entero único que identifique este rol permisos.
     * @returns void
     * @throws ApiError
     */
    public static rrhhRolPermisosDestroy(
        rolPermisoId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/rol-permisos/{rol_permiso_id}/',
            path: {
                'rol_permiso_id': rolPermisoId,
            },
        });
    }
    /**
     * Obtener asignación rol-permiso
     * Obtiene los detalles de una asignación específica por su ID.
     * @param rolPermisoId Un valor de entero único que identifique este rol permisos.
     * @returns RolPermisos
     * @throws ApiError
     */
    public static rrhhRolPermisosRetrieve(
        rolPermisoId: number,
    ): CancelablePromise<RolPermisos> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/rol-permisos/{rol_permiso_id}/',
            path: {
                'rol_permiso_id': rolPermisoId,
            },
        });
    }
}
