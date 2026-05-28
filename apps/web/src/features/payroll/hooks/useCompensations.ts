import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  type Compensation,
  type CompensationCreate,
  compensationsService,
} from '../services/compensationsService'

const KEY = ['payroll', 'compensations'] as const

export function useCompensationsList(filters?: { employee?: string }) {
  return useQuery<Compensation[]>({
    queryKey: [...KEY, filters],
    queryFn: () => compensationsService.list(filters),
  })
}

export function useCompensationHistory(employeeId: string | undefined) {
  return useQuery<Compensation[]>({
    queryKey: [...KEY, 'history', employeeId],
    queryFn: () => compensationsService.history(employeeId!),
    enabled: !!employeeId,
  })
}

export function useCreateCompensation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: CompensationCreate) => compensationsService.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  })
}
