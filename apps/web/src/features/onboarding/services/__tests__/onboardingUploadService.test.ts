import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock the apiClient before importing the module under test
vi.mock('@/lib/api', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

import { subirDocumento } from '../onboardingUploadService'
import { apiClient } from '@/lib/api'

describe('subirDocumento', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('calls the onboarding subir-documento endpoint with FormData', async () => {
    const mockResponse = {
      data: {
        data: {
          documento_id: 1,
          tipo_documento: 'dni',
          estado_documento: 'pendiente_revision',
          fecha_subida: null,
          nombre_documento: 'DNI del empleado',
        },
      },
    }
    ;(apiClient.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce(mockResponse)

    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    const result = await subirDocumento(42, 'dni', 'personal', 'DNI del empleado', file)

    expect(apiClient.post).toHaveBeenCalledWith(
      '/api/v1/onboarding/processes/subir-documento/',
      expect.any(FormData)
    )
    expect(result.tipo_documento).toBe('dni')
    expect(result.estado_documento).toBe('pendiente_revision')
  })
})
