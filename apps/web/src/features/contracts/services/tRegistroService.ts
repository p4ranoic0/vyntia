import { apiClient } from '@/shared/api/api'
import { unwrapBlobError } from '@/shared/api/blob'

/**
 * tRegistroService — frontend client for B.10 T-Registro SUNAT (Module 03.2).
 *
 * Routes at /api/v1/t-registro-declarations/ (flat under /api/v1/).
 */

export type DeclarationType = 'alta' | 'baja' | 'modificacion'

export type DeclarationStatus =
  | 'draft'
  | 'validated'
  | 'submitted'
  | 'accepted'
  | 'rejected'

export type RegimenPensionario =
  | 'snp'
  | 'spp'
  | 'decreto_19990'
  | 'decreto_20530'
  | 'sin_regimen'

export type RegimenSalud = 'essalud' | 'eps' | 'sctr' | 'ninguno'

export interface TRegistroDeclaration {
  id: string
  tenant?: string | null
  declaration_type: DeclarationType
  declaration_type_display: string
  status: DeclarationStatus
  status_display: string
  contract: string
  employee: string
  employer_ruc: string
  employer_razon_social: string
  worker_doc_type: string
  worker_doc_number: string
  worker_apellido_paterno: string
  worker_apellido_materno: string
  worker_nombres: string
  worker_birth_date: string
  worker_gender: string
  worker_nationality_code: string
  worker_address: string
  contract_start_date: string
  contract_end_date: string | null
  work_modality_code: string
  occupation_code: string
  regimen_laboral_code: string
  regimen_pensionario: RegimenPensionario
  pension_provider_code: string
  cuspp: string
  regimen_salud: RegimenSalud
  eps_code: string
  remuneracion_basica: string
  jornada_horas_semanales: number
  anexo3_txt: string
  pvs_errors: string[]
  sunat_reference: string
  sunat_response_at: string | null
  rejection_reason: string
  submitted_at: string | null
  submitted_by: string | null
  created_at: string
  updated_at: string
}

interface PaginatedResponse<T> {
  success?: boolean
  message?: string
  data?: T[] | { results?: T[] } | T
  results?: T[]
  meta?: { pagination?: { total_items?: number; current_page?: number } }
}

function unwrapList<T>(resp: { data: PaginatedResponse<T> }): T[] {
  const raw = resp.data
  const fromData = (raw?.data as { results?: T[] } | undefined)?.results
  if (Array.isArray(fromData)) return fromData
  if (Array.isArray(raw?.data)) return raw.data as T[]
  if (Array.isArray(raw?.results)) return raw.results
  return []
}

function unwrapItem<T>(resp: { data: PaginatedResponse<T> }): T {
  const raw = resp.data
  if (
    raw &&
    typeof raw === 'object' &&
    'data' in raw &&
    raw.data &&
    typeof raw.data === 'object' &&
    !Array.isArray(raw.data)
  ) {
    return raw.data as T
  }
  return raw as unknown as T
}

const BASE = '/api/v1/t-registro-declarations'

export const tRegistroService = {
  async list(): Promise<TRegistroDeclaration[]> {
    const r = await apiClient.get<PaginatedResponse<TRegistroDeclaration>>(
      `${BASE}/?page_size=100`,
    )
    return unwrapList(r)
  },

  async get(id: string): Promise<TRegistroDeclaration> {
    const r = await apiClient.get<PaginatedResponse<TRegistroDeclaration>>(
      `${BASE}/${id}/`,
    )
    return unwrapItem<TRegistroDeclaration>(r)
  },

  async create(
    payload: Partial<TRegistroDeclaration>,
  ): Promise<TRegistroDeclaration> {
    const r = await apiClient.post<PaginatedResponse<TRegistroDeclaration>>(
      `${BASE}/`,
      payload,
    )
    return unwrapItem<TRegistroDeclaration>(r)
  },

  async update(
    id: string,
    payload: Partial<TRegistroDeclaration>,
  ): Promise<TRegistroDeclaration> {
    const r = await apiClient.patch<PaginatedResponse<TRegistroDeclaration>>(
      `${BASE}/${id}/`,
      payload,
    )
    return unwrapItem<TRegistroDeclaration>(r)
  },

  async generateAnexo3(id: string): Promise<TRegistroDeclaration> {
    const r = await apiClient.post<PaginatedResponse<TRegistroDeclaration>>(
      `${BASE}/${id}/generate-anexo3/`,
    )
    return unwrapItem<TRegistroDeclaration>(r)
  },

  async validatePvs(id: string): Promise<TRegistroDeclaration> {
    const r = await apiClient.post<PaginatedResponse<TRegistroDeclaration>>(
      `${BASE}/${id}/validate-pvs/`,
    )
    return unwrapItem<TRegistroDeclaration>(r)
  },

  async submit(id: string, reference = ''): Promise<TRegistroDeclaration> {
    const r = await apiClient.post<PaginatedResponse<TRegistroDeclaration>>(
      `${BASE}/${id}/submit/`,
      { reference },
    )
    return unwrapItem<TRegistroDeclaration>(r)
  },

  async markAccepted(id: string, reference = ''): Promise<TRegistroDeclaration> {
    const r = await apiClient.post<PaginatedResponse<TRegistroDeclaration>>(
      `${BASE}/${id}/mark-accepted/`,
      { reference },
    )
    return unwrapItem<TRegistroDeclaration>(r)
  },

  async markRejected(id: string, reason: string): Promise<TRegistroDeclaration> {
    const r = await apiClient.post<PaginatedResponse<TRegistroDeclaration>>(
      `${BASE}/${id}/mark-rejected/`,
      { reason },
    )
    return unwrapItem<TRegistroDeclaration>(r)
  },

  async downloadAnexo3Txt(id: string): Promise<Blob> {
    try {
      const r = await apiClient.get<Blob>(
        `${BASE}/${id}/anexo3-txt/`,
        { responseType: 'blob' },
      )
      return r.data
    } catch (err) {
      throw await unwrapBlobError(err)
    }
  },
}
