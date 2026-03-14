import { apiClient } from '@/lib/api'
import { UploadDocumentResponse, TipoDocumento } from '../types/onboarding'

export async function uploadFoto(archivo: File): Promise<UploadDocumentResponse> {
  const formData = new FormData()
  formData.append('archivo', archivo)
  const response = await apiClient.post('/api/v1/rrhh/onboarding/subir-foto/', formData)
  return response.data?.data
}

export async function uploadDocument(
  tipoDocumento: TipoDocumento,
  archivo: File,
  nombreDocumento?: string
): Promise<UploadDocumentResponse> {
  const formData = new FormData()
  formData.append('archivo', archivo)
  formData.append('tipo_documento', tipoDocumento)
  if (nombreDocumento) formData.append('nombre_documento', nombreDocumento)
  const response = await apiClient.post('/api/v1/rrhh/onboarding/subir-documento/', formData)
  return response.data?.data
}

export async function corregirCorreo(onboardingId: number, correoPersonal: string): Promise<void> {
  await apiClient.post(`/api/v1/rrhh/onboarding/${onboardingId}/corregir-correo/`, {
    correo_personal: correoPersonal,
  })
}
