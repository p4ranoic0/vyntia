import { apiClient } from '@/shared/api/api'

/**
 * legajoContentService — frontend client for B.12 legajo content
 * (Module 03.5 — WorkExperience, SwornDeclaration, JobHistory).
 *
 * Routes at /api/v1/{work-experiences, sworn-declarations, job-histories}/.
 */

export type SectorKind = 'privado' | 'publico' | 'ong' | 'autonomo'

export interface WorkExperience {
  id: string
  tenant?: string | null
  employee: string
  employer: string
  position_title: string
  sector: SectorKind
  sector_display: string
  start_date: string
  end_date: string | null
  is_current: boolean
  responsibilities: string
  reference_name: string
  reference_phone: string
  created_at: string
  updated_at: string
}

export type DeclarationKind =
  | 'no_parentesco'
  | 'no_incompatibilidad'
  | 'intereses'
  | 'impedimentos'

export interface SwornDeclaration {
  id: string
  tenant?: string | null
  employee: string
  kind: DeclarationKind
  kind_display: string
  declared_at: string
  valid_until: string | null
  document: string | null
  notes: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface JobHistory {
  id: string
  tenant?: string | null
  employee: string
  position: string | null
  position_label: string
  department_label: string
  start_date: string
  end_date: string | null
  motive: string
  created_at: string
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

export const legajoContentService = {
  // Work experience
  async listWorkExperiences(employeeId?: string): Promise<WorkExperience[]> {
    const query = employeeId ? `?employee=${employeeId}` : ''
    const r = await apiClient.get<PaginatedResponse<WorkExperience>>(
      `/api/v1/work-experiences/${query}`,
    )
    return unwrapList(r)
  },

  async createWorkExperience(payload: Partial<WorkExperience>): Promise<WorkExperience> {
    const r = await apiClient.post<PaginatedResponse<WorkExperience>>(
      '/api/v1/work-experiences/', payload,
    )
    return unwrapItem<WorkExperience>(r)
  },

  // Sworn declarations
  async listSwornDeclarations(employeeId?: string): Promise<SwornDeclaration[]> {
    const query = employeeId ? `?employee=${employeeId}` : ''
    const r = await apiClient.get<PaginatedResponse<SwornDeclaration>>(
      `/api/v1/sworn-declarations/${query}`,
    )
    return unwrapList(r)
  },

  async createSwornDeclaration(payload: Partial<SwornDeclaration>): Promise<SwornDeclaration> {
    const r = await apiClient.post<PaginatedResponse<SwornDeclaration>>(
      '/api/v1/sworn-declarations/', payload,
    )
    return unwrapItem<SwornDeclaration>(r)
  },

  // Job history
  async listJobHistories(employeeId?: string): Promise<JobHistory[]> {
    const query = employeeId ? `?employee=${employeeId}` : ''
    const r = await apiClient.get<PaginatedResponse<JobHistory>>(
      `/api/v1/job-histories/${query}`,
    )
    return unwrapList(r)
  },

  async createJobHistory(payload: Partial<JobHistory>): Promise<JobHistory> {
    const r = await apiClient.post<PaginatedResponse<JobHistory>>(
      '/api/v1/job-histories/', payload,
    )
    return unwrapItem<JobHistory>(r)
  },
}
