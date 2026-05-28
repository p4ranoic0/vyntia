import { describe, expect, it, vi } from 'vitest'

vi.mock('@/shared/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

import { apiClient } from '@/shared/api'
import { compensationsService } from '../compensationsService'

describe('compensationsService', () => {
  it('list unwraps {data: [...]} envelope', async () => {
    ;(apiClient.get as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ data: { data: [{ id: '1' }] } })
    const res = await compensationsService.list()
    expect(res).toEqual([{ id: '1' }])
  })

  it('history calls /history/{employeeId}/', async () => {
    ;(apiClient.get as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ data: { data: [] } })
    await compensationsService.history('abc')
    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/payroll/compensations/history/abc/')
  })

  it('create POSTs the payload', async () => {
    ;(apiClient.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ data: { data: { id: '2' } } })
    const res = await compensationsService.create({
      employee: 'e1', valid_from: '2026-01-01', valid_to: null,
      base_salary: '3000.00', has_family_allowance: false,
      regimen_laboral: '728', pension_regime: 'ONP', afp_commission_type: '',
      cuspp: '', health_regime: 'ESSALUD', eps_provider: '',
      cci: '', bank_code: '', bank_account: '', permission_level: 6,
      source: 'MANUAL', contract_snapshot: null,
    })
    expect(res).toEqual({ id: '2' })
  })
})
