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
import { legajoContentService } from '../legajoContentService'

describe('legajoContentService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('listWorkExperiences hits /api/v1/work-experiences/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 'w1' }] } },
    } as never)
    const out = await legajoContentService.listWorkExperiences('e1')
    expect(out).toHaveLength(1)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/work-experiences/?employee=e1',
    )
  })

  it('createWorkExperience POSTs', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'w1', employer: 'ACME' } },
    } as never)
    await legajoContentService.createWorkExperience({
      employee: 'e1', employer: 'ACME', position_title: 'X',
    } as never)
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe('/api/v1/work-experiences/')
  })

  it('listSwornDeclarations hits /api/v1/sworn-declarations/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 's1' }] } },
    } as never)
    await legajoContentService.listSwornDeclarations('e1')
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/sworn-declarations/?employee=e1',
    )
  })

  it('createSwornDeclaration POSTs', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 's1', kind: 'no_parentesco' } },
    } as never)
    await legajoContentService.createSwornDeclaration({
      employee: 'e1', kind: 'no_parentesco', declared_at: '2026-05-14',
    } as never)
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/sworn-declarations/',
    )
  })

  it('listJobHistories hits /api/v1/job-histories/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 'h1' }] } },
    } as never)
    await legajoContentService.listJobHistories('e1')
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/job-histories/?employee=e1',
    )
  })

  it('createJobHistory POSTs', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'h1', position_label: 'X' } },
    } as never)
    await legajoContentService.createJobHistory({
      employee: 'e1', position_label: 'X', start_date: '2024-01-01',
    } as never)
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe('/api/v1/job-histories/')
  })
})
