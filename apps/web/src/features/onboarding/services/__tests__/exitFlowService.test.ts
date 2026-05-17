import { describe, expect, it, vi, beforeEach } from 'vitest'

vi.mock('@/shared/api/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

import { apiClient } from '@/shared/api/api'
import { exitFlowService } from '../exitFlowService'

describe('exitFlowService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('scaffold POSTs termination id', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { interview: { id: 'i1' }, checklist: { id: 'c1' }, systems_offboarding: { id: 's1' } } },
    } as never)
    await exitFlowService.scaffold('t1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/onboarding/exit-flow-scaffold/',
    )
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      termination: 't1',
    })
  })

  it('listInterviews hits route', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await exitFlowService.listInterviews()
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/onboarding/exit-interviews/',
    )
  })

  it('submitInterview hits action endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'i1', status: 'completed' } },
    } as never)
    await exitFlowService.submitInterview('i1', {
      answers: { p1: 'sí' },
      sentiment: 'positivo',
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/onboarding/exit-interviews/i1/submit/',
    )
  })

  it('listChecklists hits route', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await exitFlowService.listChecklists()
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/onboarding/handover-checklists/',
    )
  })

  it('completeChecklist sends signers', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'c1', status: 'completed' } },
    } as never)
    await exitFlowService.completeChecklist('c1', {
      signed_by_outgoing: 1,
      signed_by_incoming: 2,
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/onboarding/handover-checklists/c1/complete/',
    )
  })

  it('deliverItem hits route', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'i1', status: 'entregado' } },
    } as never)
    await exitFlowService.deliverItem('i1', 'todo OK')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/onboarding/handover-items/i1/deliver/',
    )
  })

  it('completeSystemsOffboarding sends checks', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 's1', status: 'completed' } },
    } as never)
    await exitFlowService.completeSystemsOffboarding('s1', {
      checks: { correo: true, vpn: true },
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/onboarding/systems-offboardings/s1/complete/',
    )
  })
})
