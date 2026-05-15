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
import { tRegistroService } from '../tRegistroService'

describe('tRegistroService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('list unwraps results', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: '1', status: 'draft' }] } },
    } as never)
    const out = await tRegistroService.list()
    expect(out).toHaveLength(1)
    const url = vi.mocked(apiClient.get).mock.calls[0]?.[0] as string
    expect(url).toContain('/api/v1/t-registro-declarations/')
  })

  it('get fetches detail', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { id: 'abc', status: 'submitted' } },
    } as never)
    const out = await tRegistroService.get('abc')
    expect(out.id).toBe('abc')
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toBe(
      '/api/v1/t-registro-declarations/abc/',
    )
  })

  it('create POSTs to base', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'new', status: 'draft' } },
    } as never)
    await tRegistroService.create({ employer_ruc: '20111111111' } as never)
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/t-registro-declarations/',
    )
  })

  it('generateAnexo3 hits action endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'x', anexo3_txt: 'H|TRREG|' } },
    } as never)
    await tRegistroService.generateAnexo3('x')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/t-registro-declarations/x/generate-anexo3/',
    )
  })

  it('validatePvs hits validate-pvs action', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'x', status: 'validated', pvs_errors: [] } },
    } as never)
    await tRegistroService.validatePvs('x')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/t-registro-declarations/x/validate-pvs/',
    )
  })

  it('submit forwards reference in body', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'x', status: 'submitted', sunat_reference: 'R1' } },
    } as never)
    await tRegistroService.submit('x', 'R1')
    const call = vi.mocked(apiClient.post).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/t-registro-declarations/x/submit/')
    expect(call?.[1]).toEqual({ reference: 'R1' })
  })

  it('markAccepted forwards reference', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'x', status: 'accepted' } },
    } as never)
    await tRegistroService.markAccepted('x', 'C-2026')
    const call = vi.mocked(apiClient.post).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/t-registro-declarations/x/mark-accepted/')
    expect(call?.[1]).toEqual({ reference: 'C-2026' })
  })

  it('markRejected forwards reason', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'x', status: 'rejected' } },
    } as never)
    await tRegistroService.markRejected('x', 'RUC inválido')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      reason: 'RUC inválido',
    })
  })

  it('downloadAnexo3Txt requests blob', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: new Blob(['H|TRREG|'], { type: 'text/plain' }),
    } as never)
    const blob = await tRegistroService.downloadAnexo3Txt('x')
    expect(blob).toBeInstanceOf(Blob)
    const call = vi.mocked(apiClient.get).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/t-registro-declarations/x/anexo3-txt/')
    expect((call?.[1] as { responseType?: string } | undefined)?.responseType).toBe('blob')
  })
})
