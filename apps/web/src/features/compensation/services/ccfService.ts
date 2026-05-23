import { apiClient } from '@/shared/api/api'
import { unwrapBlobError } from '@/shared/api/blob'

/** Job factor reference data (R.M. 243-2018-TR). System-wide. */
export interface JobFactor {
  id: string
  kind: 'competencias' | 'responsabilidad' | 'esfuerzo' | 'condiciones'
  name: string
  description?: string
  weight: string  // decimal as string from DRF
  is_active: boolean
}

export interface JobSubfactor {
  id: string
  factor: string
  factor_name?: string
  factor_kind?: string
  code: string
  name: string
  description?: string
  max_score: number
  is_active: boolean
}

/** Cuadro de Categorías y Funciones (CCF) — Ley 30709. */
export interface CCF {
  id: string
  tenant?: string | null
  title: string
  description?: string
  version: number
  parent_version?: string | null
  status: 'draft' | 'approved' | 'superseded' | 'archived'
  status_display: string
  effective_date?: string | null
  approved_at?: string | null
  approved_by?: string | null
  category_count: number
  created_at: string
  updated_at: string
  created_by?: string | null
}

export interface Category {
  id: string
  tenant?: string | null
  ccf: string
  ccf_title?: string
  code: string
  name: string
  description?: string
  functions_summary?: string
  min_education?: string
  min_experience_years: number
  technical_competencies?: string[]
  soft_competencies?: string[]
  physical_conditions?: string
  total_score: string  // decimal
  is_active: boolean
  has_salary_band?: boolean
  created_at: string
  updated_at: string
}

export interface CategoryFactorScore {
  id: string
  category: string
  subfactor: string
  subfactor_code?: string
  subfactor_name?: string
  factor_kind?: string
  score: number
  notes?: string
  created_at: string
  updated_at: string
}

export interface SalaryBand {
  id: string
  category: string
  category_code?: string
  category_name?: string
  min_salary: string
  mid_salary: string
  max_salary: string
  currency: string
  placement_criteria?: string
  created_at: string
  updated_at: string
}

/** One row in the Ley 30709 § 8 salary-gap audit report. */
export interface SalaryGapRow {
  category_id: string
  category_code: string
  category_name: string
  group_male: { count: number; avg_salary: string }
  group_female: { count: number; avg_salary: string }
  brecha_pct: string
  alert: boolean
}

export interface SalaryGapSummary {
  total_categories: number
  alerted_categories: number
  total_male_employees: number
  total_female_employees: number
  overall_brecha_pct: string
}

export interface SalaryGapAudit {
  rows: SalaryGapRow[]
  summary: SalaryGapSummary
}

/** Outcome of an Excel CCF import. */
export interface CCFImportResult {
  success: boolean
  ccf_id?: string | null
  categories_created: number
  bands_created: number
  scores_created: number
  row_errors: Array<{ row: number; code?: string; error: string }>
  fatal_error?: string | null
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
  // APIResponse.success wraps payload in `data`; CRUD ViewSets return the bare object
  if (raw && typeof raw === 'object' && 'data' in raw && raw.data && typeof raw.data === 'object' && !Array.isArray(raw.data)) {
    return raw.data as T
  }
  return raw as unknown as T
}

