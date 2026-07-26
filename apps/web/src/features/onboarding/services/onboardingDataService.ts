import { apiClient } from '@/shared/api/api'

// --- DatosFamiliares ---
export async function getFamiliares(empleadoId: number) {
  const res = await apiClient.get('/api/v1/family-members/', { empleado: empleadoId })
  const raw = res.data
  return raw?.data?.results ?? raw?.results ?? raw?.data ?? []
}

export async function createFamiliar(data: Record<string, unknown>) {
  const res = await apiClient.post('/api/v1/family-members/', data)
  return res.data?.data ?? res.data
}

export async function updateFamiliar(id: number, data: Record<string, unknown>) {
  const res = await apiClient.patch(`/api/v1/family-members/${id}/`, data)
  return res.data?.data ?? res.data
}

export async function deleteFamiliar(id: number) {
  await apiClient.delete(`/api/v1/family-members/${id}/`)
}

// --- DatosAcademicos ---
export async function getAcademicos(empleadoId: number) {
  const res = await apiClient.get('/api/v1/academic-records/', { empleado: empleadoId })
  const raw = res.data
  return raw?.data?.results ?? raw?.results ?? raw?.data ?? []
}

export async function createAcademico(data: Record<string, unknown>) {
  const res = await apiClient.post('/api/v1/academic-records/', data)
  return res.data?.data ?? res.data
}

export async function updateAcademico(id: number, data: Record<string, unknown>) {
  const res = await apiClient.patch(`/api/v1/academic-records/${id}/`, data)
  return res.data?.data ?? res.data
}

// --- CursosCertificaciones ---
export async function getCursos(empleadoId: number) {
  const res = await apiClient.get('/api/v1/certifications/', { empleado: empleadoId })
  const raw = res.data
  return raw?.data?.results ?? raw?.results ?? raw?.data ?? []
}

export async function createCurso(data: Record<string, unknown>) {
  const res = await apiClient.post('/api/v1/certifications/', data)
  return res.data?.data ?? res.data
}

export async function updateCurso(id: number, data: Record<string, unknown>) {
  const res = await apiClient.patch(`/api/v1/certifications/${id}/`, data)
  return res.data?.data ?? res.data
}

export async function deleteCurso(id: number) {
  await apiClient.delete(`/api/v1/certifications/${id}/`)
}

// --- Constancias de trabajo (DocumentosDigitales query) ---
export async function getConstanciasTrabajo(empleadoId: number) {
  const res = await apiClient.get('/api/v1/documents/documents/', {
    empleado: empleadoId,
    tipo_documento: 'constancia_trabajo',
    es_version_actual: 'true',
  })
  const raw = res.data
  return raw?.data?.results ?? raw?.results ?? raw?.data ?? []
}
