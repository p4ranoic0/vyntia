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
import { terminationService } from '../terminationService'

describe('terminationService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('list hits /api/v1/terminations/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 't1', status: 'in_progress' }] } },
    } as never)
    const out = await terminationService.list()
    expect(out).toHaveLength(1)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/terminations/',
    )
  })

  it('initiate POSTs payload', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 't1', status: 'in_progress' } },
    } as never)
    await terminationService.initiate({
      contract: 'c1',
      causal: 'renuncia',
      fecha_cese: '2026-05-20',
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/terminations/',
    )
  })

  it('complete hits action endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 't1', status: 'completed' } },
    } as never)
    await terminationService.complete('t1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/terminations/t1/complete/',
    )
  })

  it('liquidate hits action endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 't1', status: 'liquidated' } },
    } as never)
    await terminationService.liquidate('t1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/terminations/t1/liquidate/',
    )
  })

  it('cancel sends reason', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 't1', status: 'cancelled' } },
    } as never)
    await terminationService.cancel('t1', 'cambio de opinión')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/terminations/t1/cancel/',
    )
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      reason: 'cambio de opinión',
    })
  })

  it('alertas48hSLA hits collection action', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: [] },
    } as never)
    await terminationService.alertas48hSLA()
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/terminations/alertas-48h-sla/',
    )
  })

  it('markBajaTRegistroDone sends declaration id', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 't1', status: 'baja_t_registro_done' } },
    } as never)
    await terminationService.markBajaTRegistroDone('t1', 'd1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/terminations/t1/mark-baja-tregistro-done/',
    )
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      declaration: 'd1',
    })
  })
})
