/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DocumentosDigitales } from '../models/DocumentosDigitales';
import type { DocumentosDigitalesCreate } from '../models/DocumentosDigitalesCreate';
import type { DocumentosDigitalesCreateRequest } from '../models/DocumentosDigitalesCreateRequest';
import type { DocumentosDigitalesRequest } from '../models/DocumentosDigitalesRequest';
import type { PaginatedDocumentosDigitalesList } from '../models/PaginatedDocumentosDigitalesList';
import type { PatchedDocumentosDigitalesRequest } from '../models/PatchedDocumentosDigitalesRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DocumentosDigitalesService {
    /**
     * Crear documento digital
     * Crea un nuevo documento digital en el sistema.
     * @param requestBody
     * @returns DocumentosDigitalesCreate
     * @throws ApiError
     */
    public static rrhhDocumentosDigitalesCreate(
        requestBody: DocumentosDigitalesCreateRequest,
    ): CancelablePromise<DocumentosDigitalesCreate> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/rrhh/documentos-digitales/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Listar documentos digitales
     * Obtiene una lista paginada de todos los documentos digitales con filtros opcionales.
     * @param ordering Qué campo usar para ordenar los resultados.
     * @param page Un número de página dentro del conjunto de resultados paginado.
     * @param pageSize Número de resultados a devolver por página.
     * @param search Un término de búsqueda.
     * @returns PaginatedDocumentosDigitalesList
     * @throws ApiError
     */
    public static rrhhDocumentosDigitalesList(
        ordering?: string,
        page?: number,
        pageSize?: number,
        search?: string,
    ): CancelablePromise<PaginatedDocumentosDigitalesList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/documentos-digitales/',
            query: {
                'ordering': ordering,
                'page': page,
                'page_size': pageSize,
                'search': search,
            },
        });
    }
    /**
     * Eliminar documento digital
     * Elimina un documento digital del sistema.
     * @param documentoId Un valor de entero único que identifique este documentos digitales.
     * @returns void
     * @throws ApiError
     */
    public static rrhhDocumentosDigitalesDestroy(
        documentoId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/rrhh/documentos-digitales/{documento_id}/',
            path: {
                'documento_id': documentoId,
            },
        });
    }
    /**
     * Obtener documento digital
     * Obtiene los detalles de un documento digital específico por su ID.
     * @param documentoId Un valor de entero único que identifique este documentos digitales.
     * @returns DocumentosDigitales
     * @throws ApiError
     */
    public static rrhhDocumentosDigitalesRetrieve(
        documentoId: number,
    ): CancelablePromise<DocumentosDigitales> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/rrhh/documentos-digitales/{documento_id}/',
            path: {
                'documento_id': documentoId,
            },
        });
    }
    /**
     * Actualizar documento digital parcialmente
     * Actualiza parcialmente un documento digital existente.
     * @param documentoId Un valor de entero único que identifique este documentos digitales.
     * @param requestBody
     * @returns DocumentosDigitales
     * @throws ApiError
     */
    public static rrhhDocumentosDigitalesPartialUpdate(
        documentoId: number,
        requestBody?: PatchedDocumentosDigitalesRequest,
    ): CancelablePromise<DocumentosDigitales> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/rrhh/documentos-digitales/{documento_id}/',
            path: {
                'documento_id': documentoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Actualizar documento digital
     * Actualiza completamente un documento digital existente.
     * @param documentoId Un valor de entero único que identifique este documentos digitales.
     * @param requestBody
     * @returns DocumentosDigitales
     * @throws ApiError
     */
    public static rrhhDocumentosDigitalesUpdate(
        documentoId: number,
        requestBody: DocumentosDigitalesRequest,
    ): CancelablePromise<DocumentosDigitales> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/rrhh/documentos-digitales/{documento_id}/',
            path: {
                'documento_id': documentoId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
