import { apiClient } from '@/shared/api/api'

/**
 * policiesService — frontend client for B.15a Policies (Module 01).
 *
 * Routes flat at /api/v1/:
 * - /policies/
 * - /policy-versions/
 * - /policy-approval-flows/
 * - /policy-publications/
 * - /policy-acknowledgments/
 */

export type PolicyKind =
  | 'rit'
  | 'codigo_etica'
  | 'reglamento_sst'
  | 'politica_datos'
  | 'manual_funciones'
  | 'procedimiento'
  | 'otro'

export type PolicyStatus =
  | 'draft'
  | 'in_review'
  | 'approved'
  | 'published'
  | 'retired'

export type PolicyVersionStatus =
  | 'draft'
  | 'under_review'
  | 'approved'
  | 'published'
  | 'retired'

export type FlowStatus = 'pending' | 'approved' | 'rejected'
export type StepDecision = 'pending' | 'approved' | 'rejected'

export type TargetAudience = 'all' | 'role' | 'area' | 'employee'

export type SignatureKind = 'canvas' | 'typed' | 'checkbox' | 'none'

export type AcknowledgmentStatus =
  | 'pending'
  | 'acknowledged'
  | 'expired'
  | 'declined'

export interface Policy {
  id: string
  tenant?: string | null
  kind: PolicyKind
  kind_display: string
  title: string
  description: string
  owner_user: string
  owner_area: string | null
  status: PolicyStatus
  status_display: string
  current_version: string | null
  created_at: string
  updated_at: string
  created_by: string | null
  updated_by: string | null
}

export interface PolicyVersion {
  id: string
  tenant?: string | null
  policy: string
  version_number: number
  content_html: string
  pdf_file: string | null
  change_summary: string
  effective_date: string | null
  status: PolicyVersionStatus
  status_display: string
  submitted_at: string | null
  submitted_by: string | null
  approved_at: string | null
  published_at: string | null
  retired_at: string | null
  created_at: string
  updated_at: string
  created_by: string | null
}

export interface PolicyApprovalStep {
  id: string
  flow: string
  order: number
  approver_user: string
  role_hint: string
  decision: StepDecision
  decision_display: string
  decided_at: string | null
  decided_by: string | null
  comment: string
  created_at: string
}

export interface PolicyApprovalFlow {
  id: string
  tenant?: string | null
  policy_version: string
  status: FlowStatus
  status_display: string
  created_at: string
  completed_at: string | null
  steps: PolicyApprovalStep[]
}

export interface PolicyPublication {
  id: string
  tenant?: string | null
  policy_version: string
  published_at: string
  published_by: string
  target_audience: TargetAudience
  target_audience_display: string
  target_role: string | null
  target_area: string | null
  target_employees: string[]
  requires_acknowledgment: boolean
  acknowledgment_deadline: string | null
  notification_sent: boolean
  created_at: string
  updated_at: string
}

export interface PolicyAcknowledgment {
  id: string
  tenant?: string | null
  publication: string
  employee: string
  status: AcknowledgmentStatus
  status_display: string
  acknowledged_at: string | null
  signature_kind: SignatureKind | ''
  signature_kind_display: string
  signature_payload: string
  ip: string | null
  user_agent: string
  declined_reason: string
  created_at: string
  updated_at: string
}

