import { describe, expect, it, vi, beforeEach } from 'vitest'

vi.mock('@/shared/api/api', () => ({
  apiClient: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { apiClient } from '@/shared/api/api'
import { workforcePlanService } from '../workforcePlanService'

describe('workforcePlanService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('listPlans hits workforce-plans', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await workforcePlanService.listPlans()
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain('/api/v1/workforce-plans/')
  })

  it('createPlan POSTs', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'wp1' } },
    } as never)
    await workforcePlanService.createPlan({
      name: 'D', fiscal_year: 2026,
      period_start: '2026-01-01', period_end: '2026-12-31',
      owner_user: 'u1',
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe('/api/v1/workforce-plans/')
  })

  it('listProjections filter by plan', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await workforcePlanService.listProjections('wp1')
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain('plan=wp1')
  })

  it('createKeyPosition POSTs to key-positions', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'kp1' } },
    } as never)
    await workforcePlanService.createKeyPosition({
      plan: 'sp1', position: 'pos1', criticality: 'alta',
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe('/api/v1/key-positions/')
  })

  it('createCandidate POSTs to successor-candidates', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'c1' } },
    } as never)
    await workforcePlanService.createCandidate({
      key_position: 'kp1', employee: 'e1', readiness_level: 1,
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe('/api/v1/successor-candidates/')
  })

  it('createSuccessionPlan POSTs', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'sp1' } },
    } as never)
    await workforcePlanService.createSuccessionPlan({
      name: 'S', fiscal_year: 2026, owner_user: 'u1',
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe('/api/v1/succession-plans/')
  })
})
