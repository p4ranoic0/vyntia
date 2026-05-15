import { apiClient } from '@/shared/api/api'

/**
 * hiringBundleService — frontend client for B.10 HiringDocumentBundle
 * (Module 03.2 documentos obligatorios vinculación).
 *
 * Routes at /api/v1/documents/hiring-bundles/ and /hiring-bundle-items/.
 */

export type BundleStatus = 'draft' | 'sent' | 'acknowledged'

export type BundleItemKind =
  | 'contrato'
  | 'rit'
  | 'reglamento_sst'
  | 'codigo_etica'
  | 'politica_datos'
  | 'manual_funciones'
  | 'otro'

export interface HiringBundleItem {
  id: string
  bundle: string
  kind: BundleItemKind
  kind_display: string
  document: string | null
  signature: string | null
  required: boolean
  order: number
}

export interface HiringDocumentBundle {
  id: string
  tenant?: string | null
  employee: string
  contract: string | null
  title: string
  status: BundleStatus
  status_display: string
  sent_at: string | null
  acknowledged_at: string | null
  created_by: string | null
  created_at: string
  updated_at: string
  items: HiringBundleItem[]
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

const BUNDLES_BASE = '/api/v1/documents/hiring-bundles'
const ITEMS_BASE = '/api/v1/documents/hiring-bundle-items'

export const hiringBundleService = {
  async listBundles(): Promise<HiringDocumentBundle[]> {
    const r = await apiClient.get<PaginatedResponse<HiringDocumentBundle>>(
      `${BUNDLES_BASE}/?page_size=100`,
    )
    return unwrapList(r)
  },

  async getBundle(id: string): Promise<HiringDocumentBundle> {
    const r = await apiClient.get<PaginatedResponse<HiringDocumentBundle>>(
      `${BUNDLES_BASE}/${id}/`,
    )
    return unwrapItem<HiringDocumentBundle>(r)
  },

  async createBundle(payload: {
    employee: string
    contract?: string | null
    title?: string
    item_kinds?: BundleItemKind[]
  }): Promise<HiringDocumentBundle> {
    const r = await apiClient.post<PaginatedResponse<HiringDocumentBundle>>(
      `${BUNDLES_BASE}/`,
      payload,
    )
    return unwrapItem<HiringDocumentBundle>(r)
  },

  async send(id: string): Promise<HiringDocumentBundle> {
    const r = await apiClient.post<PaginatedResponse<HiringDocumentBundle>>(
      `${BUNDLES_BASE}/${id}/send/`,
    )
    return unwrapItem<HiringDocumentBundle>(r)
  },

  async acknowledge(id: string): Promise<HiringDocumentBundle> {
    const r = await apiClient.post<PaginatedResponse<HiringDocumentBundle>>(
      `${BUNDLES_BASE}/${id}/acknowledge/`,
    )
    return unwrapItem<HiringDocumentBundle>(r)
  },

  async listItems(bundleId?: string): Promise<HiringBundleItem[]> {
    const query = bundleId ? `?bundle=${bundleId}` : ''
    const r = await apiClient.get<PaginatedResponse<HiringBundleItem>>(
      `${ITEMS_BASE}/${query}`,
    )
    return unwrapList(r)
  },

  async attachDocument(
    itemId: string,
    documentId: string,
  ): Promise<HiringBundleItem> {
    const r = await apiClient.post<PaginatedResponse<HiringBundleItem>>(
      `${ITEMS_BASE}/${itemId}/attach-document/`,
      { document_id: documentId },
    )
    return unwrapItem<HiringBundleItem>(r)
  },

  async attachAcuse(
    itemId: string,
    signatureId: string,
  ): Promise<HiringBundleItem> {
    const r = await apiClient.post<PaginatedResponse<HiringBundleItem>>(
      `${ITEMS_BASE}/${itemId}/attach-acuse/`,
      { signature_id: signatureId },
    )
    return unwrapItem<HiringBundleItem>(r)
  },
}
