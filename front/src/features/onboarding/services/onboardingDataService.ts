import { apiClient } from '@/lib/api'

// --- DatosFamiliares ---
export async function getFamiliares(empleadoId: number) {
  const res = await apiClient.get('/api/v1/rrhh/datos-familiares/', { params: { empleado: empleadoId } })
  const raw = res.data
  return raw?.data?.results ?? raw?.results ?? raw?.data ?? []
}

export async function createFamiliar(data: Record<string, unknown>) {
  const res = await apiClient.post('/api/v1/rrhh/datos-familiares/', data)
  return res.data?.data ?? res.data
}

export async function updateFamiliar(id: number, data: Record<string, unknown>) {
  const res = await apiClient.patch(`/api/v1/rrhh/datos-familiares/${id}/`, data)
  return res.data?.data ?? res.data
}

export async function deleteFamiliar(id: number) {
  await apiClient.delete(`/api/v1/rrhh/datos-familiares/${id}/`)
}

// --- DatosAcademicos ---
export async function getAcademicos(empleadoId: number) {
  const res = await apiClient.get('/api/v1/rrhh/datos-academicos/', { params: { empleado: empleadoId } })
  const raw = res.data
  return raw?.data?.results ?? raw?.results ?? raw?.data ?? []
}

export async function createAcademico(data: Record<string, unknown>) {
  const res = await apiClient.post('/api/v1/rrhh/datos-academicos/', data)
  return res.data?.data ?? res.data
}

export async function updateAcademico(id: number, data: Record<string, unknown>) {
  const res = await apiClient.patch(`/api/v1/rrhh/datos-academicos/${id}/`, data)
  return res.data?.data ?? res.data
}

// --- CursosCertificaciones ---
export async function getCursos(empleadoId: number) {
  const res = await apiClient.get('/api/v1/rrhh/cursos-certificaciones/', { params: { empleado: empleadoId } })
  const raw = res.data
  return raw?.data?.results ?? raw?.results ?? raw?.data ?? []
}

export async function createCurso(data: Record<string, unknown>) {
  const res = await apiClient.post('/api/v1/rrhh/cursos-certificaciones/', data)
  return res.data?.data ?? res.data
}

export async function updateCurso(id: number, data: Record<string, unknown>) {
  const res = await apiClient.patch(`/api/v1/rrhh/cursos-certificaciones/${id}/`, data)
  return res.data?.data ?? res.data
}

export async function deleteCurso(id: number) {
  await apiClient.delete(`/api/v1/rrhh/cursos-certificaciones/${id}/`)
}

// --- Constancias de trabajo (DocumentosDigitales query) ---
export async function getConstanciasTrabajo(empleadoId: number) {
  const res = await apiClient.get('/api/v1/rrhh/legajo/', {
    params: { empleado: empleadoId, tipo_documento: 'constancia_trabajo' },
  })
  const raw = res.data
  return raw?.data?.results ?? raw?.results ?? raw?.data ?? []
}
