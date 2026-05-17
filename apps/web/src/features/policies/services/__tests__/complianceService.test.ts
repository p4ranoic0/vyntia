import { describe, expect, it, vi, beforeEach } from 'vitest'

vi.mock('@/shared/api/api', () => ({
  apiClient: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { apiClient } from '@/shared/api/api'
import { complianceService } from '../complianceService'

describe('complianceService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('listMatrices hits endpoint', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await complianceService.listMatrices()
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain('/api/v1/compliance-matrices/')
  })

  it('createMatrix POSTs', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'm1' } },
    } as never)
    await complianceService.createMatrix({
      name: 'M', fiscal_year: 2026, owner_user: 'u1',
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe('/api/v1/compliance-matrices/')
  })

  it('markCompleted hits action', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'o1', status: 'pendiente' } },
    } as never)
    await complianceService.markCompleted('o1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/compliance-obligations/o1/mark-completed/',
    )
  })

  it('getAlerts uses days_ahead querystring', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { overdue: [], due_soon: [], cutoff_date: '2026-06-16' } },
    } as never)
    await complianceService.getAlerts(45)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain('days_ahead=45')
  })

  it('markOverdue POSTs to collection action', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { flagged_overdue: 2 } },
    } as never)
    const out = await complianceService.markOverdue()
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/compliance-obligations/mark-overdue/',
    )
    expect(out.flagged_overdue).toBe(2)
  })

  it('listObligations filters by matrix', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await complianceService.listObligations('m1')
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain('matrix=m1')
  })
})
