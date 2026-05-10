import { describe, expect, it, vi, beforeEach } from 'vitest'

vi.mock('@/shared/api/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}))

import { apiClient } from '@/shared/api/api'
import { ccfService } from '../ccfService'

describe('ccfService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('listCCFs unwraps paginated data.results', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: '1', title: 'CCF A', version: 1 }] } },
    } as never)
    const ccfs = await ccfService.listCCFs()
    expect(ccfs).toHaveLength(1)
    expect(ccfs[0].title).toBe('CCF A')
  })

  it('createCCF POSTs payload and unwraps single item', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'new', title: 'X', version: 1 } },
    } as never)
    const ccf = await ccfService.createCCF({ title: 'X' })
    expect(ccf.title).toBe('X')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe('/api/v1/compensation/ccfs/')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({ title: 'X' })
  })

  it('approveCCF passes effective_date when provided', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: '1', status: 'approved' } },
    } as never)
    await ccfService.approveCCF('1', '2026-06-01')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/compensation/ccfs/1/approve/',
    )
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({ effective_date: '2026-06-01' })
  })

  it('listCategories filters by ccf when provided', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await ccfService.listCategories('abc')
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain('ccf=abc')
  })

  it('upsertFactorScore uses POST when id missing, PATCH when present', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { data: {} } } as never)
    vi.mocked(apiClient.patch).mockResolvedValueOnce({ data: { data: {} } } as never)
    await ccfService.upsertFactorScore({ category: 'c', subfactor: 's', score: 50 })
    await ccfService.upsertFactorScore({ id: 'x', category: 'c', subfactor: 's', score: 60 })
    expect(vi.mocked(apiClient.post).mock.calls).toHaveLength(1)
    expect(vi.mocked(apiClient.patch).mock.calls).toHaveLength(1)
    expect(vi.mocked(apiClient.patch).mock.calls[0]?.[0]).toContain('/x/')
  })

  it('upsertSalaryBand routes to POST or PATCH by id', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { data: {} } } as never)
    await ccfService.upsertSalaryBand({
      category: 'c', min_salary: '1000', mid_salary: '2000', max_salary: '3000',
    })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe('/api/v1/compensation/salary-bands/')
  })

  it('getSalaryGapAudit unwraps {rows, summary} shape', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        data: {
          rows: [{ category_code: 'A', alert: true } as never],
          summary: { total_categories: 1, alerted_categories: 1 } as never,
        },
      },
    } as never)
    const audit = await ccfService.getSalaryGapAudit()
    expect(audit.rows).toHaveLength(1)
    expect(audit.summary.alerted_categories).toBe(1)
  })

  it('uploadCCFExcel sends multipart with file + ccf_title', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: {
        data: {
          success: true, categories_created: 2, bands_created: 2,
          scores_created: 5, row_errors: [],
        },
      },
    } as never)
    const file = new File(['fake'], 'ccf.xlsx', { type: 'application/octet-stream' })
    const result = await ccfService.uploadCCFExcel(file, 'CCF 2026')
    expect(result.success).toBe(true)
    expect(result.categories_created).toBe(2)
    const call = vi.mocked(apiClient.post).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/compensation/ccf/import-excel/')
    expect(call?.[1]).toBeInstanceOf(FormData)
  })

  it('uploadCCFExcel extracts result from error response payload', async () => {
    vi.mocked(apiClient.post).mockRejectedValueOnce({
      response: {
        data: {
          data: {
            success: false, categories_created: 0, bands_created: 0,
            scores_created: 0,
            row_errors: [{ row: 3, error: 'bad' }],
          },
        },
      },
    } as never)
    const file = new File(['x'], 'bad.xlsx')
    const result = await ccfService.uploadCCFExcel(file, 'CCF Bad')
    expect(result.success).toBe(false)
    expect(result.row_errors).toHaveLength(1)
    expect(result.row_errors[0].row).toBe(3)
  })
})
