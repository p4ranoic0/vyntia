import { apiClient } from '@/lib/api'

export interface ConfiguracionEmpresa {
  id: number
  nombre: string
  ruc: string
  direccion: string
  distrito: string
  provincia: string
  departamento: string
  telefono: string
  email: string
  web: string
  logo: string | null
  logo_url: string | null
  representante_legal: string
  cargo_representante: string
  dni_representante: string
  resolucion_creacion: string
}

export const empresaService = {
  async get(): Promise<ConfiguracionEmpresa> {
    const response = await apiClient.get('/api/v1/organization/companies/')
    const raw = response.data
    // ViewSet list returns paginated or direct — handle both
    const data = raw?.data ?? raw
    // If it's a list, take first item
    if (Array.isArray(data)) return data[0]
    return data
  },

  async update(data: Partial<ConfiguracionEmpresa>, logo?: File): Promise<ConfiguracionEmpresa> {
    if (logo) {
      const formData = new FormData()
      Object.entries(data).forEach(([k, v]) => {
        if (v != null) formData.append(k, String(v))
      })
      formData.append('logo', logo)
      const response = await apiClient.post('/api/v1/organization/companies/', formData)
      const raw = response.data
      return raw?.data ?? raw
    }
    const response = await apiClient.post('/api/v1/organization/companies/', data)
    const raw = response.data
    return raw?.data ?? raw
  },
}