export const ccfService = {
  // Reference data
  async listFactors(): Promise<JobFactor[]> {
    const r = await apiClient.get<PaginatedResponse<JobFactor>>(
      '/api/v1/compensation/job-factors/',
    )
    return unwrapList(r)
  },
  async listSubfactors(factorId?: string): Promise<JobSubfactor[]> {
    const qs = factorId ? `?factor=${factorId}` : ''
    const r = await apiClient.get<PaginatedResponse<JobSubfactor>>(
      `/api/v1/compensation/job-subfactors/${qs}`,
    )
    return unwrapList(r)
  },

  // CCF
  async listCCFs(): Promise<CCF[]> {
    const r = await apiClient.get<PaginatedResponse<CCF>>('/api/v1/compensation/ccfs/?page_size=100')
    return unwrapList(r)
  },
  async getCCF(id: string): Promise<CCF> {
    const r = await apiClient.get<PaginatedResponse<CCF>>(`/api/v1/compensation/ccfs/${id}/`)
    return unwrapItem<CCF>(r)
  },
  async createCCF(payload: Pick<CCF, 'title' | 'description'>): Promise<CCF> {
    const r = await apiClient.post<PaginatedResponse<CCF>>('/api/v1/compensation/ccfs/', payload)
    return unwrapItem<CCF>(r)
  },
  async approveCCF(id: string, effective_date?: string): Promise<CCF> {
    const r = await apiClient.post<PaginatedResponse<CCF>>(
      `/api/v1/compensation/ccfs/${id}/approve/`,
      effective_date ? { effective_date } : {},
    )
    return unwrapItem<CCF>(r)
  },

  // Categories
  async listCategories(ccfId?: string): Promise<Category[]> {
    const qs = new URLSearchParams({ page_size: '200' })
    if (ccfId) qs.set('ccf', ccfId)
    const r = await apiClient.get<PaginatedResponse<Category>>(
      `/api/v1/compensation/categories/?${qs.toString()}`,
    )
    return unwrapList(r)
  },
  async createCategory(payload: Partial<Category>): Promise<Category> {
    const r = await apiClient.post<PaginatedResponse<Category>>(
      '/api/v1/compensation/categories/',
      payload,
    )
    return unwrapItem<Category>(r)
  },
  async updateCategory(id: string, payload: Partial<Category>): Promise<Category> {
    const r = await apiClient.patch<PaginatedResponse<Category>>(
      `/api/v1/compensation/categories/${id}/`,
      payload,
    )
    return unwrapItem<Category>(r)
  },
  async recomputeTotal(id: string): Promise<{ total_score: string }> {
    const r = await apiClient.post<PaginatedResponse<{ total_score: string }>>(
      `/api/v1/compensation/categories/${id}/recompute-total/`,
      {},
    )
    return unwrapItem<{ total_score: string }>(r)
  },

  // Factor scores
  async listFactorScores(categoryId?: string): Promise<CategoryFactorScore[]> {
    const qs = categoryId ? `?category=${categoryId}` : ''
    const r = await apiClient.get<PaginatedResponse<CategoryFactorScore>>(
      `/api/v1/compensation/factor-scores/${qs}`,
    )
    return unwrapList(r)
  },
  async upsertFactorScore(payload: {
    id?: string
    category: string
    subfactor: string
    score: number
    notes?: string
  }): Promise<CategoryFactorScore> {
    if (payload.id) {
      const r = await apiClient.patch<PaginatedResponse<CategoryFactorScore>>(
        `/api/v1/compensation/factor-scores/${payload.id}/`,
        payload,
      )
      return unwrapItem<CategoryFactorScore>(r)
    }
    const r = await apiClient.post<PaginatedResponse<CategoryFactorScore>>(
      '/api/v1/compensation/factor-scores/',
      payload,
    )
    return unwrapItem<CategoryFactorScore>(r)
  },

  // Salary bands
  async listSalaryBands(categoryId?: string): Promise<SalaryBand[]> {
    const qs = categoryId ? `?category=${categoryId}` : ''
    const r = await apiClient.get<PaginatedResponse<SalaryBand>>(
      `/api/v1/compensation/salary-bands/${qs}`,
    )
    return unwrapList(r)
  },
  async upsertSalaryBand(payload: {
    id?: string
    category: string
    min_salary: string
    mid_salary: string
    max_salary: string
    currency?: string
    placement_criteria?: string
  }): Promise<SalaryBand> {
    if (payload.id) {
      const r = await apiClient.patch<PaginatedResponse<SalaryBand>>(
        `/api/v1/compensation/salary-bands/${payload.id}/`,
        payload,
      )
      return unwrapItem<SalaryBand>(r)
    }
    const r = await apiClient.post<PaginatedResponse<SalaryBand>>(
      '/api/v1/compensation/salary-bands/',
      payload,
    )
    return unwrapItem<SalaryBand>(r)
  },

  // Audit
  async getSalaryGapAudit(ccfId?: string): Promise<SalaryGapAudit> {
    const qs = ccfId ? `?ccf_id=${ccfId}` : ''
    const r = await apiClient.get<PaginatedResponse<SalaryGapAudit>>(
      `/api/v1/compensation/audit/salary-gap/${qs}`,
    )
    return unwrapItem<SalaryGapAudit>(r)
  },

  // Excel template + import
  async downloadTemplate(): Promise<Blob> {
    try {
      const r = await apiClient.get('/api/v1/compensation/ccf/template-excel/', {
        responseType: 'blob',
      })
      return r.data as Blob
    } catch (err) {
      throw await unwrapBlobError(err)
    }
  },
  async uploadCCFExcel(file: File, ccfTitle: string): Promise<CCFImportResult> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('ccf_title', ccfTitle)
    try {
      const r = await apiClient.post<{ data?: CCFImportResult } & CCFImportResult>(
        '/api/v1/compensation/ccf/import-excel/',
        formData,
      )
      const raw = r.data as { data?: CCFImportResult } & CCFImportResult
      return (raw?.data as CCFImportResult) ?? (raw as CCFImportResult)
    } catch (err: unknown) {
      // Backend returns 400 with payload when row errors — extract result
      const resp = (err as { response?: { data?: { data?: CCFImportResult } & CCFImportResult } })
        ?.response?.data
      if (resp) return (resp.data as CCFImportResult) ?? (resp as CCFImportResult)
      throw err
    }
  },
}
