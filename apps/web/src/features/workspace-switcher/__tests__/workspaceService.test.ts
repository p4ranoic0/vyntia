import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/shared/api/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

import { apiClient } from '@/shared/api/api'
import {
  exchangeWorkspace,
  fetchWorkspaces,
} from '../services/workspaceService'

describe('workspaceService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('fetchWorkspaces unwraps standard response shape', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        success: true,
        message: 'ok',
        data: [
          { tenant_id: 't1', slug: 'acme', name: 'Acme', plan: 'starter', role: 'admin' },
        ],
      },
    } as any)
    const workspaces = await fetchWorkspaces()
    expect(workspaces).toHaveLength(1)
    expect(workspaces[0].slug).toBe('acme')
    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/workspaces/')
  })

  it('fetchWorkspaces returns empty array on missing data', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: {} } as any)
    expect(await fetchWorkspaces()).toEqual([])
  })

  it('exchangeWorkspace POSTs and returns redirect_url', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: {
        success: true,
        data: {
          exchange_token: 'token-xyz',
          redirect_url: 'https://acme.vyntia.pe/auth/exchange?token=token-xyz',
        },
      },
    } as any)
    const result = await exchangeWorkspace('acme')
    expect(result.redirect_url).toContain('acme.vyntia.pe')
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/workspaces/acme/exchange/')
  })
})
