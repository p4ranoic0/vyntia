import { apiClient } from '@/shared/api/api'

/**
 * dossierService — frontend client for B.12 DigitalDossier (Module 03.5).
 *
 * Routes at /api/v1/documents/digital-dossiers/, /dossier-sections/, /document-access-logs/.
 */

export type DossierSectionKind =
  | 'datos_personales'
  | 'datos_academicos'
  | 'experiencia_laboral'
  | 'contratos'
  | 'declaraciones_juradas'
  | 'identidad_cuspp'
  | 'historial_puestos'
  | 'evaluaciones'
  | 'capacitaciones'
  | 'reconocimientos'
  | 'sanciones'
  | 'licencias'
  | 'medicos'
  | 'accidentes'
  | 'cese'

export interface DossierSection {
  id: string
  dossier: string
  kind: DossierSectionKind
  kind_display: string
  label: string
  permission_level: number
  order: number
  notes: string
}

export interface DigitalDossier {
  id: string
  tenant?: string | null
  employee: string
  is_closed: boolean
  closed_at: string | null
  retention_until: string | null
  created_at: string
  updated_at: string
  sections: DossierSection[]
}

export type AccessAction = 'view' | 'download' | 'preview' | 'print' | 'share' | 'denied'

export interface DocumentAccessLog {
  id: string
  document: string
  user: string | null
  action: AccessAction
  action_display: string
  ip: string | null
  user_agent: string
  required_permission_level: number
  user_permission_level: number
  notes: string
  occurred_at: string
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

const DOSSIERS = '/api/v1/documents/digital-dossiers'
const ACCESS_LOGS = '/api/v1/documents/document-access-logs'

export const dossierService = {
  async list(): Promise<DigitalDossier[]> {
    const r = await apiClient.get<PaginatedResponse<DigitalDossier>>(
      `${DOSSIERS}/?page_size=100`,
    )
    return unwrapList(r)
  },

  async get(id: string): Promise<DigitalDossier> {
    const r = await apiClient.get<PaginatedResponse<DigitalDossier>>(`${DOSSIERS}/${id}/`)
    return unwrapItem<DigitalDossier>(r)
  },

  async create(employeeId: string): Promise<DigitalDossier> {
    const r = await apiClient.post<PaginatedResponse<DigitalDossier>>(
      `${DOSSIERS}/`,
      { employee: employeeId },
    )
    return unwrapItem<DigitalDossier>(r)
  },

  async build(id: string): Promise<DigitalDossier> {
    const r = await apiClient.post<PaginatedResponse<DigitalDossier>>(
      `${DOSSIERS}/${id}/build/`,
    )
    return unwrapItem<DigitalDossier>(r)
  },

  async downloadConsolidatedPdf(id: string): Promise<Blob> {
    const r = await apiClient.get<Blob>(`${DOSSIERS}/${id}/consolidated-pdf/`, {
      responseType: 'blob',
    })
    return r.data
  },

  async listAccessLogs(documentId?: string): Promise<DocumentAccessLog[]> {
    const query = documentId ? `?document=${documentId}` : ''
    const r = await apiClient.get<PaginatedResponse<DocumentAccessLog>>(
      `${ACCESS_LOGS}/${query}`,
    )
    return unwrapList(r)
  },
}
