import { apiClient } from '@/shared/api/api'

/**
 * strategicPlanService — frontend client for B.15b Strategic Plan (Module 01 § 2).
 *
 * Routes flat at /api/v1/:
 * - /strategic-plans/, /strategic-objectives/, /kpis/
 */

export type StrategicPlanStatus = 'draft' | 'active' | 'completed' | 'archived'
export type KPIStatus = 'on_track' | 'at_risk' | 'off_track' | 'done'

export interface HRStrategicPlan {
  id: string
  tenant?: string | null
  name: string
  fiscal_year: number
  period_start: string
  period_end: string
  description: string
  status: StrategicPlanStatus
  status_display: string
  owner_user: string
  approved_by: string | null
  approved_at: string | null
  created_at: string
  updated_at: string
}

export interface StrategicObjective {
  id: string
  plan: string
  code: string
  title: string
  description: string
  weight: string
  order: number
  owner_user: string | null
  created_at: string
  updated_at: string
}

export interface KPI {
  id: string
  objective: string
  name: string
  formula_note: string
  unit: string
  target: string
  actual: string
  target_date: string | null
  status: KPIStatus
  status_display: string
  progress_pct: string
  created_at: string
  updated_at: string
}

export interface PlanProgress {
  objectives: Array<{
    id: string
    code: string
    title: string
    weight: string
    avg_progress_pct: string
    kpi_count: number
  }>
  overall_pct: string
  total_weight: string
}

interface ApiEnvelope<T> {
  data?: T[] | { results?: T[] } | T
  results?: T[]
}

function unwrapList<T>(resp: { data: ApiEnvelope<T> }): T[] {
  const raw = resp.data
  const fromData = (raw?.data as { results?: T[] } | undefined)?.results
  if (Array.isArray(fromData)) return fromData
  if (Array.isArray(raw?.data)) return raw.data as T[]
  if (Array.isArray(raw?.results)) return raw.results
  return []
}

function unwrapItem<T>(resp: { data: ApiEnvelope<T> }): T {
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

const PLANS = '/api/v1/strategic-plans'
const OBJECTIVES = '/api/v1/strategic-objectives'
const KPIS = '/api/v1/kpis'

export const strategicPlanService = {
  async listPlans(): Promise<HRStrategicPlan[]> {
    const r = await apiClient.get<ApiEnvelope<HRStrategicPlan>>(`${PLANS}/?page_size=100`)
    return unwrapList(r)
  },

  async createPlan(payload: {
    name: string
    fiscal_year: number
    period_start: string
    period_end: string
    owner_user: string
    description?: string
  }): Promise<HRStrategicPlan> {
    const r = await apiClient.post<ApiEnvelope<HRStrategicPlan>>(`${PLANS}/`, payload)
    return unwrapItem(r)
  },

  async activate(id: string): Promise<HRStrategicPlan> {
    const r = await apiClient.post<ApiEnvelope<HRStrategicPlan>>(`${PLANS}/${id}/activate/`)
    return unwrapItem(r)
  },

  async complete(id: string): Promise<HRStrategicPlan> {
    const r = await apiClient.post<ApiEnvelope<HRStrategicPlan>>(`${PLANS}/${id}/complete/`)
    return unwrapItem(r)
  },

  async archive(id: string): Promise<HRStrategicPlan> {
    const r = await apiClient.post<ApiEnvelope<HRStrategicPlan>>(`${PLANS}/${id}/archive/`)
    return unwrapItem(r)
  },

  async getProgress(id: string): Promise<PlanProgress> {
    const r = await apiClient.get<ApiEnvelope<PlanProgress>>(`${PLANS}/${id}/progress/`)
    return unwrapItem(r)
  },

  async listObjectives(planId?: string): Promise<StrategicObjective[]> {
    const url = planId ? `${OBJECTIVES}/?plan=${planId}&page_size=100` : `${OBJECTIVES}/?page_size=100`
    const r = await apiClient.get<ApiEnvelope<StrategicObjective>>(url)
    return unwrapList(r)
  },

  async createObjective(payload: {
    plan: string
    code: string
    title: string
    weight: string
    description?: string
    order?: number
  }): Promise<StrategicObjective> {
    const r = await apiClient.post<ApiEnvelope<StrategicObjective>>(`${OBJECTIVES}/`, payload)
    return unwrapItem(r)
  },

  async listKpis(objectiveId?: string): Promise<KPI[]> {
    const url = objectiveId
      ? `${KPIS}/?objective=${objectiveId}&page_size=100`
      : `${KPIS}/?page_size=100`
    const r = await apiClient.get<ApiEnvelope<KPI>>(url)
    return unwrapList(r)
  },

  async createKpi(payload: {
    objective: string
    name: string
    target: string
    unit?: string
    formula_note?: string
    target_date?: string | null
  }): Promise<KPI> {
    const r = await apiClient.post<ApiEnvelope<KPI>>(`${KPIS}/`, payload)
    return unwrapItem(r)
  },

  async updateKpiActual(id: string, actual: string, statusOverride?: KPIStatus): Promise<KPI> {
    const r = await apiClient.post<ApiEnvelope<KPI>>(`${KPIS}/${id}/update-actual/`, {
      actual,
      ...(statusOverride ? { status: statusOverride } : {}),
    })
    return unwrapItem(r)
  },
}
