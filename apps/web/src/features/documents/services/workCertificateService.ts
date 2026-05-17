import { apiClient } from '@/shared/api/api'

/**
 * workCertificateService — frontend client for B.14 Constancia de Trabajo
 * (Module 03.7, Art. 45 LPCL). Routes at /api/v1/documents/work-certificates/.
 */

export interface WorkCertificate {
  id: string
  tenant?: string | null
  termination: string
  employee: string
  contract: string
  numero_constancia: string
  fecha_emision: string
  cargo_snapshot: string
  area_snapshot: string
  fecha_inicio_snapshot: string | null
  fecha_fin_snapshot: string | null
  sueldo_snapshot: string
  motivo_cese_textual: string
  signed_by: string | null
  pdf_file: string | null
  digital_document: string | null
  created_at: string
  updated_at: string
}

interface PaginatedResponse<T> {
  success?: boolean
  message?: string
  data?: T[] | { results?: T[] } | T
  results?: T[]
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

const BASE = '/api/v1/documents/work-certificates'

export const workCertificateService = {
  async list(): Promise<WorkCertificate[]> {
    const r = await apiClient.get<PaginatedResponse<WorkCertificate>>(
      `${BASE}/?page_size=100`,
    )
    return unwrapList(r)
  },

  async generate(termination: string): Promise<WorkCertificate> {
    const r = await apiClient.post<PaginatedResponse<WorkCertificate>>(
      `${BASE}/generate/`, { termination },
    )
    return unwrapItem<WorkCertificate>(r)
  },

  async downloadPdf(id: string): Promise<Blob> {
    const r = await apiClient.get<Blob>(`${BASE}/${id}/download-pdf/`, {
      responseType: 'blob',
    })
    return r.data
  },
}
