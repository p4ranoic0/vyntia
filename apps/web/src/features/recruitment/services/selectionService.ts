import { apiClient } from '@/shared/api/api'

/**
 * selectionService — frontend client for B.9 Selección (Module 03.1).
 * Covers PersonnelRequisition → JobPosting → JobApplication →
 * CandidateEvaluation → MeritRanking flow plus Candidate + SelectionStage.
 *
 * Routes are flat under /api/v1/ (matches employees-app convention).
 */

export type RegisterDocType = 'dni' | 'ce' | 'passport' | 'ptp'

export type RequisitionStatus =
  | 'draft'
  | 'pending_approval'
  | 'approved'
  | 'rejected'
  | 'cancelled'
  | 'fulfilled'

export type JustificationKind =
  | 'new_position'
  | 'replacement'
  | 'expansion'
  | 'temporary'

export type SectorMode = 'private' | 'public_servir'

export type PostingKind = 'internal' | 'external' | 'mixed'

export type PostingStatus =
  | 'draft'
  | 'published'
  | 'in_evaluation'
  | 'closed'
  | 'cancelled'
  | 'declared_void'

export type StageKind =
  | 'curricular'
  | 'knowledge'
  | 'psycho'
  | 'interview'
  | 'technical'
  | 'reference'
  | 'other'

export type ApplicationStatus =
  | 'received'
  | 'reviewing'
  | 'in_evaluation'
  | 'eliminated'
  | 'finalist'
  | 'offered'
  | 'accepted'
  | 'hired'
  | 'rejected'
  | 'withdrawn'

export type RankingOutcome = 'winner' | 'waiting_list' | 'eliminated'

