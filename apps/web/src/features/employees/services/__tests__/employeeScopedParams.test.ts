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
import { employeesService } from '../employeesService'
import { getFamiliares, getAcademicos, getCursos } from '@/features/onboarding/services/onboardingDataService'

/**
 * `apiClient.get(url, params)` takes the query params object DIRECTLY — it wraps
 * it in axios' `{ params }` config itself. Passing `{ params: { empleado } }`
 * serialized to `?params[empleado]=…`, which the backend never reads, so every
 * employee-scoped list came back unfiltered: the same familiares / datos
 * laborales showed up for every person in the tenant.
 */
describe('employee-scoped list params reach the query string', () => {
  beforeEach(() => vi.resetAllMocks())

  const paginated = { data: { data: { results: [] } } }

  const cases: Array<[string, string, () => Promise<unknown>]> = [
    ['datosFamiliares.getAll', '/api/v1/family-members/', () => employeesService.datosFamiliares.getAll('e1')],
    ['datosLaborales.get', '/api/v1/employment-data/', () => employeesService.datosLaborales.get('e1')],
    ['datosAcademicos.getAll', '/api/v1/academic-records/', () => employeesService.datosAcademicos.getAll('e1')],
    ['onboarding getFamiliares', '/api/v1/family-members/', () => getFamiliares(1)],
    ['onboarding getAcademicos', '/api/v1/academic-records/', () => getAcademicos(1)],
    ['onboarding getCursos', '/api/v1/certifications/', () => getCursos(1)],
  ]

  it.each(cases)('%s filters by empleado, not nested params', async (_name, endpoint, call) => {
    vi.mocked(apiClient.get).mockResolvedValueOnce(paginated as never)

    await call()

    const [url, params] = vi.mocked(apiClient.get).mock.calls[0] ?? []
    expect(url).toBe(endpoint)
    expect(params).not.toHaveProperty('params')
    expect(String((params as Record<string, unknown>)?.empleado)).toBeTruthy()
  })
})
