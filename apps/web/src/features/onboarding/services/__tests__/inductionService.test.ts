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
import { inductionService } from '../inductionService'

describe('inductionService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('listPlans hits /api/v1/onboarding/induction-plans/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 'p1', status: 'draft' }] } },
    } as never)
    const out = await inductionService.listPlans()
    expect(out).toHaveLength(1)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/onboarding/induction-plans/',
    )
  })

  it('createPlan forwards payload', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'p1', status: 'draft', tasks: [] } },
    } as never)
    await inductionService.createPlan({ employee: 'e1', kind: 'general' })
    const call = vi.mocked(apiClient.post).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/onboarding/induction-plans/')
    expect(call?.[1]).toMatchObject({ employee: 'e1', kind: 'general' })
  })

  it('start posts to /start/', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'p1', status: 'in_progress' } },
    } as never)
    await inductionService.start('p1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/onboarding/induction-plans/p1/start/',
    )
  })

  it('complete and certify hit lifecycle endpoints', async () => {
    vi.mocked(apiClient.post)
      .mockResolvedValueOnce({ data: { data: { id: 'p1', status: 'completed' } } } as never)
      .mockResolvedValueOnce({ data: { data: { id: 'p1', status: 'certified' } } } as never)
    await inductionService.complete('p1')
    await inductionService.certify('p1')
    const calls = vi.mocked(apiClient.post).mock.calls
    expect(calls[0]?.[0]).toBe('/api/v1/onboarding/induction-plans/p1/complete/')
    expect(calls[1]?.[0]).toBe('/api/v1/onboarding/induction-plans/p1/certify/')
  })

  it('assignMentor forwards mentor + notes', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'p1', status: 'draft' } },
    } as never)
    await inductionService.assignMentor('p1', 'm1', 'Buddy A')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      mentor: 'm1', notes: 'Buddy A',
    })
  })

  it('recordEvaluation forwards score + comments', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { plan: { id: 'p1' }, evaluation: { id: 'e1', score: 85, passed: true } } },
    } as never)
    await inductionService.recordEvaluation('p1', { score: 85, comments: 'X' })
    const call = vi.mocked(apiClient.post).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/onboarding/induction-plans/p1/record-evaluation/')
    expect(call?.[1]).toMatchObject({ score: 85, comments: 'X' })
  })

  it('downloadCertificatePdf requests blob', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: new Blob(['%PDF'], { type: 'application/pdf' }),
    } as never)
    const b = await inductionService.downloadCertificatePdf('p1')
    expect(b).toBeInstanceOf(Blob)
    const call = vi.mocked(apiClient.get).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/onboarding/induction-plans/p1/certificate-pdf/')
    expect((call?.[1] as { responseType?: string } | undefined)?.responseType).toBe('blob')
  })

  it('markTaskDone hits action endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 't1', is_done: true } },
    } as never)
    await inductionService.markTaskDone('t1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/onboarding/induction-tasks/t1/mark-done/',
    )
  })
})
