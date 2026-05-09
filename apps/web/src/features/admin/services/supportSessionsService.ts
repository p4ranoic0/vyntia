import { apiClient } from '@/shared/api/api'

export interface SupportSession {
  id: string
  staff_user: string
  target_user: string
  tenant_slug: string
  reason: string
  started_at: string
  expires_at: string
  ended_at: string | null
  actions_count: number
}

export interface PaginatedSessions {
  results: SupportSession[]
  pagination: {
    total_items: number
    current_page: number
    page_size: number
    total_pages: number
  }
}

export async function fetchSupportSessions(page = 1, pageSize = 25): Promise<PaginatedSessions> {
  const response = await apiClient.get<{ data: PaginatedSessions }>('/api/admin/support-sessions/', {
    page,
    page_size: pageSize,
  })
  return response.data?.data
}
