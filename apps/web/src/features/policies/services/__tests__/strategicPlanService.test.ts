import { describe, expect, it, vi, beforeEach } from 'vitest'

vi.mock('@/shared/api/api', () => ({
  apiClient: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { apiClient } from '@/shared/api/api'
import { strategicPlanService } from '../strategicPlanService'

describe('strategicPlanService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('listPlans hits /api/v1/strategic-plans/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 'p1', name: 'Plan' }] } },
    } as never)
    const out = await strategicPlanService.listPlans()
    expect(out).toHaveLength(1)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain('/api/v1/strategic-plans/')
  })

  it('createPlan POSTs payload', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'p1' } },
    } as never)
    await strategicPlanService.createPlan({
      name: 'P', fiscal_year: 2026,
      period_start: '2026-01-01', period_end: '2026-12-31',
      owner_user: 'u1',
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe('/api/v1/strategic-plans/')
  })

  it('activate hits action endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'p1', status: 'active' } },
    } as never)
    await strategicPlanService.activate('p1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe('/api/v1/strategic-plans/p1/activate/')
  })

  it('getProgress hits progress endpoint', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { overall_pct: '80', objectives: [] } },
    } as never)
    const out = await strategicPlanService.getProgress('p1')
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toBe('/api/v1/strategic-plans/p1/progress/')
    expect(out.overall_pct).toBe('80')
  })

  it('createObjective hits objectives endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'o1' } },
    } as never)
    await strategicPlanService.createObjective({
      plan: 'p1', code: 'OE-01', title: 'X', weight: '50',
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe('/api/v1/strategic-objectives/')
  })

  it('updateKpiActual posts actual', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'k1', actual: '85' } },
    } as never)
    await strategicPlanService.updateKpiActual('k1', '85')
    const [url, body] = vi.mocked(apiClient.post).mock.calls[0] ?? []
    expect(url).toBe('/api/v1/kpis/k1/update-actual/')
    expect(body).toEqual({ actual: '85' })
  })
})