export interface Candidate {
  id: string
  tenant?: string | null
  document_type: RegisterDocType
  document_number: string
  first_names: string
  last_names: string
  full_name?: string
  birth_date?: string | null
  gender?: 'M' | 'F' | 'X' | ''
  email: string
  phone?: string
  address?: string
  years_experience: number
  highest_education?: string
  cv_file?: string | null
  source?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PersonnelRequisition {
  id: string
  tenant?: string | null
  code?: string
  position: string
  position_name?: string
  plaza?: string | null
  department: string
  department_name?: string
  justification: JustificationKind
  justification_display?: string
  justification_notes?: string
  requested_count: number
  requested_start_date?: string | null
  estimated_monthly_cost?: string | null
  status: RequisitionStatus
  status_display?: string
  requested_by: string
  approved_by_hr?: string | null
  approved_by_finance?: string | null
  approved_at?: string | null
  rejected_by?: string | null
  rejected_at?: string | null
  rejected_reason?: string
  is_fully_approved?: boolean
  created_at: string
  updated_at: string
}

export interface JobPosting {
  id: string
  tenant?: string | null
  requisition: string
  code?: string
  title: string
  summary?: string
  sector_mode: SectorMode
  sector_mode_display?: string
  posting_kind: PostingKind
  posting_kind_display?: string
  status: PostingStatus
  status_display?: string
  published_at?: string | null
  applications_open_at?: string | null
  applications_close_at?: string | null
  results_announce_at?: string | null
  bases_url?: string
  bases_file?: string | null
  cpe_entry?: string | null
  transparency_published: boolean
  closed_reason?: string
  application_count?: number
  created_at: string
  updated_at: string
  created_by?: string | null
}

export interface SelectionStage {
  id: string
  posting: string
  kind: StageKind
  kind_display?: string
  name: string
  order: number
  is_eliminatoria: boolean
  min_score: string
  max_score: string
  weight: string
  description?: string
  created_at: string
  updated_at: string
}

export interface JobApplication {
  id: string
  tenant?: string | null
  posting: string
  posting_title?: string
  candidate: string
  candidate_name?: string
  status: ApplicationStatus
  status_display?: string
  applied_at: string
  eliminated_at_stage?: string | null
  elimination_reason?: string
  withdrawn_at?: string | null
  cover_letter?: string
  custom_cv_file?: string | null
  created_at: string
  updated_at: string
}

export interface CandidateEvaluation {
  id: string
  application: string
  candidate_name?: string
  stage: string
  stage_name?: string
  evaluator: string
  score: string
  passed: boolean
  notes?: string
  evaluated_at: string
  updated_at: string
}

export interface MeritRanking {
  id: string
  posting: string
  application: string
  candidate_name?: string
  rank: number
  total_score: string
  outcome: RankingOutcome
  outcome_display?: string
  score_breakdown: Record<string, {
    name: string
    order: number
    score: string
    weight: string
    weighted: string
    passed: boolean | null
  }>
  snapshot_at: string
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

export const selectionService = {
  // Candidates
  async listCandidates(): Promise<Candidate[]> {
    const r = await apiClient.get<PaginatedResponse<Candidate>>(
      '/api/v1/candidates/?page_size=200',
    )
    return unwrapList(r)
  },

  async createCandidate(payload: Partial<Candidate>): Promise<Candidate> {
    const r = await apiClient.post<PaginatedResponse<Candidate>>(
      '/api/v1/candidates/',
      payload,
    )
    return unwrapItem<Candidate>(r)
  },

  // Requisitions
  async listRequisitions(): Promise<PersonnelRequisition[]> {
    const r = await apiClient.get<PaginatedResponse<PersonnelRequisition>>(
      '/api/v1/personnel-requisitions/?page_size=100',
    )
    return unwrapList(r)
  },

  async getRequisition(id: string): Promise<PersonnelRequisition> {
    const r = await apiClient.get<PaginatedResponse<PersonnelRequisition>>(
      `/api/v1/personnel-requisitions/${id}/`,
    )
    return unwrapItem<PersonnelRequisition>(r)
  },

  async createRequisition(
    payload: Partial<PersonnelRequisition>,
  ): Promise<PersonnelRequisition> {
    const r = await apiClient.post<PaginatedResponse<PersonnelRequisition>>(
      '/api/v1/personnel-requisitions/',
      payload,
    )
    return unwrapItem<PersonnelRequisition>(r)
  },

  async submitRequisition(id: string): Promise<PersonnelRequisition> {
    const r = await apiClient.post<PaginatedResponse<PersonnelRequisition>>(
      `/api/v1/personnel-requisitions/${id}/submit/`,
      {},
    )
    return unwrapItem<PersonnelRequisition>(r)
  },

  async approveHR(id: string): Promise<PersonnelRequisition> {
    const r = await apiClient.post<PaginatedResponse<PersonnelRequisition>>(
      `/api/v1/personnel-requisitions/${id}/approve-hr/`,
      {},
    )
    return unwrapItem<PersonnelRequisition>(r)
  },

  async approveFinance(id: string): Promise<PersonnelRequisition> {
    const r = await apiClient.post<PaginatedResponse<PersonnelRequisition>>(
      `/api/v1/personnel-requisitions/${id}/approve-finance/`,
      {},
    )
    return unwrapItem<PersonnelRequisition>(r)
  },

  async rejectRequisition(id: string, reason: string): Promise<PersonnelRequisition> {
    const r = await apiClient.post<PaginatedResponse<PersonnelRequisition>>(
      `/api/v1/personnel-requisitions/${id}/reject/`,
      { reason },
    )
    return unwrapItem<PersonnelRequisition>(r)
  },

  async cancelRequisition(id: string): Promise<PersonnelRequisition> {
    const r = await apiClient.post<PaginatedResponse<PersonnelRequisition>>(
      `/api/v1/personnel-requisitions/${id}/cancel/`,
      {},
    )
    return unwrapItem<PersonnelRequisition>(r)
  },

  // Postings
  async listPostings(requisitionId?: string): Promise<JobPosting[]> {
    const qs = new URLSearchParams({ page_size: '100' })
    if (requisitionId) qs.set('requisition', requisitionId)
    const r = await apiClient.get<PaginatedResponse<JobPosting>>(
      `/api/v1/job-postings/?${qs.toString()}`,
    )
    return unwrapList(r)
  },

  async getPosting(id: string): Promise<JobPosting> {
    const r = await apiClient.get<PaginatedResponse<JobPosting>>(
      `/api/v1/job-postings/${id}/`,
    )
    return unwrapItem<JobPosting>(r)
  },

  async createPosting(payload: Partial<JobPosting>): Promise<JobPosting> {
    const r = await apiClient.post<PaginatedResponse<JobPosting>>(
      '/api/v1/job-postings/',
      payload,
    )
    return unwrapItem<JobPosting>(r)
  },

  async publishPosting(id: string): Promise<JobPosting> {
    const r = await apiClient.post<PaginatedResponse<JobPosting>>(
      `/api/v1/job-postings/${id}/publish/`,
      {},
    )
    return unwrapItem<JobPosting>(r)
  },

  async closePosting(id: string, reason?: string): Promise<JobPosting> {
    const r = await apiClient.post<PaginatedResponse<JobPosting>>(
      `/api/v1/job-postings/${id}/close/`,
      reason ? { reason } : {},
    )
    return unwrapItem<JobPosting>(r)
  },

  async declareVoid(id: string, reason: string): Promise<JobPosting> {
    const r = await apiClient.post<PaginatedResponse<JobPosting>>(
      `/api/v1/job-postings/${id}/declare-void/`,
      { reason },
    )
    return unwrapItem<JobPosting>(r)
  },

  async computeRanking(postingId: string): Promise<MeritRanking[]> {
    const r = await apiClient.post<PaginatedResponse<MeritRanking>>(
      `/api/v1/job-postings/${postingId}/compute-ranking/`,
      {},
    )
    return unwrapList(r)
  },

  // Stages
  async listStages(postingId: string): Promise<SelectionStage[]> {
    const r = await apiClient.get<PaginatedResponse<SelectionStage>>(
      `/api/v1/selection-stages/?posting=${postingId}&page_size=50`,
    )
    return unwrapList(r)
  },

  async upsertStage(payload: Partial<SelectionStage> & { id?: string }):
    Promise<SelectionStage> {
    if (payload.id) {
      const r = await apiClient.patch<PaginatedResponse<SelectionStage>>(
        `/api/v1/selection-stages/${payload.id}/`,
        payload,
      )
      return unwrapItem<SelectionStage>(r)
    }
    const r = await apiClient.post<PaginatedResponse<SelectionStage>>(
      '/api/v1/selection-stages/',
      payload,
    )
    return unwrapItem<SelectionStage>(r)
  },

  // Applications
  async listApplications(postingId: string): Promise<JobApplication[]> {
    const r = await apiClient.get<PaginatedResponse<JobApplication>>(
      `/api/v1/job-applications/?posting=${postingId}&page_size=200`,
    )
    return unwrapList(r)
  },

  async createApplication(
    payload: { posting: string; candidate: string; cover_letter?: string },
  ): Promise<JobApplication> {
    const r = await apiClient.post<PaginatedResponse<JobApplication>>(
      '/api/v1/job-applications/',
      payload,
    )
    return unwrapItem<JobApplication>(r)
  },

  async advanceApplication(
    id: string, newStatus: ApplicationStatus,
  ): Promise<JobApplication> {
    const r = await apiClient.post<PaginatedResponse<JobApplication>>(
      `/api/v1/job-applications/${id}/advance-to/`,
      { new_status: newStatus },
    )
    return unwrapItem<JobApplication>(r)
  },

  async eliminateApplication(
    id: string, payload: { stage?: string; reason?: string } = {},
  ): Promise<JobApplication> {
    const r = await apiClient.post<PaginatedResponse<JobApplication>>(
      `/api/v1/job-applications/${id}/eliminate/`,
      payload,
    )
    return unwrapItem<JobApplication>(r)
  },

  // Evaluations
  async listEvaluations(applicationId: string): Promise<CandidateEvaluation[]> {
    const r = await apiClient.get<PaginatedResponse<CandidateEvaluation>>(
      `/api/v1/candidate-evaluations/?application=${applicationId}&page_size=50`,
    )
    return unwrapList(r)
  },

  async upsertEvaluation(
    payload: Partial<CandidateEvaluation> & {
      application: string; stage: string; score: string; id?: string;
    },
  ): Promise<CandidateEvaluation> {
    if (payload.id) {
      const r = await apiClient.patch<PaginatedResponse<CandidateEvaluation>>(
        `/api/v1/candidate-evaluations/${payload.id}/`,
        payload,
      )
      return unwrapItem<CandidateEvaluation>(r)
    }
    const r = await apiClient.post<PaginatedResponse<CandidateEvaluation>>(
      '/api/v1/candidate-evaluations/',
      payload,
    )
    return unwrapItem<CandidateEvaluation>(r)
  },

  // Rankings
  async listRanking(postingId: string): Promise<MeritRanking[]> {
    const r = await apiClient.get<PaginatedResponse<MeritRanking>>(
      `/api/v1/merit-rankings/?posting=${postingId}&page_size=200`,
    )
    return unwrapList(r)
  },
}
