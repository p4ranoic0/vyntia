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

export async function subirDocumento(
  empleadoId: number,
  tipoDocumento: string,
  categoria: string,
  label: string,
  file: File,
  extraFields?: Record<string, string | number>
): Promise<UploadDocumentResponse> {
  const formData = new FormData()
  formData.append('empleado', String(empleadoId))
  formData.append('tipo_documento', tipoDocumento)
  formData.append('categoria', categoria)
  formData.append('nombre_documento', label)
  formData.append('archivo', file)
  formData.append('estado_documento', 'pendiente_revision')
  formData.append('nivel_acceso', 'restringido')
  if (extraFields) {
    Object.entries(extraFields).forEach(([key, val]) => {
      formData.append(key, String(val))
    })
  }
  const res = await apiClient.post('/api/v1/rrhh/onboarding/subir-documento/', formData)
  return res.data?.data ?? res.data
}

export async function corregirCorreo(onboardingId: number, correoPersonal: string): Promise<void> {
  await apiClient.post(`/api/v1/rrhh/onboarding/${onboardingId}/corregir-correo/`, {
    correo_personal: correoPersonal,
  })
}
