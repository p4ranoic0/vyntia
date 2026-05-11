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
import { selectionService } from '../selectionService'

describe('selectionService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('listCandidates unwraps results array', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: '1', first_names: 'Ana' }] } },
    } as never)
    const out = await selectionService.listCandidates()
    expect(out).toHaveLength(1)
    const url = vi.mocked(apiClient.get).mock.calls[0]?.[0] as string
    expect(url).toContain('/api/v1/candidates/')
  })

  it('createRequisition POSTs payload', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'r1', code: 'REQ-001', status: 'draft' } },
    } as never)
    const r = await selectionService.createRequisition({
      position: 'p1', department: 'd1', justification: 'replacement',
    })
    expect(r.id).toBe('r1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/personnel-requisitions/',
    )
  })

  it('approveHR posts empty body to /approve-hr/', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'r1', status: 'pending_approval' } },
    } as never)
    await selectionService.approveHR('r1')
    const call = vi.mocked(apiClient.post).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/personnel-requisitions/r1/approve-hr/')
    expect(call?.[1]).toEqual({})
  })

  it('rejectRequisition forwards reason', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'r1', status: 'rejected' } },
    } as never)
    await selectionService.rejectRequisition('r1', 'sin presupuesto')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      reason: 'sin presupuesto',
    })
  })

  it('listPostings filters by requisition when provided', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await selectionService.listPostings('req-abc')
    const url = vi.mocked(apiClient.get).mock.calls[0]?.[0] as string
    expect(url).toContain('requisition=req-abc')
  })

  it('publishPosting posts to /publish/', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'p1', status: 'published' } },
    } as never)
    await selectionService.publishPosting('p1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/job-postings/p1/publish/',
    )
  })

  it('declareVoid requires reason', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'p1', status: 'declared_void' } },
    } as never)
    await selectionService.declareVoid('p1', 'Sin candidatos aptos')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      reason: 'Sin candidatos aptos',
    })
  })

  it('computeRanking unwraps array of rankings', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: {
        data: {
          results: [
            { id: '1', rank: 1, outcome: 'winner', total_score: '17.40' },
            { id: '2', rank: 2, outcome: 'waiting_list', total_score: '15.00' },
          ],
        },
      },
    } as never)
    const rows = await selectionService.computeRanking('p1')
    expect(rows).toHaveLength(2)
    expect(rows[0].outcome).toBe('winner')
  })

  it('upsertStage POSTs when no id, PATCHes when present', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'new' } },
    } as never)
    vi.mocked(apiClient.patch).mockResolvedValueOnce({
      data: { data: { id: 'existing' } },
    } as never)
    await selectionService.upsertStage({ posting: 'p1', kind: 'knowledge', name: 'K', order: 1 })
    await selectionService.upsertStage({
      id: 'existing', posting: 'p1', kind: 'knowledge', name: 'K', order: 1,
    })
    expect(vi.mocked(apiClient.post).mock.calls).toHaveLength(1)
    expect(vi.mocked(apiClient.patch).mock.calls[0]?.[0]).toContain('/existing/')
  })

  it('advanceApplication sends new_status field', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'a1', status: 'reviewing' } },
    } as never)
    await selectionService.advanceApplication('a1', 'reviewing')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      new_status: 'reviewing',
    })
  })

  it('upsertEvaluation routes by id presence', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'ev1' } },
    } as never)
    await selectionService.upsertEvaluation({
      application: 'a1', stage: 's1', score: '17.50',
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/candidate-evaluations/',
    )
  })

  it('listRanking filters by posting', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await selectionService.listRanking('p1')
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain('posting=p1')
  })
})
