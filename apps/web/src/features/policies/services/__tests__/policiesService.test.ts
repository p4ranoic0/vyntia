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
import { policiesService } from '../policiesService'

describe('policiesService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('listPolicies hits /api/v1/policies/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 'p1', title: 'RIT' }] } },
    } as never)
    const out = await policiesService.listPolicies()
    expect(out).toHaveLength(1)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/policies/',
    )
  })

  it('createPolicy POSTs payload', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'p1', title: 'RIT' } },
    } as never)
    await policiesService.createPolicy({
      kind: 'rit', title: 'RIT', owner_user: 'u1',
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/policies/',
    )
  })

  it('retirePolicy hits action endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'p1', status: 'retired' } },
    } as never)
    await policiesService.retirePolicy('p1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/policies/p1/retire/',
    )
  })

  it('submitForReview sends approvers', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'f1', status: 'pending', steps: [] } },
    } as never)
    await policiesService.submitForReview('v1', ['u2', 'u3'])
    const [url, body] = vi.mocked(apiClient.post).mock.calls[0] ?? []
    expect(url).toBe('/api/v1/policy-versions/v1/submit-for-review/')
    expect(body).toEqual({ approvers: ['u2', 'u3'] })
  })

  it('publishVersion sends payload', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'pub1', target_audience: 'all' } },
    } as never)
    await policiesService.publishVersion('v1', {
      target_audience: 'all', requires_acknowledgment: true,
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/policy-versions/v1/publish/',
    )
  })

  it('decideStep posts to /decide/', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { step: { id: 's1' }, flow: { id: 'f1' } } },
    } as never)
    await policiesService.decideStep('f1', { step_order: 1, decision: 'approved' })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/policy-approval-flows/f1/decide/',
    )
  })

  it('acknowledge POSTs signature_kind + payload', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'a1', status: 'acknowledged' } },
    } as never)
    await policiesService.acknowledge('a1', {
      signature_kind: 'checkbox', signature_payload: 'true',
    })
    const [url, body] = vi.mocked(apiClient.post).mock.calls[0] ?? []
    expect(url).toBe('/api/v1/policy-acknowledgments/a1/acknowledge/')
    expect(body).toMatchObject({ signature_kind: 'checkbox' })
  })

  it('decline POSTs reason', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'a1', status: 'declined' } },
    } as never)
    await policiesService.decline('a1', 'no')
    const [, body] = vi.mocked(apiClient.post).mock.calls[0] ?? []
    expect(body).toEqual({ reason: 'no' })
  })

  it('expireOverdue collection action', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { expired: 3 } },
    } as never)
    const out = await policiesService.expireOverdue()
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/policy-acknowledgments/expire-overdue/',
    )
    expect(out.expired).toBe(3)
  })

  it('listAcknowledgments builds filter querystring', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await policiesService.listAcknowledgments({ status: 'pending' })
    const url = vi.mocked(apiClient.get).mock.calls[0]?.[0]
    expect(url).toContain('status=pending')
  })
})
