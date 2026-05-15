import { apiClient } from '@/shared/api/api'

/**
 * documentSignatureService — frontend client for B.10 DocumentSignature
 * (Module 03.2 e-firma).
 *
 * Routes at /api/v1/documents/signatures/.
 */

export type SignatureKind = 'canvas' | 'typed' | 'checkbox'

export type SignatureStatus = 'requested' | 'signed' | 'rejected' | 'expired'

export interface DocumentSignature {
  id: string
  tenant?: string | null
  document: string
  signer_user: string | null
  signer_name: string
  signer_doc_number: string
  signer_email: string
  kind: SignatureKind
  kind_display: string
  status: SignatureStatus
  status_display: string
  canvas_base64: string
  typed_name: string
  checkbox_text: string
  requested_at: string
  expires_at: string | null
  signed_at: string | null
  rejection_reason: string
  signer_ip: string | null
  signer_user_agent: string
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

const BASE = '/api/v1/documents/signatures'

export const documentSignatureService = {
  async list(): Promise<DocumentSignature[]> {
    const r = await apiClient.get<PaginatedResponse<DocumentSignature>>(
      `${BASE}/?page_size=100`,
    )
    return unwrapList(r)
  },

  async get(id: string): Promise<DocumentSignature> {
    const r = await apiClient.get<PaginatedResponse<DocumentSignature>>(
      `${BASE}/${id}/`,
    )
    return unwrapItem<DocumentSignature>(r)
  },

  async create(
    payload: Partial<DocumentSignature>,
  ): Promise<DocumentSignature> {
    const r = await apiClient.post<PaginatedResponse<DocumentSignature>>(
      `${BASE}/`,
      payload,
    )
    return unwrapItem<DocumentSignature>(r)
  },

  async capture(
    id: string,
    payload: {
      canvas_base64?: string
      typed_name?: string
      checkbox_text?: string
    },
  ): Promise<DocumentSignature> {
    const r = await apiClient.post<PaginatedResponse<DocumentSignature>>(
      `${BASE}/${id}/capture/`,
      payload,
    )
    return unwrapItem<DocumentSignature>(r)
  },

  async reject(id: string, reason: string): Promise<DocumentSignature> {
    const r = await apiClient.post<PaginatedResponse<DocumentSignature>>(
      `${BASE}/${id}/reject/`,
      { reason },
    )
    return unwrapItem<DocumentSignature>(r)
  },

  async expireOverdue(): Promise<{ expired_count: number }> {
    const r = await apiClient.post<
      PaginatedResponse<{ expired_count: number }>
    >(`${BASE}/expire-overdue/`)
    return unwrapItem<{ expired_count: number }>(r)
  },
}
