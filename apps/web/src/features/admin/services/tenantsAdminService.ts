import { apiClient } from '@/shared/api/api'

export interface AdminTenant {
  id: string
  slug: string
  name: string
  ruc: string
  plan: 'starter' | 'pro' | 'enterprise' | 'govtech'
  status: 'trial' | 'active' | 'suspended' | 'cancelled'
  trial_ends_at: string | null
  max_users: number
  cancelled_at: string | null
  created_at: string
  updated_at: string
  member_count: number
}

export interface CreateTenantPayload {
  slug: string
  name: string
  ruc: string
  plan: AdminTenant['plan']
  trial_days: number
  admin_email: string
  admin_name: string
}

export interface CreateTenantResponse {
  tenant: AdminTenant
  invitation: {
    id: string
    email: string
    expires_at: string
    activation_url: string
  }
}

export interface PaginatedTenants {
  results: AdminTenant[]
  pagination: {
    total_items: number
    current_page: number
    page_size: number
    total_pages: number
  }
}

export async function fetchTenants(page = 1, pageSize = 25): Promise<PaginatedTenants> {
  const response = await apiClient.get<{ data: PaginatedTenants }>('/api/admin/tenants/', {
    page,
    page_size: pageSize,
  })
  return response.data?.data
}

export async function fetchTenant(id: string): Promise<AdminTenant> {
  const response = await apiClient.get<{ data: AdminTenant }>(`/api/admin/tenants/${id}/`)
  return response.data?.data
}

export async function createTenant(payload: CreateTenantPayload): Promise<CreateTenantResponse> {
  const response = await apiClient.post<{ data: CreateTenantResponse }>('/api/admin/tenants/', payload)
  return response.data?.data
}

export async function updateTenant(
  id: string,
  patch: Partial<Pick<AdminTenant, 'plan' | 'max_users' | 'trial_ends_at'>>,
): Promise<AdminTenant> {
  const response = await apiClient.patch<{ data: AdminTenant }>(`/api/admin/tenants/${id}/`, patch)
  return response.data?.data
}

export async function suspendTenant(id: string): Promise<AdminTenant> {
  const response = await apiClient.post<{ data: AdminTenant }>(`/api/admin/tenants/${id}/suspend/`)
  return response.data?.data
}

export async function cancelTenant(id: string): Promise<AdminTenant> {
  const response = await apiClient.post<{ data: AdminTenant }>(`/api/admin/tenants/${id}/cancel/`)
  return response.data?.data
}

export async function reinviteTenant(
  id: string,
  email: string,
  role: 'owner' | 'admin' | 'member' = 'owner',
): Promise<{ id: string; email: string; expires_at: string; activation_url: string }> {
  const response = await apiClient.post<{
    data: { id: string; email: string; expires_at: string; activation_url: string }
  }>(`/api/admin/tenants/${id}/invitations/`, { email, role })
  return response.data?.data
}
