import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/shared/api/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}))

import { apiClient } from '@/shared/api/api'
import {
  fetchTenants,
  createTenant,
  suspendTenant,
} from '../services/tenantsAdminService'

describe('tenantsAdminService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('fetchTenants passes pagination params', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        data: {
          results: [],
          pagination: { total_items: 0, current_page: 1, page_size: 25, total_pages: 0 },
        },
      },
    } as any)
    await fetchTenants(2, 50)
    expect(apiClient.get).toHaveBeenCalledWith('/api/admin/tenants/', {
      page: 2,
      page_size: 50,
    })
  })

  it('createTenant POSTs payload', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { tenant: { slug: 'x' }, invitation: {} } },
    } as any)
    await createTenant({
      slug: 'x',
      name: 'X',
      ruc: '20999999999',
      plan: 'starter',
      trial_days: 30,
      admin_email: 'a@b.c',
      admin_name: 'A',
    })
    expect(apiClient.post).toHaveBeenCalledWith(
      '/api/admin/tenants/',
      expect.objectContaining({ slug: 'x', plan: 'starter' }),
    )
  })

  it('suspendTenant POSTs to suspend endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { data: {} } } as any)
    await suspendTenant('abc-123')
    expect(apiClient.post).toHaveBeenCalledWith('/api/admin/tenants/abc-123/suspend/')
  })
})
