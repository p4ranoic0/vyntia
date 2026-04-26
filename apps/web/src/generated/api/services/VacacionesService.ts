/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AprobacionSolicitudRequest } from '../models/AprobacionSolicitudRequest';
import type { ConfiguracionVacaciones } from '../models/ConfiguracionVacaciones';
import type { ConfiguracionVacacionesRequest } from '../models/ConfiguracionVacacionesRequest';
import type { GoceVacaciones } from '../models/GoceVacaciones';
import type { GoceVacacionesRequest } from '../models/GoceVacacionesRequest';
import type { HistorialSolicitudVacaciones } from '../models/HistorialSolicitudVacaciones';
import type { PaginatedGoceVacacionesList } from '../models/PaginatedGoceVacacionesList';
import type { PaginatedHistorialSolicitudVacacionesList } from '../models/PaginatedHistorialSolicitudVacacionesList';
import type { PaginatedPeriodoVacacionalList } from '../models/PaginatedPeriodoVacacionalList';
import type { PaginatedSolicitudVacacionesList } from '../models/PaginatedSolicitudVacacionesList';
import type { PatchedConfiguracionVacacionesRequest } from '../models/PatchedConfiguracionVacacionesRequest';
import type { PatchedGoceVacacionesRequest } from '../models/PatchedGoceVacacionesRequest';
import type { PatchedPeriodoVacacionalRequest } from '../models/PatchedPeriodoVacacionalRequest';
import type { PatchedSolicitudVacacionesRequest } from '../models/PatchedSolicitudVacacionesRequest';
import type { PeriodoVacacional } from '../models/PeriodoVacacional';
import type { PeriodoVacacionalRequest } from '../models/PeriodoVacacionalRequest';
import type { SolicitudVacaciones } from '../models/SolicitudVacaciones';
import type { SolicitudVacacionesCreate } from '../models/SolicitudVacacionesCreate';
import type { SolicitudVacacionesCreateRequest } from '../models/SolicitudVacacionesCreateRequest';
import type { SolicitudVacacionesRequest } from '../models/SolicitudVacacionesRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class VacacionesService {
    /**
     * Crear configuración de vacaciones
     * Crea una nueva configuración por ámbito general, área o empleado.
     * @param requestBody
     * @returns any Configuración creada correctamente
     * @throws ApiError
     */
    public static vacacionesConfiguracionesCreate(
        requestBody: ConfiguracionVacacionesRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/vacaciones/configuraciones/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Datos inválidos`,
                401: `No autenticado`,
                403: `Sin permisos de administrador`,
            },
        });
    }
    /**
     * Listar configuraciones de vacaciones
     * Retorna configuraciones activas/inactivas según filtros del usuario RRHH.
     * @param activo
     * @param area
     * @param empleado
     * @param fechaFinVigenciaDesde
     * @param fechaFinVigenciaHasta
     * @param fechaInicioVigenciaDesde
     * @param fechaInicioVigenciaHasta
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @param tipoConfiguracion * `general` - General
     * * `area` - Por Área
     * * `empleado` - Por Empleado
     * * `cargo` - Por Cargo
     * @returns any Listado paginado de configuraciones
     * @throws ApiError
     */
    public static vacacionesConfiguracionesList(
        activo?: boolean,
        area?: number,
        empleado?: number,
        fechaFinVigenciaDesde?: string,
        fechaFinVigenciaHasta?: string,
        fechaInicioVigenciaDesde?: string,
        fechaInicioVigenciaHasta?: string,
        ordering?: string,
        page?: number,
        pageSize?: number,
        search?: string,
        tipoConfiguracion?: 'area' | 'cargo' | 'empleado' | 'general',
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/vacaciones/configuraciones/',
            query: {
                'activo': activo,
                'area': area,
                'empleado': empleado,
                'fecha_fin_vigencia_desde': fechaFinVigenciaDesde,
                'fecha_fin_vigencia_hasta': fechaFinVigenciaHasta,
                'fecha_inicio_vigencia_desde': fechaInicioVigenciaDesde,
                'fecha_inicio_vigencia_hasta': fechaInicioVigenciaHasta,
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
                'tipo_configuracion': tipoConfiguracion,
            },
            errors: {
                401: `No autenticado`,
                403: `Sin permisos RRHH`,
            },
        });
    }
    /**
     * Desactivar configuración de vacaciones
     * @param configuracionId Un valor de entero único que identifique este configuracion vacaciones.
     * @returns void
     * @throws ApiError
     */
    public static vacacionesConfiguracionesDestroy(
        configuracionId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/vacaciones/configuraciones/{configuracion_id}/',
            path: {
                'configuracion_id': configuracionId,
            },
        });
    }
    /**
     * Obtener configuración de vacaciones
     * @param configuracionId Un valor de entero único que identifique este configuracion vacaciones.
     * @returns ConfiguracionVacaciones
     * @throws ApiError
     */
    public static vacacionesConfiguracionesRetrieve(
        configuracionId: number,
    ): CancelablePromise<ConfiguracionVacaciones> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/vacaciones/configuraciones/{configuracion_id}/',
            path: {
                'configuracion_id': configuracionId,
            },
        });
    }
    /**
     * Actualizar parcialmente configuración
     * @param configuracionId Un valor de entero único que identifique este configuracion vacaciones.
     * @param requestBody
     * @returns ConfiguracionVacaciones
     * @throws ApiError
     */
    public static vacacionesConfiguracionesPartialUpdate(
        configuracionId: number,
        requestBody?: PatchedConfiguracionVacacionesRequest,
    ): CancelablePromise<ConfiguracionVacaciones> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/vacaciones/configuraciones/{configuracion_id}/',
            path: {
                'configuracion_id': configuracionId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Actualizar configuración de vacaciones
     * @param configuracionId Un valor de entero único que identifique este configuracion vacaciones.
     * @param requestBody
     * @returns ConfiguracionVacaciones
     * @throws ApiError
     */
    public static vacacionesConfiguracionesUpdate(
        configuracionId: number,
        requestBody: ConfiguracionVacacionesRequest,
    ): CancelablePromise<ConfiguracionVacaciones> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/vacaciones/configuraciones/{configuracion_id}/',
            path: {
                'configuracion_id': configuracionId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param requestBody
     * @returns PeriodoVacacional
     * @throws ApiError
     */
    public static vacacionesPeriodosCreate(
        requestBody: PeriodoVacacionalRequest,
    ): CancelablePromise<PeriodoVacacional> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/vacaciones/periodos/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar períodos vacacionales
     * @param anoPeriodo
     * @param anoPeriodoDesde
     * @param anoPeriodoHasta
     * @param area
     * @param contratoId
     * @param diasPendientesMax
     * @param diasPendientesMin
     * @param empleado
     * @param estadoPeriodo * `activo` - Activo
     * * `cerrado` - Cerrado
     * * `vencido` - Vencido
     * * `cancelado` - Cancelado
     * @param fechaInicioDesde
     * @param fechaInicioHasta
     * @param fechaVencimientoDesde
     * @param fechaVencimientoHasta
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @param vencido
     * @returns PaginatedPeriodoVacacionalList
     * @throws ApiError
     */
    public static vacacionesPeriodosList(
        anoPeriodo?: number,
        anoPeriodoDesde?: number,
        anoPeriodoHasta?: number,
        area?: string,
        contratoId?: number,
        diasPendientesMax?: number,
        diasPendientesMin?: number,
        empleado?: number,
        estadoPeriodo?: 'activo' | 'cancelado' | 'cerrado' | 'vencido',
        fechaInicioDesde?: string,
        fechaInicioHasta?: string,
        fechaVencimientoDesde?: string,
        fechaVencimientoHasta?: string,
        ordering?: string,
        page?: number,
        pageSize?: number,
        search?: string,
        vencido?: boolean,
    ): CancelablePromise<PaginatedPeriodoVacacionalList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/vacaciones/periodos/',
            query: {
                'ano_periodo': anoPeriodo,
                'ano_periodo_desde': anoPeriodoDesde,
                'ano_periodo_hasta': anoPeriodoHasta,
                'area': area,
                'contrato_id': contratoId,
                'dias_pendientes_max': diasPendientesMax,
                'dias_pendientes_min': diasPendientesMin,
                'empleado': empleado,
                'estado_periodo': estadoPeriodo,
                'fecha_inicio_desde': fechaInicioDesde,
                'fecha_inicio_hasta': fechaInicioHasta,
                'fecha_vencimiento_desde': fechaVencimientoDesde,
                'fecha_vencimiento_hasta': fechaVencimientoHasta,
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
                'vencido': vencido,
            },
        });
    }
    /**
     * @param requestBody
     * @returns PeriodoVacacional
     * @throws ApiError
     */
    public static vacacionesPeriodosGenerarMasivoCreate(
        requestBody: PeriodoVacacionalRequest,
    ): CancelablePromise<PeriodoVacacional> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/vacaciones/periodos/generar-masivo/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param periodoId Un valor de entero único que identifique este periodo vacacional.
     * @returns void
     * @throws ApiError
     */
    public static vacacionesPeriodosDestroy(
        periodoId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/vacaciones/periodos/{periodo_id}/',
            path: {
                'periodo_id': periodoId,
            },
        });
    }
    /**
     * Obtener período vacacional
     * @param periodoId Un valor de entero único que identifique este periodo vacacional.
     * @returns PeriodoVacacional
     * @throws ApiError
     */
    public static vacacionesPeriodosRetrieve(
        periodoId: number,
    ): CancelablePromise<PeriodoVacacional> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/vacaciones/periodos/{periodo_id}/',
            path: {
                'periodo_id': periodoId,
            },
        });
    }
    /**
     * @param periodoId Un valor de entero único que identifique este periodo vacacional.
     * @param requestBody
     * @returns PeriodoVacacional
     * @throws ApiError
     */
    public static vacacionesPeriodosPartialUpdate(
        periodoId: number,
        requestBody?: PatchedPeriodoVacacionalRequest,
    ): CancelablePromise<PeriodoVacacional> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/vacaciones/periodos/{periodo_id}/',
            path: {
                'periodo_id': periodoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param periodoId Un valor de entero único que identifique este periodo vacacional.
     * @param requestBody
     * @returns PeriodoVacacional
     * @throws ApiError
     */
    public static vacacionesPeriodosUpdate(
        periodoId: number,
        requestBody: PeriodoVacacionalRequest,
    ): CancelablePromise<PeriodoVacacional> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/vacaciones/periodos/{periodo_id}/',
            path: {
                'periodo_id': periodoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param periodoId Un valor de entero único que identifique este periodo vacacional.
     * @param requestBody
     * @returns PeriodoVacacional
     * @throws ApiError
     */
    public static vacacionesPeriodosAjustarDiasCreate(
        periodoId: number,
        requestBody: PeriodoVacacionalRequest,
    ): CancelablePromise<PeriodoVacacional> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/vacaciones/periodos/{periodo_id}/ajustar-dias/',
            path: {
                'periodo_id': periodoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Crear solicitud de vacaciones
     * @param requestBody
     * @returns SolicitudVacacionesCreate
     * @throws ApiError
     */
    public static vacacionesSolicitudesCreate(
        requestBody: SolicitudVacacionesCreateRequest,
    ): CancelablePromise<SolicitudVacacionesCreate> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/vacaciones/solicitudes/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar solicitudes de vacaciones
     * @param anoPeriodo
     * @param area
     * @param contratoId
     * @param diasSolicitadosMax
     * @param diasSolicitadosMin
     * @param empleado
     * @param estadoSolicitud * `borrador` - Borrador
     * * `enviada` - Enviada
     * * `en_revision` - En Revisión
     * * `aprobada_jefe` - Aprobada por Jefe
     * * `aprobada_rrhh` - Aprobada por RRHH
     * * `aprobada` - Aprobada
     * * `rechazada` - Rechazada
     * * `cancelada` - Cancelada
     * * `en_goce` - En Goce
     * * `finalizada` - Finalizada
     * @param fechaEnvioDesde
     * @param fechaEnvioHasta
     * @param fechaFinDesde
     * @param fechaFinHasta
     * @param fechaInicioDesde
     * @param fechaInicioHasta
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param pendienteJefe
     * @param pendienteRrhh
     * @param search Un término de búsqueda.
     * @param tipoSolicitud * `vacaciones` - Vacaciones
     * * `adelanto_vacaciones` - Adelanto de Vacaciones
     * * `fraccionamiento` - Fraccionamiento
     * * `postergacion` - Postergación
     * @returns PaginatedSolicitudVacacionesList
     * @throws ApiError
     */
    public static vacacionesSolicitudesList(
        anoPeriodo?: number,
        area?: string,
        contratoId?: number,
        diasSolicitadosMax?: number,
        diasSolicitadosMin?: number,
        empleado?: number,
        estadoSolicitud?: 'aprobada' | 'aprobada_jefe' | 'aprobada_rrhh' | 'borrador' | 'cancelada' | 'en_goce' | 'en_revision' | 'enviada' | 'finalizada' | 'rechazada',
        fechaEnvioDesde?: string,
        fechaEnvioHasta?: string,
        fechaFinDesde?: string,
        fechaFinHasta?: string,
        fechaInicioDesde?: string,
        fechaInicioHasta?: string,
        ordering?: string,
        page?: number,
        pageSize?: number,
        pendienteJefe?: boolean,
        pendienteRrhh?: boolean,
        search?: string,
        tipoSolicitud?: 'adelanto_vacaciones' | 'fraccionamiento' | 'postergacion' | 'vacaciones',
    ): CancelablePromise<PaginatedSolicitudVacacionesList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/vacaciones/solicitudes/',
            query: {
                'ano_periodo': anoPeriodo,
                'area': area,
                'contrato_id': contratoId,
                'dias_solicitados_max': diasSolicitadosMax,
                'dias_solicitados_min': diasSolicitadosMin,
                'empleado': empleado,
                'estado_solicitud': estadoSolicitud,
                'fecha_envio_desde': fechaEnvioDesde,
                'fecha_envio_hasta': fechaEnvioHasta,
                'fecha_fin_desde': fechaFinDesde,
                'fecha_fin_hasta': fechaFinHasta,
                'fecha_inicio_desde': fechaInicioDesde,
                'fecha_inicio_hasta': fechaInicioHasta,
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'pendiente_jefe': pendienteJefe,
                'pendiente_rrhh': pendienteRrhh,
                'search': search,
                'tipo_solicitud': tipoSolicitud,
            },
        });
    }
    /**
     * @returns SolicitudVacaciones
     * @throws ApiError
     */
    public static vacacionesSolicitudesMisSolicitudesRetrieve(): CancelablePromise<SolicitudVacaciones> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/vacaciones/solicitudes/mis-solicitudes/',
        });
    }
    /**
     * @returns SolicitudVacaciones
     * @throws ApiError
     */
    public static vacacionesSolicitudesPendientesJefeRetrieve(): CancelablePromise<SolicitudVacaciones> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/vacaciones/solicitudes/pendientes-jefe/',
        });
    }
    /**
     * @returns SolicitudVacaciones
     * @throws ApiError
     */
    public static vacacionesSolicitudesPendientesRrhhRetrieve(): CancelablePromise<SolicitudVacaciones> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/vacaciones/solicitudes/pendientes-rrhh/',
        });
    }
    /**
     * @param solicitudId Un valor de entero único que identifique este solicitud vacaciones.
     * @returns void
     * @throws ApiError
     */
    public static vacacionesSolicitudesDestroy(
        solicitudId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/vacaciones/solicitudes/{solicitud_id}/',
            path: {
                'solicitud_id': solicitudId,
            },
        });
    }
    /**
     * Obtener solicitud de vacaciones
     * @param solicitudId Un valor de entero único que identifique este solicitud vacaciones.
     * @returns SolicitudVacaciones
     * @throws ApiError
     */
    public static vacacionesSolicitudesRetrieve(
        solicitudId: number,
    ): CancelablePromise<SolicitudVacaciones> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/vacaciones/solicitudes/{solicitud_id}/',
            path: {
                'solicitud_id': solicitudId,
            },
        });
    }
    /**
     * @param solicitudId Un valor de entero único que identifique este solicitud vacaciones.
     * @param requestBody
     * @returns SolicitudVacaciones
     * @throws ApiError
     */
    public static vacacionesSolicitudesPartialUpdate(
        solicitudId: number,
        requestBody?: PatchedSolicitudVacacionesRequest,
    ): CancelablePromise<SolicitudVacaciones> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/vacaciones/solicitudes/{solicitud_id}/',
            path: {
                'solicitud_id': solicitudId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param solicitudId Un valor de entero único que identifique este solicitud vacaciones.
     * @param requestBody
     * @returns SolicitudVacaciones
     * @throws ApiError
     */
    public static vacacionesSolicitudesUpdate(
        solicitudId: number,
        requestBody: SolicitudVacacionesRequest,
    ): CancelablePromise<SolicitudVacaciones> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/vacaciones/solicitudes/{solicitud_id}/',
            path: {
                'solicitud_id': solicitudId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param solicitudId Un valor de entero único que identifique este solicitud vacaciones.
     * @param requestBody
     * @returns SolicitudVacaciones
     * @throws ApiError
     */
    public static vacacionesSolicitudesAprobarJefeCreate(
        solicitudId: number,
        requestBody: AprobacionSolicitudRequest,
    ): CancelablePromise<SolicitudVacaciones> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/vacaciones/solicitudes/{solicitud_id}/aprobar-jefe/',
            path: {
                'solicitud_id': solicitudId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param solicitudId Un valor de entero único que identifique este solicitud vacaciones.
     * @param requestBody
     * @returns SolicitudVacaciones
     * @throws ApiError
     */
    public static vacacionesSolicitudesAprobarRrhhCreate(
        solicitudId: number,
        requestBody: AprobacionSolicitudRequest,
    ): CancelablePromise<SolicitudVacaciones> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/vacaciones/solicitudes/{solicitud_id}/aprobar-rrhh/',
            path: {
                'solicitud_id': solicitudId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param solicitudId Un valor de entero único que identifique este solicitud vacaciones.
     * @param requestBody
     * @returns SolicitudVacaciones
     * @throws ApiError
     */
    public static vacacionesSolicitudesCancelarCreate(
        solicitudId: number,
        requestBody: SolicitudVacacionesRequest,
    ): CancelablePromise<SolicitudVacaciones> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/vacaciones/solicitudes/{solicitud_id}/cancelar/',
            path: {
                'solicitud_id': solicitudId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param solicitudId Un valor de entero único que identifique este solicitud vacaciones.
     * @param requestBody
     * @returns SolicitudVacaciones
     * @throws ApiError
     */
    public static vacacionesSolicitudesEnviarCreate(
        solicitudId: number,
        requestBody: SolicitudVacacionesRequest,
    ): CancelablePromise<SolicitudVacaciones> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/vacaciones/solicitudes/{solicitud_id}/enviar/',
            path: {
                'solicitud_id': solicitudId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param requestBody
     * @returns GoceVacaciones
     * @throws ApiError
     */
    public static vacacionesGocesCreate(
        requestBody: GoceVacacionesRequest,
    ): CancelablePromise<GoceVacaciones> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/vacaciones/goces/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar goces de vacaciones
     * @param anoPeriodo
     * @param area
     * @param contratoId
     * @param empleado
     * @param enCurso
     * @param estadoGoce * `programado` - Programado
     * * `en_curso` - En Curso
     * * `finalizado` - Finalizado
     * * `interrumpido` - Interrumpido
     * * `cancelado` - Cancelado
     * @param fechaFinRealDesde
     * @param fechaFinRealHasta
     * @param fechaInicioRealDesde
     * @param fechaInicioRealHasta
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @returns PaginatedGoceVacacionesList
     * @throws ApiError
     */
    public static vacacionesGocesList(
        anoPeriodo?: number,
        area?: string,
        contratoId?: number,
        empleado?: number,
        enCurso?: boolean,
        estadoGoce?: 'cancelado' | 'en_curso' | 'finalizado' | 'interrumpido' | 'programado',
        fechaFinRealDesde?: string,
        fechaFinRealHasta?: string,
        fechaInicioRealDesde?: string,
        fechaInicioRealHasta?: string,
        ordering?: string,
        page?: number,
        pageSize?: number,
        search?: string,
    ): CancelablePromise<PaginatedGoceVacacionesList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/vacaciones/goces/',
            query: {
                'ano_periodo': anoPeriodo,
                'area': area,
                'contrato_id': contratoId,
                'empleado': empleado,
                'en_curso': enCurso,
                'estado_goce': estadoGoce,
                'fecha_fin_real_desde': fechaFinRealDesde,
                'fecha_fin_real_hasta': fechaFinRealHasta,
                'fecha_inicio_real_desde': fechaInicioRealDesde,
                'fecha_inicio_real_hasta': fechaInicioRealHasta,
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }
    /**
     * @param goceId Un valor de entero único que identifique este goce vacaciones.
     * @returns void
     * @throws ApiError
     */
    public static vacacionesGocesDestroy(
        goceId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/vacaciones/goces/{goce_id}/',
            path: {
                'goce_id': goceId,
            },
        });
    }
    /**
     * Obtener goce de vacaciones
     * @param goceId Un valor de entero único que identifique este goce vacaciones.
     * @returns GoceVacaciones
     * @throws ApiError
     */
    public static vacacionesGocesRetrieve(
        goceId: number,
    ): CancelablePromise<GoceVacaciones> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/vacaciones/goces/{goce_id}/',
            path: {
                'goce_id': goceId,
            },
        });
    }
    /**
     * @param goceId Un valor de entero único que identifique este goce vacaciones.
     * @param requestBody
     * @returns GoceVacaciones
     * @throws ApiError
     */
    public static vacacionesGocesPartialUpdate(
        goceId: number,
        requestBody?: PatchedGoceVacacionesRequest,
    ): CancelablePromise<GoceVacaciones> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/vacaciones/goces/{goce_id}/',
            path: {
                'goce_id': goceId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param goceId Un valor de entero único que identifique este goce vacaciones.
     * @param requestBody
     * @returns GoceVacaciones
     * @throws ApiError
     */
    public static vacacionesGocesUpdate(
        goceId: number,
        requestBody: GoceVacacionesRequest,
    ): CancelablePromise<GoceVacaciones> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/vacaciones/goces/{goce_id}/',
            path: {
                'goce_id': goceId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @returns PaginatedHistorialSolicitudVacacionesList
     * @throws ApiError
     */
    public static vacacionesHistorialList(
        ordering?: string,
        page?: number,
        pageSize?: number,
    ): CancelablePromise<PaginatedHistorialSolicitudVacacionesList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/vacaciones/historial/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
            },
        });
    }
    /**
     * @param historialId Un valor de entero único que identifique este historial solicitud vacaciones.
     * @returns HistorialSolicitudVacaciones
     * @throws ApiError
     */
    public static vacacionesHistorialRetrieve(
        historialId: number,
    ): CancelablePromise<HistorialSolicitudVacaciones> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/vacaciones/historial/{historial_id}/',
            path: {
                'historial_id': historialId,
            },
        });
    }
}