interface ApiEnvelope<T> {
  success?: boolean
  message?: string
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

const POLICIES = '/api/v1/policies'
const VERSIONS = '/api/v1/policy-versions'
const FLOWS = '/api/v1/policy-approval-flows'
const PUBS = '/api/v1/policy-publications'
const ACKS = '/api/v1/policy-acknowledgments'

export const policiesService = {
  // ----- Policies -----
  async listPolicies(): Promise<Policy[]> {
    const r = await apiClient.get<ApiEnvelope<Policy>>(`${POLICIES}/?page_size=100`)
    return unwrapList(r)
  },

  async getPolicy(id: string): Promise<Policy> {
    const r = await apiClient.get<ApiEnvelope<Policy>>(`${POLICIES}/${id}/`)
    return unwrapItem(r)
  },

  async createPolicy(payload: {
    kind: PolicyKind
    title: string
    description?: string
    owner_user: string
    owner_area?: string | null
  }): Promise<Policy> {
    const r = await apiClient.post<ApiEnvelope<Policy>>(`${POLICIES}/`, payload)
    return unwrapItem(r)
  },

  async retirePolicy(id: string): Promise<Policy> {
    const r = await apiClient.post<ApiEnvelope<Policy>>(`${POLICIES}/${id}/retire/`)
    return unwrapItem(r)
  },

  // ----- Versions -----
  async listVersions(policyId?: string): Promise<PolicyVersion[]> {
    const url = policyId
      ? `${VERSIONS}/?policy=${policyId}&page_size=100`
      : `${VERSIONS}/?page_size=100`
    const r = await apiClient.get<ApiEnvelope<PolicyVersion>>(url)
    return unwrapList(r)
  },

  async createVersion(payload: {
    policy: string
    content_html?: string
    change_summary?: string
    effective_date?: string | null
  }): Promise<PolicyVersion> {
    const r = await apiClient.post<ApiEnvelope<PolicyVersion>>(
      `${VERSIONS}/`, payload,
    )
    return unwrapItem(r)
  },

  async submitForReview(versionId: string, approvers: string[]): Promise<PolicyApprovalFlow> {
    const r = await apiClient.post<ApiEnvelope<PolicyApprovalFlow>>(
      `${VERSIONS}/${versionId}/submit-for-review/`,
      { approvers },
    )
    return unwrapItem(r)
  },

  async publishVersion(
    versionId: string,
    payload: {
      target_audience: TargetAudience
      target_role?: string | null
      target_area?: string | null
      target_employees?: string[]
      requires_acknowledgment?: boolean
      deadline?: string | null
    },
  ): Promise<PolicyPublication> {
    const r = await apiClient.post<ApiEnvelope<PolicyPublication>>(
      `${VERSIONS}/${versionId}/publish/`, payload,
    )
    return unwrapItem(r)
  },

  // ----- Approval flows -----
  async listApprovalFlows(): Promise<PolicyApprovalFlow[]> {
    const r = await apiClient.get<ApiEnvelope<PolicyApprovalFlow>>(
      `${FLOWS}/?page_size=100`,
    )
    return unwrapList(r)
  },

  async decideStep(
    flowId: string,
    payload: { step_order: number; decision: 'approved' | 'rejected'; comment?: string },
  ): Promise<{ step: PolicyApprovalStep; flow: PolicyApprovalFlow }> {
    const r = await apiClient.post<
      ApiEnvelope<{ step: PolicyApprovalStep; flow: PolicyApprovalFlow }>
    >(`${FLOWS}/${flowId}/decide/`, payload)
    return unwrapItem(r)
  },

  // ----- Publications -----
  async listPublications(): Promise<PolicyPublication[]> {
    const r = await apiClient.get<ApiEnvelope<PolicyPublication>>(
      `${PUBS}/?page_size=100`,
    )
    return unwrapList(r)
  },

  async seedAcknowledgments(publicationId: string): Promise<{ created: number }> {
    const r = await apiClient.post<ApiEnvelope<{ created: number }>>(
      `${PUBS}/${publicationId}/seed-acknowledgments/`,
    )
    return unwrapItem(r)
  },

  // ----- Acknowledgments -----
  async listAcknowledgments(filters?: {
    publication?: string
    employee?: string
    status?: AcknowledgmentStatus
  }): Promise<PolicyAcknowledgment[]> {
    const qs = filters
      ? '?' +
        new URLSearchParams(
          Object.fromEntries(
            Object.entries(filters).filter(([, v]) => v !== undefined && v !== ''),
          ) as Record<string, string>,
        ).toString() +
        '&page_size=100'
      : '?page_size=100'
    const r = await apiClient.get<ApiEnvelope<PolicyAcknowledgment>>(`${ACKS}/${qs}`)
    return unwrapList(r)
  },

  async acknowledge(
    ackId: string,
    payload: { signature_kind: SignatureKind; signature_payload?: string },
  ): Promise<PolicyAcknowledgment> {
    const r = await apiClient.post<ApiEnvelope<PolicyAcknowledgment>>(
      `${ACKS}/${ackId}/acknowledge/`, payload,
    )
    return unwrapItem(r)
  },

  async decline(ackId: string, reason: string): Promise<PolicyAcknowledgment> {
    const r = await apiClient.post<ApiEnvelope<PolicyAcknowledgment>>(
      `${ACKS}/${ackId}/decline/`, { reason },
    )
    return unwrapItem(r)
  },

  async expireOverdue(): Promise<{ expired: number }> {
    const r = await apiClient.post<ApiEnvelope<{ expired: number }>>(
      `${ACKS}/expire-overdue/`,
    )
    return unwrapItem(r)
  },
}
