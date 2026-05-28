import { apiClient } from '@/shared/api'

export interface Compensation {
  id: string
  employee: string
  valid_from: string
  valid_to: string | null
  base_salary: string
  has_family_allowance: boolean
  regimen_laboral: string
  pension_regime: string
  afp_commission_type: string
  cuspp: string
  health_regime: string
  eps_provider: string
  cci: string
  bank_code: string
  bank_account: string
  permission_level: number
  source: 'MIGRATION' | 'MANUAL' | 'CONTRACT_AMENDMENT'
  contract_snapshot: string | null
  created_at: string
  updated_at: string
}

export type CompensationCreate = Omit<Compensation, 'id' | 'created_at' | 'updated_at'>

const BASE = '/api/v1/payroll/compensations/'

function unwrap<T>(raw: unknown): T {
  const r = raw as Record<string, unknown> | null
  return (r?.data ?? r?.results ?? r) as T
}

export const compensationsService = {
  async list(filters?: { employee?: string; source?: string }) {
    const response = await apiClient.get<{ data?: Compensation[]; results?: Compensation[] }>(BASE, filters)
    return unwrap<Compensation[]>(response.data) ?? []
  },

  async history(employeeId: string) {
    const response = await apiClient.get<{ data?: Compensation[] }>(`${BASE}history/${employeeId}/`)
    return unwrap<Compensation[]>(response.data) ?? []
  },

  async create(payload: CompensationCreate) {
    const response = await apiClient.post<Compensation>(BASE, payload)
    return unwrap<Compensation>(response.data)
  },

  async update(id: string, payload: Partial<CompensationCreate>) {
    const response = await apiClient.patch<Compensation>(`${BASE}${id}/`, payload)
    return unwrap<Compensation>(response.data)
  },

  async remove(id: string) {
    await apiClient.delete(`${BASE}${id}/`)
  },
}
