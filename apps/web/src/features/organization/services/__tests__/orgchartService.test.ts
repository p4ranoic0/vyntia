import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/shared/api/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}))

import { apiClient } from '@/shared/api/api'
import { orgchartService } from '../orgchartService'

describe('orgchartService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('listPositions defaults is_current=true and unwraps results', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        data: {
          results: [
            { id: 'p1', code: 'ANA-001', name: 'Analista', is_current: true },
          ],
        },
      },
    } as never)
    const positions = await orgchartService.listPositions({ is_current: true })
    expect(positions).toHaveLength(1)
    expect(positions[0].code).toBe('ANA-001')
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain('is_current=true')
  })

  it('listPlazas unwraps results from data.results shape', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        data: {
          results: [{ id: 'pl1', code: 'PLAZA-001', status: 'vacante' }],
        },
      },
    } as never)
    const plazas = await orgchartService.listPlazas()
    expect(plazas).toHaveLength(1)
    expect(plazas[0].status).toBe('vacante')
  })

  it('listOccupationalCategories handles bare array response (no pagination)', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        data: [
          { id: '1', code: '01', name: 'Ejecutivo', is_active: true },
          { id: '2', code: '02', name: 'Empleado', is_active: true },
        ],
      },
    } as never)
    const cats = await orgchartService.listOccupationalCategories()
    expect(cats).toHaveLength(2)
  })

  it('reparentDepartment PATCHes area_padre', async () => {
    vi.mocked(apiClient.patch).mockResolvedValueOnce({ data: {} } as never)
    await orgchartService.reparentDepartment('dept-1', 'dept-2')
    expect(vi.mocked(apiClient.patch).mock.calls[0]?.[0]).toBe(
      '/api/v1/organization/departments/dept-1/',
    )
    expect(vi.mocked(apiClient.patch).mock.calls[0]?.[1]).toEqual({ area_padre: 'dept-2' })
  })

  it('reassignPlaza calls vacate then occupy', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ data: {} } as never)
    await orgchartService.reassignPlaza('plaza-1', 'emp-new')
    const calls = vi.mocked(apiClient.post).mock.calls
    expect(calls).toHaveLength(2)
    expect(calls[0]?.[0]).toContain('/vacate/')
    expect(calls[1]?.[0]).toContain('/occupy/')
    expect(calls[1]?.[1]).toEqual({ employee: 'emp-new' })
  })

  it('movePositionToDepartment PATCHes department FK', async () => {
    vi.mocked(apiClient.patch).mockResolvedValueOnce({ data: {} } as never)
    await orgchartService.movePositionToDepartment('pos-1', 'dept-x')
    expect(vi.mocked(apiClient.patch).mock.calls[0]?.[1]).toEqual({ department: 'dept-x' })
  })
})
