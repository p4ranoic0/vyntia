/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AreaDetail } from '../models/AreaDetail';
import type { AreaDetailRequest } from '../models/AreaDetailRequest';
import type { DatosAcademicos } from '../models/DatosAcademicos';
import type { DatosAcademicosRequest } from '../models/DatosAcademicosRequest';
import type { DatosFamiliares } from '../models/DatosFamiliares';
import type { DatosFamiliaresRequest } from '../models/DatosFamiliaresRequest';
import type { DatosLaborales } from '../models/DatosLaborales';
import type { DatosLaboralesRequest } from '../models/DatosLaboralesRequest';
import type { EmpleadoDetail } from '../models/EmpleadoDetail';
import type { EmpleadoDetailRequest } from '../models/EmpleadoDetailRequest';
import type { HistorialUbicaciones } from '../models/HistorialUbicaciones';
import type { HistorialUbicacionesRequest } from '../models/HistorialUbicacionesRequest';
import type { PaginatedAreaListList } from '../models/PaginatedAreaListList';
import type { PaginatedDatosAcademicosListList } from '../models/PaginatedDatosAcademicosListList';
import type { PaginatedDatosFamiliaresListList } from '../models/PaginatedDatosFamiliaresListList';
import type { PaginatedDatosLaboralesListList } from '../models/PaginatedDatosLaboralesListList';
import type { PaginatedEmpleadoListList } from '../models/PaginatedEmpleadoListList';
import type { PaginatedHistorialUbicacionesList } from '../models/PaginatedHistorialUbicacionesList';
import type { PaginatedPermisoListList } from '../models/PaginatedPermisoListList';
import type { PaginatedRolListList } from '../models/PaginatedRolListList';
import type { PaginatedRolPermisosDetailList } from '../models/PaginatedRolPermisosDetailList';
import type { PaginatedUsuarioListList } from '../models/PaginatedUsuarioListList';
import type { PatchedAreaDetailRequest } from '../models/PatchedAreaDetailRequest';
import type { PatchedDatosAcademicosRequest } from '../models/PatchedDatosAcademicosRequest';
import type { PatchedDatosFamiliaresRequest } from '../models/PatchedDatosFamiliaresRequest';
import type { PatchedDatosLaboralesRequest } from '../models/PatchedDatosLaboralesRequest';
import type { PatchedEmpleadoDetailRequest } from '../models/PatchedEmpleadoDetailRequest';
import type { PatchedHistorialUbicacionesRequest } from '../models/PatchedHistorialUbicacionesRequest';
import type { PatchedPermisoDetailRequest } from '../models/PatchedPermisoDetailRequest';
import type { PatchedRolDetailRequest } from '../models/PatchedRolDetailRequest';
import type { PatchedRolPermisosRequest } from '../models/PatchedRolPermisosRequest';
import type { PatchedUsuarioDetailRequest } from '../models/PatchedUsuarioDetailRequest';
import type { PermisoDetail } from '../models/PermisoDetail';
import type { PermisoDetailRequest } from '../models/PermisoDetailRequest';
import type { RolDetail } from '../models/RolDetail';
import type { RolDetailRequest } from '../models/RolDetailRequest';
import type { RolPermisos } from '../models/RolPermisos';
import type { RolPermisosDetail } from '../models/RolPermisosDetail';
import type { RolPermisosRequest } from '../models/RolPermisosRequest';
import type { TokenRefresh } from '../models/TokenRefresh';
import type { TokenRefreshRequest } from '../models/TokenRefreshRequest';
import type { UsuarioDetail } from '../models/UsuarioDetail';
import type { UsuarioDetailRequest } from '../models/UsuarioDetailRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class LegacyService {
    /**
     * Gestión de Áreas Organizacionales.
     *
     * Lista, crea, actualiza y elimina áreas de la organización.
     * Incluye filtros por órgano y siglas.
     * @param requestBody
     * @returns AreaDetail
     * @throws ApiError
     */
    public static legacyAreasCreate(
        requestBody?: AreaDetailRequest,
    ): CancelablePromise<AreaDetail> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/legacy/areas/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Áreas Organizacionales.
     *
     * Lista, crea, actualiza y elimina áreas de la organización.
     * Incluye filtros por órgano y siglas.
     * @param estadoArea * `activo` - Activo
     * * `inactivo` - Inactivo
     * * `reestructuracion` - Reestructuración
     * @param nombreOrgano
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param siglasArea
     * @returns PaginatedAreaListList
     * @throws ApiError
     */
    public static legacyAreasList(
        estadoArea?: 'activo' | 'inactivo' | 'reestructuracion',
        nombreOrgano?: string,
        page?: number,
        pageSize?: number,
        siglasArea?: string,
    ): CancelablePromise<PaginatedAreaListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/areas/',
            query: {
                'estado_area': estadoArea,
                'nombre_organo': nombreOrgano,
                'page': page,
                'page_size': pageSize,
                'siglas_area': siglasArea,
            },
        });
    }
    /**
     * Gestión de Áreas Organizacionales.
     *
     * Lista, crea, actualiza y elimina áreas de la organización.
     * Incluye filtros por órgano y siglas.
     * @param areaId Un valor de entero único que identifique este area.
     * @returns void
     * @throws ApiError
     */
    public static legacyAreasDestroy(
        areaId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/legacy/areas/{area_id}/',
            path: {
                'area_id': areaId,
            },
        });
    }
    /**
     * Gestión de Áreas Organizacionales.
     *
     * Lista, crea, actualiza y elimina áreas de la organización.
     * Incluye filtros por órgano y siglas.
     * @param areaId Un valor de entero único que identifique este area.
     * @returns AreaDetail
     * @throws ApiError
     */
    public static legacyAreasRetrieve(
        areaId: number,
    ): CancelablePromise<AreaDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/areas/{area_id}/',
            path: {
                'area_id': areaId,
            },
        });
    }
    /**
     * Gestión de Áreas Organizacionales.
     *
     * Lista, crea, actualiza y elimina áreas de la organización.
     * Incluye filtros por órgano y siglas.
     * @param areaId Un valor de entero único que identifique este area.
     * @param requestBody
     * @returns AreaDetail
     * @throws ApiError
     */
    public static legacyAreasPartialUpdate(
        areaId: number,
        requestBody?: PatchedAreaDetailRequest,
    ): CancelablePromise<AreaDetail> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/legacy/areas/{area_id}/',
            path: {
                'area_id': areaId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Áreas Organizacionales.
     *
     * Lista, crea, actualiza y elimina áreas de la organización.
     * Incluye filtros por órgano y siglas.
     * @param areaId Un valor de entero único que identifique este area.
     * @param requestBody
     * @returns AreaDetail
     * @throws ApiError
     */
    public static legacyAreasUpdate(
        areaId: number,
        requestBody?: AreaDetailRequest,
    ): CancelablePromise<AreaDetail> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/legacy/areas/{area_id}/',
            path: {
                'area_id': areaId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Empleados.
     *
     * CRUD completo de empleados incluyendo:
     * - Datos personales (nombres, documentos, contacto)
     * - Datos familiares, académicos y laborales
     * - Historial de ubicaciones (departamentos/cargos)
     *
     * Soporta filtros avanzados y búsqueda por nombre/documento.
     * @param requestBody
     * @returns EmpleadoDetail
     * @throws ApiError
     */
    public static legacyEmpleadosCreate(
        requestBody: EmpleadoDetailRequest,
    ): CancelablePromise<EmpleadoDetail> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/legacy/empleados/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Empleados.
     *
     * CRUD completo de empleados incluyendo:
     * - Datos personales (nombres, documentos, contacto)
     * - Datos familiares, académicos y laborales
     * - Historial de ubicaciones (departamentos/cargos)
     *
     * Soporta filtros avanzados y búsqueda por nombre/documento.
     * @param dni Buscar por DNI
     * @param estado Solo activos
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Buscar por nombre
     * @returns PaginatedEmpleadoListList
     * @throws ApiError
     */
    public static legacyEmpleadosList(
        dni?: string,
        estado?: boolean,
        page?: number,
        pageSize?: number,
        search?: string,
    ): CancelablePromise<PaginatedEmpleadoListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/empleados/',
            query: {
                'dni': dni,
                'estado': estado,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }
    /**
     * Gestión de Empleados.
     *
     * CRUD completo de empleados incluyendo:
     * - Datos personales (nombres, documentos, contacto)
     * - Datos familiares, académicos y laborales
     * - Historial de ubicaciones (departamentos/cargos)
     *
     * Soporta filtros avanzados y búsqueda por nombre/documento.
     * @param empleadoId Un valor de entero único que identifique este empleado.
     * @returns void
     * @throws ApiError
     */
    public static legacyEmpleadosDestroy(
        empleadoId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/legacy/empleados/{empleado_id}/',
            path: {
                'empleado_id': empleadoId,
            },
        });
    }
    /**
     * Gestión de Empleados.
     *
     * CRUD completo de empleados incluyendo:
     * - Datos personales (nombres, documentos, contacto)
     * - Datos familiares, académicos y laborales
     * - Historial de ubicaciones (departamentos/cargos)
     *
     * Soporta filtros avanzados y búsqueda por nombre/documento.
     * @param empleadoId Un valor de entero único que identifique este empleado.
     * @returns EmpleadoDetail
     * @throws ApiError
     */
    public static legacyEmpleadosRetrieve(
        empleadoId: number,
    ): CancelablePromise<EmpleadoDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/empleados/{empleado_id}/',
            path: {
                'empleado_id': empleadoId,
            },
        });
    }
    /**
     * Gestión de Empleados.
     *
     * CRUD completo de empleados incluyendo:
     * - Datos personales (nombres, documentos, contacto)
     * - Datos familiares, académicos y laborales
     * - Historial de ubicaciones (departamentos/cargos)
     *
     * Soporta filtros avanzados y búsqueda por nombre/documento.
     * @param empleadoId Un valor de entero único que identifique este empleado.
     * @param requestBody
     * @returns EmpleadoDetail
     * @throws ApiError
     */
    public static legacyEmpleadosPartialUpdate(
        empleadoId: number,
        requestBody?: PatchedEmpleadoDetailRequest,
    ): CancelablePromise<EmpleadoDetail> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/legacy/empleados/{empleado_id}/',
            path: {
                'empleado_id': empleadoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Empleados.
     *
     * CRUD completo de empleados incluyendo:
     * - Datos personales (nombres, documentos, contacto)
     * - Datos familiares, académicos y laborales
     * - Historial de ubicaciones (departamentos/cargos)
     *
     * Soporta filtros avanzados y búsqueda por nombre/documento.
     * @param empleadoId Un valor de entero único que identifique este empleado.
     * @param requestBody
     * @returns EmpleadoDetail
     * @throws ApiError
     */
    public static legacyEmpleadosUpdate(
        empleadoId: number,
        requestBody: EmpleadoDetailRequest,
    ): CancelablePromise<EmpleadoDetail> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/legacy/empleados/{empleado_id}/',
            path: {
                'empleado_id': empleadoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Datos Familiares de Empleados.
     * @param requestBody
     * @returns DatosFamiliares
     * @throws ApiError
     */
    public static legacyDatosFamiliaresCreate(
        requestBody: DatosFamiliaresRequest,
    ): CancelablePromise<DatosFamiliares> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/legacy/datos-familiares/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Datos Familiares de Empleados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @returns PaginatedDatosFamiliaresListList
     * @throws ApiError
     */
    public static legacyDatosFamiliaresList(
        page?: number,
        pageSize?: number,
    ): CancelablePromise<PaginatedDatosFamiliaresListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/datos-familiares/',
            query: {
                'page': page,
                'page_size': pageSize,
            },
        });
    }
    /**
     * Datos Familiares de Empleados.
     * @param familiarId Un valor de entero único que identifique este datos familiares.
     * @returns void
     * @throws ApiError
     */
    public static legacyDatosFamiliaresDestroy(
        familiarId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/legacy/datos-familiares/{familiar_id}/',
            path: {
                'familiar_id': familiarId,
            },
        });
    }
    /**
     * Datos Familiares de Empleados.
     * @param familiarId Un valor de entero único que identifique este datos familiares.
     * @returns DatosFamiliares
     * @throws ApiError
     */
    public static legacyDatosFamiliaresRetrieve(
        familiarId: number,
    ): CancelablePromise<DatosFamiliares> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/datos-familiares/{familiar_id}/',
            path: {
                'familiar_id': familiarId,
            },
        });
    }
    /**
     * Datos Familiares de Empleados.
     * @param familiarId Un valor de entero único que identifique este datos familiares.
     * @param requestBody
     * @returns DatosFamiliares
     * @throws ApiError
     */
    public static legacyDatosFamiliaresPartialUpdate(
        familiarId: number,
        requestBody?: PatchedDatosFamiliaresRequest,
    ): CancelablePromise<DatosFamiliares> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/legacy/datos-familiares/{familiar_id}/',
            path: {
                'familiar_id': familiarId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Datos Familiares de Empleados.
     * @param familiarId Un valor de entero único que identifique este datos familiares.
     * @param requestBody
     * @returns DatosFamiliares
     * @throws ApiError
     */
    public static legacyDatosFamiliaresUpdate(
        familiarId: number,
        requestBody: DatosFamiliaresRequest,
    ): CancelablePromise<DatosFamiliares> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/legacy/datos-familiares/{familiar_id}/',
            path: {
                'familiar_id': familiarId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Datos Académicos de Empleados.
     * @param requestBody
     * @returns DatosAcademicos
     * @throws ApiError
     */
    public static legacyDatosAcademicosCreate(
        requestBody: DatosAcademicosRequest,
    ): CancelablePromise<DatosAcademicos> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/legacy/datos-academicos/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Datos Académicos de Empleados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @returns PaginatedDatosAcademicosListList
     * @throws ApiError
     */
    public static legacyDatosAcademicosList(
        page?: number,
        pageSize?: number,
    ): CancelablePromise<PaginatedDatosAcademicosListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/datos-academicos/',
            query: {
                'page': page,
                'page_size': pageSize,
            },
        });
    }
    /**
     * Datos Académicos de Empleados.
     * @param academicoId Un valor de entero único que identifique este datos academicos.
     * @returns void
     * @throws ApiError
     */
    public static legacyDatosAcademicosDestroy(
        academicoId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/legacy/datos-academicos/{academico_id}/',
            path: {
                'academico_id': academicoId,
            },
        });
    }
    /**
     * Datos Académicos de Empleados.
     * @param academicoId Un valor de entero único que identifique este datos academicos.
     * @returns DatosAcademicos
     * @throws ApiError
     */
    public static legacyDatosAcademicosRetrieve(
        academicoId: number,
    ): CancelablePromise<DatosAcademicos> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/datos-academicos/{academico_id}/',
            path: {
                'academico_id': academicoId,
            },
        });
    }
    /**
     * Datos Académicos de Empleados.
     * @param academicoId Un valor de entero único que identifique este datos academicos.
     * @param requestBody
     * @returns DatosAcademicos
     * @throws ApiError
     */
    public static legacyDatosAcademicosPartialUpdate(
        academicoId: number,
        requestBody?: PatchedDatosAcademicosRequest,
    ): CancelablePromise<DatosAcademicos> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/legacy/datos-academicos/{academico_id}/',
            path: {
                'academico_id': academicoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Datos Académicos de Empleados.
     * @param academicoId Un valor de entero único que identifique este datos academicos.
     * @param requestBody
     * @returns DatosAcademicos
     * @throws ApiError
     */
    public static legacyDatosAcademicosUpdate(
        academicoId: number,
        requestBody: DatosAcademicosRequest,
    ): CancelablePromise<DatosAcademicos> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/legacy/datos-academicos/{academico_id}/',
            path: {
                'academico_id': academicoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Datos Laborales de Empleados.
     * @param requestBody
     * @returns DatosLaborales
     * @throws ApiError
     */
    public static legacyDatosLaboralesCreate(
        requestBody: DatosLaboralesRequest,
    ): CancelablePromise<DatosLaborales> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/legacy/datos-laborales/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Datos Laborales de Empleados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @returns PaginatedDatosLaboralesListList
     * @throws ApiError
     */
    public static legacyDatosLaboralesList(
        page?: number,
        pageSize?: number,
    ): CancelablePromise<PaginatedDatosLaboralesListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/datos-laborales/',
            query: {
                'page': page,
                'page_size': pageSize,
            },
        });
    }
    /**
     * Datos Laborales de Empleados.
     * @param datoLaboralId Un valor de entero único que identifique este datos laborales.
     * @returns void
     * @throws ApiError
     */
    public static legacyDatosLaboralesDestroy(
        datoLaboralId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/legacy/datos-laborales/{dato_laboral_id}/',
            path: {
                'dato_laboral_id': datoLaboralId,
            },
        });
    }
    /**
     * Datos Laborales de Empleados.
     * @param datoLaboralId Un valor de entero único que identifique este datos laborales.
     * @returns DatosLaborales
     * @throws ApiError
     */
    public static legacyDatosLaboralesRetrieve(
        datoLaboralId: number,
    ): CancelablePromise<DatosLaborales> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/datos-laborales/{dato_laboral_id}/',
            path: {
                'dato_laboral_id': datoLaboralId,
            },
        });
    }
    /**
     * Datos Laborales de Empleados.
     * @param datoLaboralId Un valor de entero único que identifique este datos laborales.
     * @param requestBody
     * @returns DatosLaborales
     * @throws ApiError
     */
    public static legacyDatosLaboralesPartialUpdate(
        datoLaboralId: number,
        requestBody?: PatchedDatosLaboralesRequest,
    ): CancelablePromise<DatosLaborales> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/legacy/datos-laborales/{dato_laboral_id}/',
            path: {
                'dato_laboral_id': datoLaboralId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Datos Laborales de Empleados.
     * @param datoLaboralId Un valor de entero único que identifique este datos laborales.
     * @param requestBody
     * @returns DatosLaborales
     * @throws ApiError
     */
    public static legacyDatosLaboralesUpdate(
        datoLaboralId: number,
        requestBody: DatosLaboralesRequest,
    ): CancelablePromise<DatosLaborales> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/legacy/datos-laborales/{dato_laboral_id}/',
            path: {
                'dato_laboral_id': datoLaboralId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Historial de Ubicaciones (Departamentos/Cargos) de Empleados.
     * @param requestBody
     * @returns HistorialUbicaciones
     * @throws ApiError
     */
    public static legacyUbicacionesCreate(
        requestBody: HistorialUbicacionesRequest,
    ): CancelablePromise<HistorialUbicaciones> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/legacy/ubicaciones/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Historial de Ubicaciones (Departamentos/Cargos) de Empleados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @returns PaginatedHistorialUbicacionesList
     * @throws ApiError
     */
    public static legacyUbicacionesList(
        page?: number,
        pageSize?: number,
    ): CancelablePromise<PaginatedHistorialUbicacionesList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/ubicaciones/',
            query: {
                'page': page,
                'page_size': pageSize,
            },
        });
    }
    /**
     * Historial de Ubicaciones (Departamentos/Cargos) de Empleados.
     * @param ubicacionId
     * @returns void
     * @throws ApiError
     */
    public static legacyUbicacionesDestroy(
        ubicacionId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/legacy/ubicaciones/{ubicacion_id}/',
            path: {
                'ubicacion_id': ubicacionId,
            },
        });
    }
    /**
     * Historial de Ubicaciones (Departamentos/Cargos) de Empleados.
     * @param ubicacionId
     * @returns HistorialUbicaciones
     * @throws ApiError
     */
    public static legacyUbicacionesRetrieve(
        ubicacionId: number,
    ): CancelablePromise<HistorialUbicaciones> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/ubicaciones/{ubicacion_id}/',
            path: {
                'ubicacion_id': ubicacionId,
            },
        });
    }
    /**
     * Historial de Ubicaciones (Departamentos/Cargos) de Empleados.
     * @param ubicacionId
     * @param requestBody
     * @returns HistorialUbicaciones
     * @throws ApiError
     */
    public static legacyUbicacionesPartialUpdate(
        ubicacionId: number,
        requestBody?: PatchedHistorialUbicacionesRequest,
    ): CancelablePromise<HistorialUbicaciones> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/legacy/ubicaciones/{ubicacion_id}/',
            path: {
                'ubicacion_id': ubicacionId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Historial de Ubicaciones (Departamentos/Cargos) de Empleados.
     * @param ubicacionId
     * @param requestBody
     * @returns HistorialUbicaciones
     * @throws ApiError
     */
    public static legacyUbicacionesUpdate(
        ubicacionId: number,
        requestBody: HistorialUbicacionesRequest,
    ): CancelablePromise<HistorialUbicaciones> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/legacy/ubicaciones/{ubicacion_id}/',
            path: {
                'ubicacion_id': ubicacionId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Usuarios del Sistema.
     *
     * Usuarios con autenticación y roles de acceso.
     * Cada usuario se asocia a un empleado y puede tener múltiples roles.
     * @param requestBody
     * @returns UsuarioDetail
     * @throws ApiError
     */
    public static legacyUsuariosCreate(
        requestBody: UsuarioDetailRequest,
    ): CancelablePromise<UsuarioDetail> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/legacy/usuarios/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Usuarios del Sistema.
     *
     * Usuarios con autenticación y roles de acceso.
     * Cada usuario se asocia a un empleado y puede tener múltiples roles.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @returns PaginatedUsuarioListList
     * @throws ApiError
     */
    public static legacyUsuariosList(
        page?: number,
        pageSize?: number,
    ): CancelablePromise<PaginatedUsuarioListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/usuarios/',
            query: {
                'page': page,
                'page_size': pageSize,
            },
        });
    }
    /**
     * Gestión de Usuarios del Sistema.
     *
     * Usuarios con autenticación y roles de acceso.
     * Cada usuario se asocia a un empleado y puede tener múltiples roles.
     * @param usuarioId Un valor de entero único que identifique este usuario.
     * @returns void
     * @throws ApiError
     */
    public static legacyUsuariosDestroy(
        usuarioId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/legacy/usuarios/{usuario_id}/',
            path: {
                'usuario_id': usuarioId,
            },
        });
    }
    /**
     * Gestión de Usuarios del Sistema.
     *
     * Usuarios con autenticación y roles de acceso.
     * Cada usuario se asocia a un empleado y puede tener múltiples roles.
     * @param usuarioId Un valor de entero único que identifique este usuario.
     * @returns UsuarioDetail
     * @throws ApiError
     */
    public static legacyUsuariosRetrieve(
        usuarioId: number,
    ): CancelablePromise<UsuarioDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/usuarios/{usuario_id}/',
            path: {
                'usuario_id': usuarioId,
            },
        });
    }
    /**
     * Gestión de Usuarios del Sistema.
     *
     * Usuarios con autenticación y roles de acceso.
     * Cada usuario se asocia a un empleado y puede tener múltiples roles.
     * @param usuarioId Un valor de entero único que identifique este usuario.
     * @param requestBody
     * @returns UsuarioDetail
     * @throws ApiError
     */
    public static legacyUsuariosPartialUpdate(
        usuarioId: number,
        requestBody?: PatchedUsuarioDetailRequest,
    ): CancelablePromise<UsuarioDetail> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/legacy/usuarios/{usuario_id}/',
            path: {
                'usuario_id': usuarioId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Usuarios del Sistema.
     *
     * Usuarios con autenticación y roles de acceso.
     * Cada usuario se asocia a un empleado y puede tener múltiples roles.
     * @param usuarioId Un valor de entero único que identifique este usuario.
     * @param requestBody
     * @returns UsuarioDetail
     * @throws ApiError
     */
    public static legacyUsuariosUpdate(
        usuarioId: number,
        requestBody: UsuarioDetailRequest,
    ): CancelablePromise<UsuarioDetail> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/legacy/usuarios/{usuario_id}/',
            path: {
                'usuario_id': usuarioId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Roles (RBAC).
     *
     * Roles control de acceso basado en roles.
     * Cada rol contiene múltiples permisos.
     * @param requestBody
     * @returns RolDetail
     * @throws ApiError
     */
    public static legacyRolesCreate(
        requestBody: RolDetailRequest,
    ): CancelablePromise<RolDetail> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/legacy/roles/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Roles (RBAC).
     *
     * Roles control de acceso basado en roles.
     * Cada rol contiene múltiples permisos.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @returns PaginatedRolListList
     * @throws ApiError
     */
    public static legacyRolesList(
        page?: number,
        pageSize?: number,
    ): CancelablePromise<PaginatedRolListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/roles/',
            query: {
                'page': page,
                'page_size': pageSize,
            },
        });
    }
    /**
     * Gestión de Roles (RBAC).
     *
     * Roles control de acceso basado en roles.
     * Cada rol contiene múltiples permisos.
     * @param rolId Un valor de entero único que identifique este rol.
     * @returns void
     * @throws ApiError
     */
    public static legacyRolesDestroy(
        rolId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/legacy/roles/{rol_id}/',
            path: {
                'rol_id': rolId,
            },
        });
    }
    /**
     * Gestión de Roles (RBAC).
     *
     * Roles control de acceso basado en roles.
     * Cada rol contiene múltiples permisos.
     * @param rolId Un valor de entero único que identifique este rol.
     * @returns RolDetail
     * @throws ApiError
     */
    public static legacyRolesRetrieve(
        rolId: number,
    ): CancelablePromise<RolDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/roles/{rol_id}/',
            path: {
                'rol_id': rolId,
            },
        });
    }
    /**
     * Gestión de Roles (RBAC).
     *
     * Roles control de acceso basado en roles.
     * Cada rol contiene múltiples permisos.
     * @param rolId Un valor de entero único que identifique este rol.
     * @param requestBody
     * @returns RolDetail
     * @throws ApiError
     */
    public static legacyRolesPartialUpdate(
        rolId: number,
        requestBody?: PatchedRolDetailRequest,
    ): CancelablePromise<RolDetail> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/legacy/roles/{rol_id}/',
            path: {
                'rol_id': rolId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Roles (RBAC).
     *
     * Roles control de acceso basado en roles.
     * Cada rol contiene múltiples permisos.
     * @param rolId Un valor de entero único que identifique este rol.
     * @param requestBody
     * @returns RolDetail
     * @throws ApiError
     */
    public static legacyRolesUpdate(
        rolId: number,
        requestBody: RolDetailRequest,
    ): CancelablePromise<RolDetail> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/legacy/roles/{rol_id}/',
            path: {
                'rol_id': rolId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Permisos.
     *
     * Permisos del sistema organizados por módulo.
     * Utiliza módulos estáticos configurados en config.modules_config.
     * @param requestBody
     * @returns PermisoDetail
     * @throws ApiError
     */
    public static legacyPermisosCreate(
        requestBody: PermisoDetailRequest,
    ): CancelablePromise<PermisoDetail> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/legacy/permisos/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Permisos.
     *
     * Permisos del sistema organizados por módulo.
     * Utiliza módulos estáticos configurados en config.modules_config.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @returns PaginatedPermisoListList
     * @throws ApiError
     */
    public static legacyPermisosList(
        page?: number,
        pageSize?: number,
    ): CancelablePromise<PaginatedPermisoListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/permisos/',
            query: {
                'page': page,
                'page_size': pageSize,
            },
        });
    }
    /**
     * Gestión de Permisos.
     *
     * Permisos del sistema organizados por módulo.
     * Utiliza módulos estáticos configurados en config.modules_config.
     * @param permisoId Un valor de entero único que identifique este permiso.
     * @returns void
     * @throws ApiError
     */
    public static legacyPermisosDestroy(
        permisoId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/legacy/permisos/{permiso_id}/',
            path: {
                'permiso_id': permisoId,
            },
        });
    }
    /**
     * Gestión de Permisos.
     *
     * Permisos del sistema organizados por módulo.
     * Utiliza módulos estáticos configurados en config.modules_config.
     * @param permisoId Un valor de entero único que identifique este permiso.
     * @returns PermisoDetail
     * @throws ApiError
     */
    public static legacyPermisosRetrieve(
        permisoId: number,
    ): CancelablePromise<PermisoDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/permisos/{permiso_id}/',
            path: {
                'permiso_id': permisoId,
            },
        });
    }
    /**
     * Gestión de Permisos.
     *
     * Permisos del sistema organizados por módulo.
     * Utiliza módulos estáticos configurados en config.modules_config.
     * @param permisoId Un valor de entero único que identifique este permiso.
     * @param requestBody
     * @returns PermisoDetail
     * @throws ApiError
     */
    public static legacyPermisosPartialUpdate(
        permisoId: number,
        requestBody?: PatchedPermisoDetailRequest,
    ): CancelablePromise<PermisoDetail> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/legacy/permisos/{permiso_id}/',
            path: {
                'permiso_id': permisoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gestión de Permisos.
     *
     * Permisos del sistema organizados por módulo.
     * Utiliza módulos estáticos configurados en config.modules_config.
     * @param permisoId Un valor de entero único que identifique este permiso.
     * @param requestBody
     * @returns PermisoDetail
     * @throws ApiError
     */
    public static legacyPermisosUpdate(
        permisoId: number,
        requestBody: PermisoDetailRequest,
    ): CancelablePromise<PermisoDetail> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/legacy/permisos/{permiso_id}/',
            path: {
                'permiso_id': permisoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Asignación de Permisos a Roles.
     *
     * Gestiona la relación muchos-a-muchos entre Roles y Permisos.
     * Permite filtrar por rol específico.
     * @param requestBody
     * @returns RolPermisos
     * @throws ApiError
     */
    public static legacyRolPermisosCreate(
        requestBody: RolPermisosRequest,
    ): CancelablePromise<RolPermisos> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/legacy/rol-permisos/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Asignación de Permisos a Roles.
     *
     * Gestiona la relación muchos-a-muchos entre Roles y Permisos.
     * Permite filtrar por rol específico.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param permiso
     * @param rol
     * @returns PaginatedRolPermisosDetailList
     * @throws ApiError
     */
    public static legacyRolPermisosList(
        page?: number,
        pageSize?: number,
        permiso?: number,
        rol?: number,
    ): CancelablePromise<PaginatedRolPermisosDetailList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/rol-permisos/',
            query: {
                'page': page,
                'page_size': pageSize,
                'permiso': permiso,
                'rol': rol,
            },
        });
    }
    /**
     * Asignación de Permisos a Roles.
     *
     * Gestiona la relación muchos-a-muchos entre Roles y Permisos.
     * Permite filtrar por rol específico.
     * @param rolPermisoId Un valor de entero único que identifique este rol permisos.
     * @returns void
     * @throws ApiError
     */
    public static legacyRolPermisosDestroy(
        rolPermisoId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/legacy/rol-permisos/{rol_permiso_id}/',
            path: {
                'rol_permiso_id': rolPermisoId,
            },
        });
    }
    /**
     * Asignación de Permisos a Roles.
     *
     * Gestiona la relación muchos-a-muchos entre Roles y Permisos.
     * Permite filtrar por rol específico.
     * @param rolPermisoId Un valor de entero único que identifique este rol permisos.
     * @returns RolPermisosDetail
     * @throws ApiError
     */
    public static legacyRolPermisosRetrieve(
        rolPermisoId: number,
    ): CancelablePromise<RolPermisosDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/legacy/rol-permisos/{rol_permiso_id}/',
            path: {
                'rol_permiso_id': rolPermisoId,
            },
        });
    }
    /**
     * Asignación de Permisos a Roles.
     *
     * Gestiona la relación muchos-a-muchos entre Roles y Permisos.
     * Permite filtrar por rol específico.
     * @param rolPermisoId Un valor de entero único que identifique este rol permisos.
     * @param requestBody
     * @returns RolPermisos
     * @throws ApiError
     */
    public static legacyRolPermisosPartialUpdate(
        rolPermisoId: number,
        requestBody?: PatchedRolPermisosRequest,
    ): CancelablePromise<RolPermisos> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/legacy/rol-permisos/{rol_permiso_id}/',
            path: {
                'rol_permiso_id': rolPermisoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Asignación de Permisos a Roles.
     *
     * Gestiona la relación muchos-a-muchos entre Roles y Permisos.
     * Permite filtrar por rol específico.
     * @param rolPermisoId Un valor de entero único que identifique este rol permisos.
     * @param requestBody
     * @returns RolPermisos
     * @throws ApiError
     */
    public static legacyRolPermisosUpdate(
        rolPermisoId: number,
        requestBody: RolPermisosRequest,
    ): CancelablePromise<RolPermisos> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/legacy/rol-permisos/{rol_permiso_id}/',
            path: {
                'rol_permiso_id': rolPermisoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static legacyLoginCreate(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/legacy/login/',
        });
    }
    /**
     * Takes a refresh type JSON web token and returns an access type JSON web
     * token if the refresh token is valid.
     * @param requestBody
     * @returns TokenRefresh
     * @throws ApiError
     */
    public static legacyTokenRefreshCreate(
        requestBody: TokenRefreshRequest,
    ): CancelablePromise<TokenRefresh> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/legacy/token/refresh/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
