/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Empleado } from '../models/Empleado';
import type { EmpleadoCreate } from '../models/EmpleadoCreate';
import type { EmpleadoCreateRequest } from '../models/EmpleadoCreateRequest';
import type { EmpleadoUpdate } from '../models/EmpleadoUpdate';
import type { EmpleadoUpdateRequest } from '../models/EmpleadoUpdateRequest';
import type { PaginatedEmpleadoListList } from '../models/PaginatedEmpleadoListList';
import type { PatchedEmpleadoUpdateRequest } from '../models/PatchedEmpleadoUpdateRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class EmpleadosService {
    /**
     * Crear empleado
     * Crea un nuevo empleado en el sistema.
     * @param requestBody
     * @returns EmpleadoCreate
     * @throws ApiError
     */
    public static rrhhEmpleadosCreate(
        requestBody: EmpleadoCreateRequest,
    ): CancelablePromise<EmpleadoCreate> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/empleados/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar empleados
     * Obtiene una lista paginada de todos los empleados con filtros opcionales.
     * @param apeMaterno
     * @param apePaterno
     * @param area
     * @param areaSiglas
     * @param categoria
     * @param distrito
     * @param dni
     * @param edadMax
     * @param edadMin
     * @param estado * `activo` - Activo
     * * `inactivo` - Inactivo
     * * `cesado` - Cesado
     * @param estadoCivil * `soltero` - Soltero
     * * `casado` - Casado
     * * `divorciado` - Divorciado
     * * `viudo` - Viudo
     * * `conviviente` - Conviviente
     * @param fechaNacDesde
     * @param fechaNacHasta
     * @param genero * `masculino` - Masculino
     * * `femenino` - Femenino
     * * `otro` - Otro
     * * `no_especifica` - No especifica
     * @param nombres
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param puesto
     * @param regLaboral
     * @param remuneracionMax
     * @param remuneracionMin
     * @param search Un término de búsqueda.
     * @param tieneConyuge
     * @param tieneHijos
     * @returns PaginatedEmpleadoListList
     * @throws ApiError
     */
    public static rrhhEmpleadosList(
        apeMaterno?: string,
        apePaterno?: string,
        area?: number,
        areaSiglas?: string,
        categoria?: string,
        distrito?: string,
        dni?: string,
        edadMax?: number,
        edadMin?: number,
        estado?: 'activo' | 'cesado' | 'inactivo',
        estadoCivil?: 'casado' | 'conviviente' | 'divorciado' | 'soltero' | 'viudo',
        fechaNacDesde?: string,
        fechaNacHasta?: string,
        genero?: 'femenino' | 'masculino' | 'no_especifica' | 'otro',
        nombres?: string,
        ordering?: string,
        page?: number,
        pageSize?: number,
        puesto?: string,
        regLaboral?: string,
        remuneracionMax?: number,
        remuneracionMin?: number,
        search?: string,
        tieneConyuge?: boolean,
        tieneHijos?: boolean,
    ): CancelablePromise<PaginatedEmpleadoListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/empleados/',
            query: {
                'ape_materno': apeMaterno,
                'ape_paterno': apePaterno,
                'area': area,
                'area_siglas': areaSiglas,
                'categoria': categoria,
                'distrito': distrito,
                'dni': dni,
                'edad_max': edadMax,
                'edad_min': edadMin,
                'estado': estado,
                'estado_civil': estadoCivil,
                'fecha_nac_desde': fechaNacDesde,
                'fecha_nac_hasta': fechaNacHasta,
                'genero': genero,
                'nombres': nombres,
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'puesto': puesto,
                'reg_laboral': regLaboral,
                'remuneracion_max': remuneracionMax,
                'remuneracion_min': remuneracionMin,
                'search': search,
                'tiene_conyuge': tieneConyuge,
                'tiene_hijos': tieneHijos,
            },
        });
    }
    /**
     * Eliminar empleado
     * Elimina un empleado del sistema.
     * @param empleadoId Un valor de entero único que identifique este empleado.
     * @returns void
     * @throws ApiError
     */
    public static rrhhEmpleadosDestroy(
        empleadoId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/empleados/{empleado_id}/',
            path: {
                'empleado_id': empleadoId,
            },
        });
    }
    /**
     * Obtener empleado
     * Obtiene los detalles de un empleado específico por su ID.
     * @param empleadoId Un valor de entero único que identifique este empleado.
     * @returns Empleado
     * @throws ApiError
     */
    public static rrhhEmpleadosRetrieve(
        empleadoId: number,
    ): CancelablePromise<Empleado> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/empleados/{empleado_id}/',
            path: {
                'empleado_id': empleadoId,
            },
        });
    }
    /**
     * Actualizar empleado parcialmente
     * Actualiza parcialmente un empleado existente.
     * @param empleadoId Un valor de entero único que identifique este empleado.
     * @param requestBody
     * @returns EmpleadoUpdate
     * @throws ApiError
     */
    public static rrhhEmpleadosPartialUpdate(
        empleadoId: number,
        requestBody?: PatchedEmpleadoUpdateRequest,
    ): CancelablePromise<EmpleadoUpdate> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/rrhh/empleados/{empleado_id}/',
            path: {
                'empleado_id': empleadoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Actualizar empleado
     * Actualiza completamente un empleado existente.
     * @param empleadoId Un valor de entero único que identifique este empleado.
     * @param requestBody
     * @returns EmpleadoUpdate
     * @throws ApiError
     */
    public static rrhhEmpleadosUpdate(
        empleadoId: number,
        requestBody: EmpleadoUpdateRequest,
    ): CancelablePromise<EmpleadoUpdate> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/rrhh/empleados/{empleado_id}/',
            path: {
                'empleado_id': empleadoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
