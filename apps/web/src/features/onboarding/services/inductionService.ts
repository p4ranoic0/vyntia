import { apiClient } from '@/shared/api/api'
import { unwrapBlobError } from '@/shared/api/blob'

/**
 * inductionService — frontend client for B.11 Induction (Module 03.3).
 *
 * Routes at /api/v1/onboarding/{induction-plans, induction-tasks, induction-materials}/.
 */

export type InductionStatus = 'draft' | 'in_progress' | 'completed' | 'certified'
export type InductionKind = 'general' | 'especifica' | 'tecnica' | 'mixed'
export type TaskKind = 'day_1' | 'first_week' | 'first_month' | 'ongoing'
export type MaterialFormat = 'video' | 'pdf' | 'interactive' | 'link'

export interface InductionTask {
  id: string
  plan: string
  kind: TaskKind
  kind_display: string
  title: string
  description: string
  due_offset_days: number
  order: number
  completed_at: string | null
  completed_by: string | null
  is_done: boolean
}

export interface InductionMaterial {
  id: string
  plan: string
  task: string | null
  title: string
  format: MaterialFormat
  format_display: string
  url: string
  file: string | null
  duration_minutes: number
}

export interface InductionPlan {
  id: string
  tenant?: string | null
  employee: string
  contract: string | null
  title: string
  kind: InductionKind
  kind_display: string
  status: InductionStatus
  status_display: string
  starts_at: string | null
  ends_at: string | null
  completed_at: string | null
  certified_at: string | null
  certificate_pdf: string | null
  lengua_originaria: string
  created_by: string | null
  created_at: string
  updated_at: string
  tasks: InductionTask[]
  materials: InductionMaterial[]
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

const PLANS = '/api/v1/onboarding/induction-plans'
const TASKS = '/api/v1/onboarding/induction-tasks'

export const inductionService = {
  async listPlans(): Promise<InductionPlan[]> {
    const r = await apiClient.get<PaginatedResponse<InductionPlan>>(
      `${PLANS}/?page_size=100`,
    )
    return unwrapList(r)
  },

  async getPlan(id: string): Promise<InductionPlan> {
    const r = await apiClient.get<PaginatedResponse<InductionPlan>>(`${PLANS}/${id}/`)
    return unwrapItem<InductionPlan>(r)
  },

  async createPlan(payload: {
    employee: string
    contract?: string | null
    kind?: InductionKind
    title?: string
    lengua_originaria?: string
  }): Promise<InductionPlan> {
    const r = await apiClient.post<PaginatedResponse<InductionPlan>>(`${PLANS}/`, payload)
    return unwrapItem<InductionPlan>(r)
  },

  async start(id: string): Promise<InductionPlan> {
    const r = await apiClient.post<PaginatedResponse<InductionPlan>>(`${PLANS}/${id}/start/`)
    return unwrapItem<InductionPlan>(r)
  },

  async complete(id: string): Promise<InductionPlan> {
    const r = await apiClient.post<PaginatedResponse<InductionPlan>>(`${PLANS}/${id}/complete/`)
    return unwrapItem<InductionPlan>(r)
  },

  async certify(id: string): Promise<InductionPlan> {
    const r = await apiClient.post<PaginatedResponse<InductionPlan>>(`${PLANS}/${id}/certify/`)
    return unwrapItem<InductionPlan>(r)
  },

  async assignMentor(id: string, mentor: string, notes = ''): Promise<InductionPlan> {
    const r = await apiClient.post<PaginatedResponse<InductionPlan>>(
      `${PLANS}/${id}/assign-mentor/`,
      { mentor, notes },
    )
    return unwrapItem<InductionPlan>(r)
  },

  async recordEvaluation(
    id: string,
    payload: { score: number; competencies?: Record<string, unknown>; comments?: string },
  ): Promise<{ plan: InductionPlan; evaluation: { id: string; score: number; passed: boolean } }> {
    const r = await apiClient.post<
      PaginatedResponse<{ plan: InductionPlan; evaluation: { id: string; score: number; passed: boolean } }>
    >(`${PLANS}/${id}/record-evaluation/`, payload)
    return unwrapItem(r)
  },

  async downloadCertificatePdf(id: string): Promise<Blob> {
    try {
      const r = await apiClient.get<Blob>(`${PLANS}/${id}/certificate-pdf/`, {
        responseType: 'blob',
      })
      return r.data
    } catch (err) {
      throw await unwrapBlobError(err)
    }
  },

  async markTaskDone(taskId: string): Promise<InductionTask> {
    const r = await apiClient.post<PaginatedResponse<InductionTask>>(
      `${TASKS}/${taskId}/mark-done/`,
    )
    return unwrapItem<InductionTask>(r)
  },
}
