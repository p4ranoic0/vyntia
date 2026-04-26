/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Area } from '../models/Area';
import type { ContratosAdendas } from '../models/ContratosAdendas';
import type { ContratosAdendasCreate } from '../models/ContratosAdendasCreate';
import type { ContratosAdendasCreateRequest } from '../models/ContratosAdendasCreateRequest';
import type { ContratosAdendasRequest } from '../models/ContratosAdendasRequest';
import type { ContratosAdendasUpdate } from '../models/ContratosAdendasUpdate';
import type { ContratosAdendasUpdateRequest } from '../models/ContratosAdendasUpdateRequest';
import type { DatosAcademicos } from '../models/DatosAcademicos';
import type { DatosAcademicosRequest } from '../models/DatosAcademicosRequest';
import type { DatosFamiliares } from '../models/DatosFamiliares';
import type { DatosFamiliaresRequest } from '../models/DatosFamiliaresRequest';
import type { DatosLaborales } from '../models/DatosLaborales';
import type { DatosLaboralesRequest } from '../models/DatosLaboralesRequest';
import type { DocumentosDigitales } from '../models/DocumentosDigitales';
import type { DocumentosDigitalesRequest } from '../models/DocumentosDigitalesRequest';
import type { Empleado } from '../models/Empleado';
import type { EmpleadoRequest } from '../models/EmpleadoRequest';
import type { Modulos } from '../models/Modulos';
import type { OnboardingEmpleado } from '../models/OnboardingEmpleado';
import type { OnboardingEmpleadoRequest } from '../models/OnboardingEmpleadoRequest';
import type { OnboardingValidacion } from '../models/OnboardingValidacion';
import type { OnboardingValidacionRequest } from '../models/OnboardingValidacionRequest';
import type { PaginatedContratosAdendasListList } from '../models/PaginatedContratosAdendasListList';
import type { PaginatedDatosAcademicosList } from '../models/PaginatedDatosAcademicosList';
import type { PaginatedDatosFamiliaresList } from '../models/PaginatedDatosFamiliaresList';
import type { PaginatedDatosLaboralesList } from '../models/PaginatedDatosLaboralesList';
import type { PaginatedPermisoList } from '../models/PaginatedPermisoList';
import type { PaginatedRolList } from '../models/PaginatedRolList';
import type { PaginatedUsuarioList } from '../models/PaginatedUsuarioList';
import type { PaginatedUsuarioRolesListList } from '../models/PaginatedUsuarioRolesListList';
import type { PatchedContratosAdendasUpdateRequest } from '../models/PatchedContratosAdendasUpdateRequest';
import type { PatchedDatosAcademicosRequest } from '../models/PatchedDatosAcademicosRequest';
import type { PatchedDatosFamiliaresRequest } from '../models/PatchedDatosFamiliaresRequest';
import type { PatchedDatosLaboralesRequest } from '../models/PatchedDatosLaboralesRequest';
import type { PatchedOnboardingEmpleadoRequest } from '../models/PatchedOnboardingEmpleadoRequest';
import type { PatchedPermisoRequest } from '../models/PatchedPermisoRequest';
import type { PatchedRolRequest } from '../models/PatchedRolRequest';
import type { PatchedUsuarioRequest } from '../models/PatchedUsuarioRequest';
import type { PatchedUsuarioRolesRequest } from '../models/PatchedUsuarioRolesRequest';
import type { Permiso } from '../models/Permiso';
import type { PermisoRequest } from '../models/PermisoRequest';
import type { Rol } from '../models/Rol';
import type { RolPermisos } from '../models/RolPermisos';
import type { RolRequest } from '../models/RolRequest';
import type { Usuario } from '../models/Usuario';
import type { UsuarioCreate } from '../models/UsuarioCreate';
import type { UsuarioCreateRequest } from '../models/UsuarioCreateRequest';
import type { UsuarioRequest } from '../models/UsuarioRequest';
import type { UsuarioRoles } from '../models/UsuarioRoles';
import type { UsuarioRolesCreate } from '../models/UsuarioRolesCreate';
import type { UsuarioRolesCreateRequest } from '../models/UsuarioRolesCreateRequest';
import type { UsuarioRolesRequest } from '../models/UsuarioRolesRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class RrhhService {
    /**
     * Get only active areas.
     * @returns Area
     * @throws ApiError
     */
    public static rrhhAreasActivasRetrieve(): CancelablePromise<Area> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/areas/activas/',
        });
    }
    /**
     * Get only active employees.
     * @returns Empleado
     * @throws ApiError
     */
    public static rrhhEmpleadosActivosRetrieve(): CancelablePromise<Empleado> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/empleados/activos/',
        });
    }
    /**
     * Get employee statistics.
     * @returns Empleado
     * @throws ApiError
     */
    public static rrhhEmpleadosEstadisticasRetrieve(): CancelablePromise<Empleado> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/empleados/estadisticas/',
        });
    }
    /**
     * Get complete employee data including family and academic info.
     * @param empleadoId Un valor de entero único que identifique este empleado.
     * @returns Empleado
     * @throws ApiError
     */
    public static rrhhEmpleadosDatosCompletosRetrieve(
        empleadoId: number,
    ): CancelablePromise<Empleado> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/empleados/{empleado_id}/datos_completos/',
            path: {
                'empleado_id': empleadoId,
            },
        });
    }
    /**
     * Genera y devuelve el reporte integral del empleado en PDF.
     * @param empleadoId Un valor de entero único que identifique este empleado.
     * @returns Empleado
     * @throws ApiError
     */
    public static rrhhEmpleadosReporteIntegralRetrieve(
        empleadoId: number,
    ): CancelablePromise<Empleado> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/empleados/{empleado_id}/reporte_integral/',
            path: {
                'empleado_id': empleadoId,
            },
        });
    }
    /**
     * Genera un reporte PDF de una seccion del empleado.
     * @param empleadoId Un valor de entero único que identifique este empleado.
     * @returns Empleado
     * @throws ApiError
     */
    public static rrhhEmpleadosReporteSeccionRetrieve(
        empleadoId: number,
    ): CancelablePromise<Empleado> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/empleados/{empleado_id}/reporte_seccion/',
            path: {
                'empleado_id': empleadoId,
            },
        });
    }
    /**
     * Transfer employee to another area.
     * @param empleadoId Un valor de entero único que identifique este empleado.
     * @param requestBody
     * @returns Empleado
     * @throws ApiError
     */
    public static rrhhEmpleadosTransferirCreate(
        empleadoId: number,
        requestBody: EmpleadoRequest,
    ): CancelablePromise<Empleado> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/empleados/{empleado_id}/transferir/',
            path: {
                'empleado_id': empleadoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Crear datos familiares - requiere rol RRHH.
     * @param requestBody
     * @returns DatosFamiliares
     * @throws ApiError
     */
    public static rrhhDatosFamiliaresCreate(
        requestBody: DatosFamiliaresRequest,
    ): CancelablePromise<DatosFamiliares> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/datos-familiares/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar datos familiares - requiere autenticación.
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @returns PaginatedDatosFamiliaresList
     * @throws ApiError
     */
    public static rrhhDatosFamiliaresList(
        ordering?: string,
        page?: number,
        pageSize?: number,
        search?: string,
    ): CancelablePromise<PaginatedDatosFamiliaresList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/datos-familiares/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }
    /**
     * Eliminar datos familiares - requiere rol administrador.
     * @param familiarId Un valor de entero único que identifique este datos familiares.
     * @returns void
     * @throws ApiError
     */
    public static rrhhDatosFamiliaresDestroy(
        familiarId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/datos-familiares/{familiar_id}/',
            path: {
                'familiar_id': familiarId,
            },
        });
    }
    /**
     * Obtener datos familiares específicos - requiere autenticación.
     * @param familiarId Un valor de entero único que identifique este datos familiares.
     * @returns DatosFamiliares
     * @throws ApiError
     */
    public static rrhhDatosFamiliaresRetrieve(
        familiarId: number,
    ): CancelablePromise<DatosFamiliares> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/datos-familiares/{familiar_id}/',
            path: {
                'familiar_id': familiarId,
            },
        });
    }
    /**
     * Actualizar datos familiares parcialmente - requiere rol RRHH.
     * @param familiarId Un valor de entero único que identifique este datos familiares.
     * @param requestBody
     * @returns DatosFamiliares
     * @throws ApiError
     */
    public static rrhhDatosFamiliaresPartialUpdate(
        familiarId: number,
        requestBody?: PatchedDatosFamiliaresRequest,
    ): CancelablePromise<DatosFamiliares> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/rrhh/datos-familiares/{familiar_id}/',
            path: {
                'familiar_id': familiarId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Actualizar datos familiares - requiere rol RRHH.
     * @param familiarId Un valor de entero único que identifique este datos familiares.
     * @param requestBody
     * @returns DatosFamiliares
     * @throws ApiError
     */
    public static rrhhDatosFamiliaresUpdate(
        familiarId: number,
        requestBody: DatosFamiliaresRequest,
    ): CancelablePromise<DatosFamiliares> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/rrhh/datos-familiares/{familiar_id}/',
            path: {
                'familiar_id': familiarId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Crear datos académicos - requiere rol RRHH.
     * @param requestBody
     * @returns DatosAcademicos
     * @throws ApiError
     */
    public static rrhhDatosAcademicosCreate(
        requestBody: DatosAcademicosRequest,
    ): CancelablePromise<DatosAcademicos> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/datos-academicos/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar datos académicos - requiere autenticación.
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @returns PaginatedDatosAcademicosList
     * @throws ApiError
     */
    public static rrhhDatosAcademicosList(
        ordering?: string,
        page?: number,
        pageSize?: number,
        search?: string,
    ): CancelablePromise<PaginatedDatosAcademicosList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/datos-academicos/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }
    /**
     * Eliminar datos académicos - requiere rol administrador.
     * @param academicoId Un valor de entero único que identifique este datos academicos.
     * @returns void
     * @throws ApiError
     */
    public static rrhhDatosAcademicosDestroy(
        academicoId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/datos-academicos/{academico_id}/',
            path: {
                'academico_id': academicoId,
            },
        });
    }
    /**
     * Obtener datos académicos específicos - requiere autenticación.
     * @param academicoId Un valor de entero único que identifique este datos academicos.
     * @returns DatosAcademicos
     * @throws ApiError
     */
    public static rrhhDatosAcademicosRetrieve(
        academicoId: number,
    ): CancelablePromise<DatosAcademicos> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/datos-academicos/{academico_id}/',
            path: {
                'academico_id': academicoId,
            },
        });
    }
    /**
     * Actualizar datos académicos parcialmente - requiere rol RRHH.
     * @param academicoId Un valor de entero único que identifique este datos academicos.
     * @param requestBody
     * @returns DatosAcademicos
     * @throws ApiError
     */
    public static rrhhDatosAcademicosPartialUpdate(
        academicoId: number,
        requestBody?: PatchedDatosAcademicosRequest,
    ): CancelablePromise<DatosAcademicos> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/rrhh/datos-academicos/{academico_id}/',
            path: {
                'academico_id': academicoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Actualizar datos académicos - requiere rol RRHH.
     * @param academicoId Un valor de entero único que identifique este datos academicos.
     * @param requestBody
     * @returns DatosAcademicos
     * @throws ApiError
     */
    public static rrhhDatosAcademicosUpdate(
        academicoId: number,
        requestBody: DatosAcademicosRequest,
    ): CancelablePromise<DatosAcademicos> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/rrhh/datos-academicos/{academico_id}/',
            path: {
                'academico_id': academicoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Crear datos laborales - requiere rol RRHH.
     * @param requestBody
     * @returns DatosLaborales
     * @throws ApiError
     */
    public static rrhhDatosLaboralesCreate(
        requestBody: DatosLaboralesRequest,
    ): CancelablePromise<DatosLaborales> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/datos-laborales/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar datos laborales - requiere autenticación.
     * @param antiguedadMaxAOs
     * @param antiguedadMinAOs
     * @param categoria
     * @param condicion
     * @param estado
     * @param fechaCeseDesde
     * @param fechaCeseHasta
     * @param fechaIngresoDesde
     * @param fechaIngresoHasta
     * @param grupoOcupacional
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param puesto
     * @param regLaboral
     * @param remuneracionMax
     * @param remuneracionMin
     * @param search Un término de búsqueda.
     * @returns PaginatedDatosLaboralesList
     * @throws ApiError
     */
    public static rrhhDatosLaboralesList(
        antiguedadMaxAOs?: number,
        antiguedadMinAOs?: number,
        categoria?: string,
        condicion?: string,
        estado?: boolean,
        fechaCeseDesde?: string,
        fechaCeseHasta?: string,
        fechaIngresoDesde?: string,
        fechaIngresoHasta?: string,
        grupoOcupacional?: string,
        ordering?: string,
        page?: number,
        pageSize?: number,
        puesto?: string,
        regLaboral?: string,
        remuneracionMax?: number,
        remuneracionMin?: number,
        search?: string,
    ): CancelablePromise<PaginatedDatosLaboralesList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/datos-laborales/',
            query: {
                'antiguedad_max_años': antiguedadMaxAOs,
                'antiguedad_min_años': antiguedadMinAOs,
                'categoria': categoria,
                'condicion': condicion,
                'estado': estado,
                'fecha_cese_desde': fechaCeseDesde,
                'fecha_cese_hasta': fechaCeseHasta,
                'fecha_ingreso_desde': fechaIngresoDesde,
                'fecha_ingreso_hasta': fechaIngresoHasta,
                'grupo_ocupacional': grupoOcupacional,
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'puesto': puesto,
                'reg_laboral': regLaboral,
                'remuneracion_max': remuneracionMax,
                'remuneracion_min': remuneracionMin,
                'search': search,
            },
        });
    }
    /**
     * Get salary statistics.
     * @returns DatosLaborales
     * @throws ApiError
     */
    public static rrhhDatosLaboralesEstadisticasRemuneracionRetrieve(): CancelablePromise<DatosLaborales> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/datos-laborales/estadisticas_remuneracion/',
        });
    }
    /**
     * Eliminar datos laborales - requiere rol administrador.
     * @param datoLaboralId Un valor de entero único que identifique este datos laborales.
     * @returns void
     * @throws ApiError
     */
    public static rrhhDatosLaboralesDestroy(
        datoLaboralId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/datos-laborales/{dato_laboral_id}/',
            path: {
                'dato_laboral_id': datoLaboralId,
            },
        });
    }
    /**
     * Obtener datos laborales específicos - requiere autenticación.
     * @param datoLaboralId Un valor de entero único que identifique este datos laborales.
     * @returns DatosLaborales
     * @throws ApiError
     */
    public static rrhhDatosLaboralesRetrieve(
        datoLaboralId: number,
    ): CancelablePromise<DatosLaborales> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/datos-laborales/{dato_laboral_id}/',
            path: {
                'dato_laboral_id': datoLaboralId,
            },
        });
    }
    /**
     * Actualizar datos laborales parcialmente - requiere rol RRHH.
     * @param datoLaboralId Un valor de entero único que identifique este datos laborales.
     * @param requestBody
     * @returns DatosLaborales
     * @throws ApiError
     */
    public static rrhhDatosLaboralesPartialUpdate(
        datoLaboralId: number,
        requestBody?: PatchedDatosLaboralesRequest,
    ): CancelablePromise<DatosLaborales> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/rrhh/datos-laborales/{dato_laboral_id}/',
            path: {
                'dato_laboral_id': datoLaboralId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Actualizar datos laborales - requiere rol RRHH.
     * @param datoLaboralId Un valor de entero único que identifique este datos laborales.
     * @param requestBody
     * @returns DatosLaborales
     * @throws ApiError
     */
    public static rrhhDatosLaboralesUpdate(
        datoLaboralId: number,
        requestBody: DatosLaboralesRequest,
    ): CancelablePromise<DatosLaborales> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/rrhh/datos-laborales/{dato_laboral_id}/',
            path: {
                'dato_laboral_id': datoLaboralId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Get pay slips (boletas de pago) - replaces old Boleta endpoint.
     * @returns DocumentosDigitales
     * @throws ApiError
     */
    public static rrhhDocumentosDigitalesBoletasPagoRetrieve(): CancelablePromise<DocumentosDigitales> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/documentos-digitales/boletas_pago/',
        });
    }
    /**
     * Get documents grouped by type.
     * @returns DocumentosDigitales
     * @throws ApiError
     */
    public static rrhhDocumentosDigitalesPorTipoRetrieve(): CancelablePromise<DocumentosDigitales> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/documentos-digitales/por_tipo/',
        });
    }
    /**
     * Get documents that will expire soon.
     * @returns DocumentosDigitales
     * @throws ApiError
     */
    public static rrhhDocumentosDigitalesProximosVencerRetrieve(): CancelablePromise<DocumentosDigitales> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/documentos-digitales/proximos_vencer/',
        });
    }
    /**
     * Subir documento institucional al legajo de un empleado.
     *
     * Permite a RRHH subir boletas, constancias, resoluciones, etc.
     * Acepta un archivo o multiples archivos para subida masiva.
     * @param requestBody
     * @returns DocumentosDigitales
     * @throws ApiError
     */
    public static rrhhDocumentosDigitalesSubirInstitucionalCreate(
        requestBody: DocumentosDigitalesRequest,
    ): CancelablePromise<DocumentosDigitales> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/documentos-digitales/subir_institucional/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Rechazar un documento - requiere rol RRHH.
     * @param documentoId Un valor de entero único que identifique este documentos digitales.
     * @param requestBody
     * @returns DocumentosDigitales
     * @throws ApiError
     */
    public static rrhhDocumentosDigitalesRechazarCreate(
        documentoId: number,
        requestBody: DocumentosDigitalesRequest,
    ): CancelablePromise<DocumentosDigitales> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/documentos-digitales/{documento_id}/rechazar/',
            path: {
                'documento_id': documentoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Validar un documento - requiere rol RRHH.
     * @param documentoId Un valor de entero único que identifique este documentos digitales.
     * @param requestBody
     * @returns DocumentosDigitales
     * @throws ApiError
     */
    public static rrhhDocumentosDigitalesValidarCreate(
        documentoId: number,
        requestBody: DocumentosDigitalesRequest,
    ): CancelablePromise<DocumentosDigitales> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/documentos-digitales/{documento_id}/validar/',
            path: {
                'documento_id': documentoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Crear contrato o adenda - requiere rol RRHH.
     * @param requestBody
     * @returns ContratosAdendasCreate
     * @throws ApiError
     */
    public static rrhhContratosAdendasCreate(
        requestBody: ContratosAdendasCreateRequest,
    ): CancelablePromise<ContratosAdendasCreate> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/contratos-adendas/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar contratos y adendas - requiere autenticación.
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @returns PaginatedContratosAdendasListList
     * @throws ApiError
     */
    public static rrhhContratosAdendasList(
        ordering?: string,
        page?: number,
        pageSize?: number,
        search?: string,
    ): CancelablePromise<PaginatedContratosAdendasListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/contratos-adendas/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }
    /**
     * Obtiene contratos próximos a vencer.
     * @returns ContratosAdendas
     * @throws ApiError
     */
    public static rrhhContratosAdendasAlertasVencimientoRetrieve(): CancelablePromise<ContratosAdendas> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/contratos-adendas/alertas_vencimiento/',
        });
    }
    /**
     * Obtiene estadísticas generales del sistema de contratos.
     * @returns ContratosAdendas
     * @throws ApiError
     */
    public static rrhhContratosAdendasEstadisticasRetrieve(): CancelablePromise<ContratosAdendas> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/contratos-adendas/estadisticas/',
        });
    }
    /**
     * Genera reporte estadístico de contratos.
     * @returns ContratosAdendas
     * @throws ApiError
     */
    public static rrhhContratosAdendasReporteContratosRetrieve(): CancelablePromise<ContratosAdendas> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/contratos-adendas/reporte_contratos/',
        });
    }
    /**
     * Eliminar contrato o adenda - requiere rol administrador.
     * @param contratoId Un valor de entero único que identifique este Contrato/Adenda.
     * @returns void
     * @throws ApiError
     */
    public static rrhhContratosAdendasDestroy(
        contratoId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/contratos-adendas/{contrato_id}/',
            path: {
                'contrato_id': contratoId,
            },
        });
    }
    /**
     * Obtener contrato específico - requiere autenticación.
     * @param contratoId Un valor de entero único que identifique este Contrato/Adenda.
     * @returns ContratosAdendas
     * @throws ApiError
     */
    public static rrhhContratosAdendasRetrieve(
        contratoId: number,
    ): CancelablePromise<ContratosAdendas> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/contratos-adendas/{contrato_id}/',
            path: {
                'contrato_id': contratoId,
            },
        });
    }
    /**
     * Actualizar contrato parcialmente - requiere rol RRHH.
     * @param contratoId Un valor de entero único que identifique este Contrato/Adenda.
     * @param requestBody
     * @returns ContratosAdendasUpdate
     * @throws ApiError
     */
    public static rrhhContratosAdendasPartialUpdate(
        contratoId: number,
        requestBody?: PatchedContratosAdendasUpdateRequest,
    ): CancelablePromise<ContratosAdendasUpdate> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/rrhh/contratos-adendas/{contrato_id}/',
            path: {
                'contrato_id': contratoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Actualizar contrato o adenda - requiere rol RRHH.
     * @param contratoId Un valor de entero único que identifique este Contrato/Adenda.
     * @param requestBody
     * @returns ContratosAdendasUpdate
     * @throws ApiError
     */
    public static rrhhContratosAdendasUpdate(
        contratoId: number,
        requestBody: ContratosAdendasUpdateRequest,
    ): CancelablePromise<ContratosAdendasUpdate> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/rrhh/contratos-adendas/{contrato_id}/',
            path: {
                'contrato_id': contratoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Renueva un contrato existente creando uno nuevo.
     * @param contratoId Un valor de entero único que identifique este Contrato/Adenda.
     * @param requestBody
     * @returns ContratosAdendas
     * @throws ApiError
     */
    public static rrhhContratosAdendasRenovarContratoCreate(
        contratoId: number,
        requestBody: ContratosAdendasRequest,
    ): CancelablePromise<ContratosAdendas> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/contratos-adendas/{contrato_id}/renovar_contrato/',
            path: {
                'contrato_id': contratoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Crear usuario - requiere rol administrador.
     * @param requestBody
     * @returns UsuarioCreate
     * @throws ApiError
     */
    public static rrhhUsuariosCreate(
        requestBody: UsuarioCreateRequest,
    ): CancelablePromise<UsuarioCreate> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/usuarios/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar usuarios - requiere rol administrador.
     * @param dateJoinedDesde
     * @param dateJoinedHasta
     * @param email
     * @param empleadoArea
     * @param empleadoDni
     * @param estado
     * @param fechaUltLoginDesde
     * @param fechaUltLoginHasta
     * @param firstName
     * @param isActive
     * @param lastName
     * @param loginRecienteDias
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param rol
     * @param search Un término de búsqueda.
     * @param sinLoginDias
     * @param tieneRoles
     * @param username
     * @returns PaginatedUsuarioList
     * @throws ApiError
     */
    public static rrhhUsuariosList(
        dateJoinedDesde?: string,
        dateJoinedHasta?: string,
        email?: string,
        empleadoArea?: number,
        empleadoDni?: string,
        estado?: boolean,
        fechaUltLoginDesde?: string,
        fechaUltLoginHasta?: string,
        firstName?: string,
        isActive?: boolean,
        lastName?: string,
        loginRecienteDias?: number,
        ordering?: string,
        page?: number,
        pageSize?: number,
        rol?: string,
        search?: string,
        sinLoginDias?: number,
        tieneRoles?: boolean,
        username?: string,
    ): CancelablePromise<PaginatedUsuarioList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/usuarios/',
            query: {
                'date_joined_desde': dateJoinedDesde,
                'date_joined_hasta': dateJoinedHasta,
                'email': email,
                'empleado_area': empleadoArea,
                'empleado_dni': empleadoDni,
                'estado': estado,
                'fecha_ult_login_desde': fechaUltLoginDesde,
                'fecha_ult_login_hasta': fechaUltLoginHasta,
                'first_name': firstName,
                'is_active': isActive,
                'last_name': lastName,
                'login_reciente_dias': loginRecienteDias,
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'rol': rol,
                'search': search,
                'sin_login_dias': sinLoginDias,
                'tiene_roles': tieneRoles,
                'username': username,
            },
        });
    }
    /**
     * Get users without recent login.
     * @returns Usuario
     * @throws ApiError
     */
    public static rrhhUsuariosSinLoginRecienteRetrieve(): CancelablePromise<Usuario> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/usuarios/sin_login_reciente/',
        });
    }
    /**
     * Eliminar usuario - requiere rol administrador.
     * @param usuarioId Un valor de entero único que identifique este usuario.
     * @returns void
     * @throws ApiError
     */
    public static rrhhUsuariosDestroy(
        usuarioId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/usuarios/{usuario_id}/',
            path: {
                'usuario_id': usuarioId,
            },
        });
    }
    /**
     * Obtener usuario específico - requiere rol administrador.
     * @param usuarioId Un valor de entero único que identifique este usuario.
     * @returns Usuario
     * @throws ApiError
     */
    public static rrhhUsuariosRetrieve(
        usuarioId: number,
    ): CancelablePromise<Usuario> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/usuarios/{usuario_id}/',
            path: {
                'usuario_id': usuarioId,
            },
        });
    }
    /**
     * Actualizar usuario parcialmente - requiere rol administrador.
     * @param usuarioId Un valor de entero único que identifique este usuario.
     * @param requestBody
     * @returns Usuario
     * @throws ApiError
     */
    public static rrhhUsuariosPartialUpdate(
        usuarioId: number,
        requestBody?: PatchedUsuarioRequest,
    ): CancelablePromise<Usuario> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/rrhh/usuarios/{usuario_id}/',
            path: {
                'usuario_id': usuarioId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Actualizar usuario - requiere rol administrador.
     * @param usuarioId Un valor de entero único que identifique este usuario.
     * @param requestBody
     * @returns Usuario
     * @throws ApiError
     */
    public static rrhhUsuariosUpdate(
        usuarioId: number,
        requestBody: UsuarioRequest,
    ): CancelablePromise<Usuario> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/rrhh/usuarios/{usuario_id}/',
            path: {
                'usuario_id': usuarioId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Asigna uno o múltiples roles a un usuario específico
     * @param usuarioId Un valor de entero único que identifique este usuario.
     * @param requestBody
     * @returns Usuario
     * @throws ApiError
     */
    public static rrhhUsuariosAsignarRolCreate(
        usuarioId: number,
        requestBody: UsuarioRequest,
    ): CancelablePromise<Usuario> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/usuarios/{usuario_id}/asignar_rol/',
            path: {
                'usuario_id': usuarioId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Remueve un rol de un usuario específico
     * @param usuarioId Un valor de entero único que identifique este usuario.
     * @param requestBody
     * @returns Usuario
     * @throws ApiError
     */
    public static rrhhUsuariosRemoverRolCreate(
        usuarioId: number,
        requestBody: UsuarioRequest,
    ): CancelablePromise<Usuario> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/usuarios/{usuario_id}/remover_rol/',
            path: {
                'usuario_id': usuarioId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Obtiene los roles asignados a un usuario específico
     * @param usuarioId Un valor de entero único que identifique este usuario.
     * @returns Usuario
     * @throws ApiError
     */
    public static rrhhUsuariosRolesRetrieve(
        usuarioId: number,
    ): CancelablePromise<Usuario> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/usuarios/{usuario_id}/roles/',
            path: {
                'usuario_id': usuarioId,
            },
        });
    }
    /**
     * Crear rol - requiere rol administrador.
     * @param requestBody
     * @returns Rol
     * @throws ApiError
     */
    public static rrhhRolesCreate(
        requestBody: RolRequest,
    ): CancelablePromise<Rol> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/roles/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar roles - requiere rol administrador.
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @returns PaginatedRolList
     * @throws ApiError
     */
    public static rrhhRolesList(
        ordering?: string,
        page?: number,
        pageSize?: number,
        search?: string,
    ): CancelablePromise<PaginatedRolList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/roles/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }
    /**
     * Get only active roles.
     * @returns Rol
     * @throws ApiError
     */
    public static rrhhRolesActivosRetrieve(): CancelablePromise<Rol> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/roles/activos/',
        });
    }
    /**
     * Eliminar rol - requiere rol administrador.
     * @param rolId Un valor de entero único que identifique este rol.
     * @returns void
     * @throws ApiError
     */
    public static rrhhRolesDestroy(
        rolId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/roles/{rol_id}/',
            path: {
                'rol_id': rolId,
            },
        });
    }
    /**
     * Obtener rol específico - requiere rol administrador.
     * @param rolId Un valor de entero único que identifique este rol.
     * @returns Rol
     * @throws ApiError
     */
    public static rrhhRolesRetrieve(
        rolId: number,
    ): CancelablePromise<Rol> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/roles/{rol_id}/',
            path: {
                'rol_id': rolId,
            },
        });
    }
    /**
     * Actualizar rol parcialmente - requiere rol administrador.
     * @param rolId Un valor de entero único que identifique este rol.
     * @param requestBody
     * @returns Rol
     * @throws ApiError
     */
    public static rrhhRolesPartialUpdate(
        rolId: number,
        requestBody?: PatchedRolRequest,
    ): CancelablePromise<Rol> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/rrhh/roles/{rol_id}/',
            path: {
                'rol_id': rolId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Actualizar rol - requiere rol administrador.
     * @param rolId Un valor de entero único que identifique este rol.
     * @param requestBody
     * @returns Rol
     * @throws ApiError
     */
    public static rrhhRolesUpdate(
        rolId: number,
        requestBody: RolRequest,
    ): CancelablePromise<Rol> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/rrhh/roles/{rol_id}/',
            path: {
                'rol_id': rolId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Crear permiso - requiere rol administrador.
     * @param requestBody
     * @returns Permiso
     * @throws ApiError
     */
    public static rrhhPermisosCreate(
        requestBody: PermisoRequest,
    ): CancelablePromise<Permiso> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/permisos/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar permisos - requiere rol administrador.
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @returns PaginatedPermisoList
     * @throws ApiError
     */
    public static rrhhPermisosList(
        ordering?: string,
        page?: number,
        pageSize?: number,
        search?: string,
    ): CancelablePromise<PaginatedPermisoList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/permisos/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }
    /**
     * Eliminar permiso - requiere rol administrador.
     * @param permisoId Un valor de entero único que identifique este permiso.
     * @returns void
     * @throws ApiError
     */
    public static rrhhPermisosDestroy(
        permisoId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/permisos/{permiso_id}/',
            path: {
                'permiso_id': permisoId,
            },
        });
    }
    /**
     * Obtener permiso específico - requiere rol administrador.
     * @param permisoId Un valor de entero único que identifique este permiso.
     * @returns Permiso
     * @throws ApiError
     */
    public static rrhhPermisosRetrieve(
        permisoId: number,
    ): CancelablePromise<Permiso> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/permisos/{permiso_id}/',
            path: {
                'permiso_id': permisoId,
            },
        });
    }
    /**
     * Actualizar permiso parcialmente - requiere rol administrador.
     * @param permisoId Un valor de entero único que identifique este permiso.
     * @param requestBody
     * @returns Permiso
     * @throws ApiError
     */
    public static rrhhPermisosPartialUpdate(
        permisoId: number,
        requestBody?: PatchedPermisoRequest,
    ): CancelablePromise<Permiso> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/rrhh/permisos/{permiso_id}/',
            path: {
                'permiso_id': permisoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Actualizar permiso - requiere rol administrador.
     * @param permisoId Un valor de entero único que identifique este permiso.
     * @param requestBody
     * @returns Permiso
     * @throws ApiError
     */
    public static rrhhPermisosUpdate(
        permisoId: number,
        requestBody: PermisoRequest,
    ): CancelablePromise<Permiso> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/rrhh/permisos/{permiso_id}/',
            path: {
                'permiso_id': permisoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Obtiene solo los módulos activos.
     * @returns Modulos
     * @throws ApiError
     */
    public static rrhhModulosActivosRetrieve(): CancelablePromise<Modulos> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/modulos/activos/',
        });
    }
    /**
     * Obtiene todos los roles que tienen un permiso específico.
     * @returns RolPermisos
     * @throws ApiError
     */
    public static rrhhRolPermisosPorPermisoRetrieve(): CancelablePromise<RolPermisos> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/rol-permisos/por_permiso/',
        });
    }
    /**
     * Obtiene todos los permisos asignados a un rol específico.
     * @returns RolPermisos
     * @throws ApiError
     */
    public static rrhhRolPermisosPorRolRetrieve(): CancelablePromise<RolPermisos> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/rol-permisos/por_rol/',
        });
    }
    /**
     * Crea una nueva asignación de rol a usuario - requiere rol administrador.
     * @param requestBody
     * @returns UsuarioRolesCreate
     * @throws ApiError
     */
    public static rrhhUsuarioRolesCreate(
        requestBody: UsuarioRolesCreateRequest,
    ): CancelablePromise<UsuarioRolesCreate> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/usuario-roles/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar asignaciones de roles - requiere rol administrador.
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @returns PaginatedUsuarioRolesListList
     * @throws ApiError
     */
    public static rrhhUsuarioRolesList(
        ordering?: string,
        page?: number,
        pageSize?: number,
        search?: string,
    ): CancelablePromise<PaginatedUsuarioRolesListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/usuario-roles/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }
    /**
     * Obtiene todas las asignaciones de roles activas
     * @returns UsuarioRoles
     * @throws ApiError
     */
    public static rrhhUsuarioRolesActivosRetrieve(): CancelablePromise<UsuarioRoles> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/usuario-roles/activos/',
        });
    }
    /**
     * Asigna múltiples roles a un usuario o un rol a múltiples usuarios
     * @param requestBody
     * @returns UsuarioRoles
     * @throws ApiError
     */
    public static rrhhUsuarioRolesAsignarMultipleCreate(
        requestBody: UsuarioRolesRequest,
    ): CancelablePromise<UsuarioRoles> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/usuario-roles/asignar_multiple/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Busca usuarios que tienen roles específicos asignados
     * Parámetros de consulta:
     * - rol_ids: Lista de IDs de roles separados por coma
     * - nombres: Filtro por nombres de usuario (búsqueda parcial)
     * - estado: Estado de la asignación (activo, inactivo, expirado)
     * - operador: 'AND' o 'OR' para múltiples roles (por defecto 'OR')
     * @returns UsuarioRoles
     * @throws ApiError
     */
    public static rrhhUsuarioRolesBuscarUsuariosPorRolesRetrieve(): CancelablePromise<UsuarioRoles> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/usuario-roles/buscar_usuarios_por_roles/',
        });
    }
    /**
     * Obtiene los usuarios que tienen un rol específico
     * @returns UsuarioRoles
     * @throws ApiError
     */
    public static rrhhUsuarioRolesPorRolRetrieve(): CancelablePromise<UsuarioRoles> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/usuario-roles/por_rol/',
        });
    }
    /**
     * Obtiene las asignaciones de roles para un usuario específico
     * @returns UsuarioRoles
     * @throws ApiError
     */
    public static rrhhUsuarioRolesPorUsuarioRetrieve(): CancelablePromise<UsuarioRoles> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/usuario-roles/por_usuario/',
        });
    }
    /**
     * Marca una asignación como inactiva en lugar de eliminarla - requiere rol administrador.
     * @param usuarioRolId Un valor de entero único que identifique este usuario roles.
     * @returns void
     * @throws ApiError
     */
    public static rrhhUsuarioRolesDestroy(
        usuarioRolId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/usuario-roles/{usuario_rol_id}/',
            path: {
                'usuario_rol_id': usuarioRolId,
            },
        });
    }
    /**
     * Obtener asignación específica - requiere rol administrador.
     * @param usuarioRolId Un valor de entero único que identifique este usuario roles.
     * @returns UsuarioRoles
     * @throws ApiError
     */
    public static rrhhUsuarioRolesRetrieve(
        usuarioRolId: number,
    ): CancelablePromise<UsuarioRoles> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/usuario-roles/{usuario_rol_id}/',
            path: {
                'usuario_rol_id': usuarioRolId,
            },
        });
    }
    /**
     * Actualizar asignación parcialmente - requiere rol administrador.
     * @param usuarioRolId Un valor de entero único que identifique este usuario roles.
     * @param requestBody
     * @returns UsuarioRoles
     * @throws ApiError
     */
    public static rrhhUsuarioRolesPartialUpdate(
        usuarioRolId: number,
        requestBody?: PatchedUsuarioRolesRequest,
    ): CancelablePromise<UsuarioRoles> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/rrhh/usuario-roles/{usuario_rol_id}/',
            path: {
                'usuario_rol_id': usuarioRolId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Actualizar asignación - requiere rol administrador.
     * @param usuarioRolId Un valor de entero único que identifique este usuario roles.
     * @param requestBody
     * @returns UsuarioRoles
     * @throws ApiError
     */
    public static rrhhUsuarioRolesUpdate(
        usuarioRolId: number,
        requestBody: UsuarioRolesRequest,
    ): CancelablePromise<UsuarioRoles> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/rrhh/usuario-roles/{usuario_rol_id}/',
            path: {
                'usuario_rol_id': usuarioRolId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Obtener el onboarding del usuario actual.
     * @returns OnboardingEmpleado
     * @throws ApiError
     */
    public static rrhhOnboardingMiOnboardingRetrieve(): CancelablePromise<OnboardingEmpleado> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/onboarding/mi_onboarding/',
        });
    }
    /**
     * ViewSet para gestionar el proceso de onboarding de nuevos empleados.
     * @param onboardingId Un valor de entero único que identifique este onboarding empleado.
     * @returns void
     * @throws ApiError
     */
    public static rrhhOnboardingDestroy(
        onboardingId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/onboarding/{onboarding_id}/',
            path: {
                'onboarding_id': onboardingId,
            },
        });
    }
    /**
     * ViewSet para gestionar el proceso de onboarding de nuevos empleados.
     * @param onboardingId Un valor de entero único que identifique este onboarding empleado.
     * @param requestBody
     * @returns OnboardingEmpleado
     * @throws ApiError
     */
    public static rrhhOnboardingPartialUpdate(
        onboardingId: number,
        requestBody?: PatchedOnboardingEmpleadoRequest,
    ): CancelablePromise<OnboardingEmpleado> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/rrhh/onboarding/{onboarding_id}/',
            path: {
                'onboarding_id': onboardingId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * ViewSet para gestionar el proceso de onboarding de nuevos empleados.
     * @param onboardingId Un valor de entero único que identifique este onboarding empleado.
     * @param requestBody
     * @returns OnboardingEmpleado
     * @throws ApiError
     */
    public static rrhhOnboardingUpdate(
        onboardingId: number,
        requestBody: OnboardingEmpleadoRequest,
    ): CancelablePromise<OnboardingEmpleado> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/rrhh/onboarding/{onboarding_id}/',
            path: {
                'onboarding_id': onboardingId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Reenviar email de bienvenida.
     * @param onboardingId Un valor de entero único que identifique este onboarding empleado.
     * @param requestBody
     * @returns OnboardingEmpleado
     * @throws ApiError
     */
    public static rrhhOnboardingReenviarEmailCreate(
        onboardingId: number,
        requestBody: OnboardingEmpleadoRequest,
    ): CancelablePromise<OnboardingEmpleado> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/onboarding/{onboarding_id}/reenviar_email/',
            path: {
                'onboarding_id': onboardingId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Validar el onboarding y aprobar todos los documentos.
     * @param onboardingId Un valor de entero único que identifique este onboarding empleado.
     * @param requestBody
     * @returns OnboardingValidacion
     * @throws ApiError
     */
    public static rrhhOnboardingValidarCreate(
        onboardingId: number,
        requestBody: OnboardingValidacionRequest,
    ): CancelablePromise<OnboardingValidacion> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/onboarding/{onboarding_id}/validar/',
            path: {
                'onboarding_id': onboardingId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
