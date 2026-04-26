/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OnboardingEmpleado } from '../models/OnboardingEmpleado';
import type { OnboardingIniciar } from '../models/OnboardingIniciar';
import type { OnboardingIniciarRequest } from '../models/OnboardingIniciarRequest';
import type { PaginatedOnboardingEmpleadoList } from '../models/PaginatedOnboardingEmpleadoList';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class OnboardingService {
    /**
     * Iniciar onboarding
     * Inicia un nuevo proceso de onboarding para un empleado.
     * @param requestBody
     * @returns OnboardingIniciar
     * @throws ApiError
     */
    public static rrhhOnboardingCreate(
        requestBody: OnboardingIniciarRequest,
    ): CancelablePromise<OnboardingIniciar> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/onboarding/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar onboardings
     * Obtiene la lista de procesos de onboarding.
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @returns PaginatedOnboardingEmpleadoList
     * @throws ApiError
     */
    public static rrhhOnboardingList(
        ordering?: string,
        page?: number,
        pageSize?: number,
        search?: string,
    ): CancelablePromise<PaginatedOnboardingEmpleadoList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/onboarding/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }
    /**
     * Detalle de onboarding
     * Obtiene el detalle de un proceso de onboarding.
     * @param onboardingId Un valor de entero único que identifique este onboarding empleado.
     * @returns OnboardingEmpleado
     * @throws ApiError
     */
    public static rrhhOnboardingRetrieve(
        onboardingId: number,
    ): CancelablePromise<OnboardingEmpleado> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/onboarding/{onboarding_id}/',
            path: {
                'onboarding_id': onboardingId,
            },
        });
    }
}
