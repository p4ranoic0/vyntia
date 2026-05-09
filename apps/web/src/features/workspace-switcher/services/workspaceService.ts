import { apiClient } from '@/shared/api/api'

export interface Workspace {
  tenant_id: string
  slug: string
  name: string
  plan: string
  role: string
}

export interface ExchangeResponse {
  exchange_token: string
  redirect_url: string
}

/**
 * GET /api/v1/workspaces/ — list the user's active TenantMemberships.
 */
export async function fetchWorkspaces(): Promise<Workspace[]> {
  const response = await apiClient.get('/api/v1/workspaces/')
  // Standard wrapper unwrap: { success, message, data: Workspace[] }
  return response.data?.data ?? []
}

/**
 * POST /api/v1/workspaces/<slug>/exchange/ — get a short-lived token to
 * jump to <slug>.vyntia.pe.
 */
export async function exchangeWorkspace(slug: string): Promise<ExchangeResponse> {
  const response = await apiClient.post(`/api/v1/workspaces/${slug}/exchange/`)
  return response.data?.data ?? { exchange_token: '', redirect_url: '' }
}
