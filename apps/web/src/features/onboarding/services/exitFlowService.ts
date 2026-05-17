import { apiClient } from '@/shared/api/api'

/**
 * exitFlowService — frontend client for B.14 ExitInterview + HandoverChecklist
 * + HandoverItem + SystemsOffboarding (Module 03.7). Routes at /api/v1/onboarding/.
 */

export type InterviewSentiment =
  | 'positivo' | 'neutral' | 'negativo' | 'mixto' | 'no_responde'

export interface ExitInterview {
  id: string
  tenant?: string | null
  termination: string
  status: 'pending' | 'completed' | 'skipped'
  status_display: string
  answers: Record<string, unknown>
  sentiment: InterviewSentiment | ''
  sentiment_display: string
  comments: string
  interviewer: string | null
  interview_date: string | null
  created_at: string
  updated_at: string
}

export type HandoverItemStatus = 'pendiente' | 'entregado' | 'no_aplica'
export type HandoverItemKind =
  | 'proyecto' | 'documento' | 'equipo' | 'acceso' | 'credencial' | 'otro'

export interface HandoverItem {
  id: string
  checklist: string
  kind: HandoverItemKind
  kind_display: string
  name: string
  description: string
  is_required: boolean
  status: HandoverItemStatus
  status_display: string
  delivered_at: string | null
  delivered_by: string | null
  notes: string
  order: number
  created_at: string
  updated_at: string
}

export interface HandoverChecklist {
  id: string
  tenant?: string | null
  termination: string
  status: 'draft' | 'in_progress' | 'completed'
  status_display: string
  receiving_user: string | null
  signed_by_outgoing: string | null
  signed_by_outgoing_at: string | null
  signed_by_incoming: string | null
  signed_by_incoming_at: string | null
  completed_at: string | null
  notes: string
  items: HandoverItem[]
  created_at: string
  updated_at: string
}

export interface SystemsOffboarding {
  id: string
  tenant?: string | null
  termination: string
  status: 'pending' | 'in_progress' | 'completed'
  status_display: string
  checks: Record<string, boolean>
  notes: string
  completed_at: string | null
  completed_by: string | null
  created_at: string
  updated_at: string
}

export interface ExitFlowScaffoldResult {
  interview: ExitInterview
  checklist: HandoverChecklist
  systems_offboarding: SystemsOffboarding
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

const BASE = '/api/v1/onboarding'

export const exitFlowService = {
  async scaffold(termination: string): Promise<ExitFlowScaffoldResult> {
    const r = await apiClient.post<PaginatedResponse<ExitFlowScaffoldResult>>(
      `${BASE}/exit-flow-scaffold/`, { termination },
    )
    return unwrapItem<ExitFlowScaffoldResult>(r)
  },

  // ExitInterview
  async listInterviews(): Promise<ExitInterview[]> {
    const r = await apiClient.get<PaginatedResponse<ExitInterview>>(
      `${BASE}/exit-interviews/?page_size=100`,
    )
    return unwrapList(r)
  },

  async submitInterview(
    id: string,
    payload: {
      answers: Record<string, unknown>
      sentiment: InterviewSentiment
      comments?: string
      interview_date?: string
    },
  ): Promise<ExitInterview> {
    const r = await apiClient.post<PaginatedResponse<ExitInterview>>(
      `${BASE}/exit-interviews/${id}/submit/`, payload,
    )
    return unwrapItem<ExitInterview>(r)
  },

  // HandoverChecklist
  async listChecklists(): Promise<HandoverChecklist[]> {
    const r = await apiClient.get<PaginatedResponse<HandoverChecklist>>(
      `${BASE}/handover-checklists/?page_size=100`,
    )
    return unwrapList(r)
  },

  async completeChecklist(
    id: string,
    payload: { signed_by_outgoing: number; signed_by_incoming: number },
  ): Promise<HandoverChecklist> {
    const r = await apiClient.post<PaginatedResponse<HandoverChecklist>>(
      `${BASE}/handover-checklists/${id}/complete/`, payload,
    )
    return unwrapItem<HandoverChecklist>(r)
  },

  // HandoverItem
  async deliverItem(id: string, notes = ''): Promise<HandoverItem> {
    const r = await apiClient.post<PaginatedResponse<HandoverItem>>(
      `${BASE}/handover-items/${id}/deliver/`, { notes },
    )
    return unwrapItem<HandoverItem>(r)
  },

  async itemNoAplica(id: string, notes = ''): Promise<HandoverItem> {
    const r = await apiClient.post<PaginatedResponse<HandoverItem>>(
      `${BASE}/handover-items/${id}/no-aplica/`, { notes },
    )
    return unwrapItem<HandoverItem>(r)
  },

  // SystemsOffboarding
  async listSystemsOffboardings(): Promise<SystemsOffboarding[]> {
    const r = await apiClient.get<PaginatedResponse<SystemsOffboarding>>(
      `${BASE}/systems-offboardings/?page_size=100`,
    )
    return unwrapList(r)
  },

  async completeSystemsOffboarding(
    id: string,
    payload: { checks: Record<string, boolean>; notes?: string },
  ): Promise<SystemsOffboarding> {
    const r = await apiClient.post<PaginatedResponse<SystemsOffboarding>>(
      `${BASE}/systems-offboardings/${id}/complete/`, payload,
    )
    return unwrapItem<SystemsOffboarding>(r)
  },
}
