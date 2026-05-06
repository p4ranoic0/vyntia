import { apiClient } from '@/lib/api'

export interface ConfiguracionVacaciones {
  id: string
  tipo_configuracion: string
  dias_por_ano: number
  is_active: boolean
}

export interface PeriodoVacacional {
  id: string
  empleado: string
  empleado_nombre?: string
  ano_periodo: number
  periodo_label?: string
  fecha_inicio_periodo: string
  fecha_fin_periodo: string
  fecha_vencimiento: string
  dias_correspondientes: number
  dias_adicionales?: number
  dias_totales?: number
  dias_gozados: number
  dias_pendientes: number
  dias_vencidos?: number
  estado_periodo: 'activo' | 'cerrado' | 'vencido' | 'cancelado'
  contrato?: string | null
  contrato_numero?: string | null
  contrato_fecha_inicio?: string | null
  contrato_fecha_fin?: string | null
  contrato_estado?: string | null
}

export interface SolicitudVacaciones {
  id: string
  empleado: {
    id: string
    nombres?: string
    apellidos?: string
    numero_identificacion?: string
  }
  empleado_nombre?: string
  empleado_nombre_completo?: string
  area?: { nombre_area?: string }
  area_nombre?: string
  periodo_vacacional: {
    id: string
    ano_periodo?: number
  }
  periodo_ano?: string
  tipo_solicitud: string
  fecha_inicio: string
  fecha_fin: string
  fecha_inicio_solicitud?: string
  fecha_fin_solicitud?: string
  dias_solicitados: number
  medio_dia?: boolean
  dias_calendario?: number
  dias_habiles?: number
  estado_solicitud: string
  fecha_envio?: string
  created_at: string
  observaciones_solicitud?: string
  fraccionamiento?: boolean
}

export interface GoceVacaciones {
  id: string
  empleado: string
  solicitud_vacaciones: string
  periodo_vacacional: string
  fecha_inicio_real: string
  fecha_fin_real: string
  dias_gozados: number
  estado_goce: string
}

export interface HistorialSolicitudVacaciones {
  id: string
  solicitud_vacaciones: string
  tipo_accion: string
  descripcion_accion: string
  estado_anterior?: string
  estado_nuevo?: string
  fecha_accion: string
}

export interface EstadisticasVacaciones {
  area_nombre: string
  ano: number
  total_empleados: number
  total_solicitudes: number
  total_dias_correspondientes: number
  total_dias_pendientes: number
  total_goces: number
}

export interface EmpleadoDiasVencidos {
  empleado_id: string
  empleado_nombre_completo: string
  empleado_numero_empleado: string
  area_nombre: string
  ano: number
  dias_correspondientes: number
  dias_vencidos: number
  porcentaje_uso: number
  fecha_vencimiento: string
}

export interface ResumenPeriodo {
  dias_correspondientes: number
  dias_gozados: number
  dias_pendientes: number
  dias_vencidos: number
  vencimiento_proximo: boolean
}

export interface SolicitudVacacionesForm {
  empleado_id?: string
  empleado?: string
  periodo_vacacional_id?: string
  periodo_vacacional?: string
  tipo_solicitud?: 'vacaciones' | 'adelanto_vacaciones' | 'fraccionamiento'
  fecha_inicio_solicitud?: string
  fecha_fin_solicitud?: string
  fecha_inicio?: string
  fecha_fin?: string
  motivo_solicitud?: string
  observaciones_solicitud?: string
  observaciones_empleado?: string
  fraccionamiento?: boolean
  medio_dia?: boolean
}

export interface AprobacionSolicitudForm {
  accion?: 'aprobar' | 'rechazar'
  accion_aprobacion?: 'aprobar' | 'rechazar'
  motivo?: string
  motivo_aprobacion?: string
}

export interface GoceVacacionesForm {
  solicitud_vacaciones: string
  fecha_inicio_real: string
  fecha_fin_real: string
  observaciones?: string
}

export interface ConfiguracionVacacionesForm {
  tipo_configuracion: string
  dias_por_ano: number
  is_active?: boolean
}

export interface FiltrosSolicitudes {
  empleado?: string
  empleado_id?: string
  area?: string
  area_id?: string
  estado_solicitud?: string
  estado?: string
  ano_periodo?: number
  ano?: number
  tipo_solicitud?: string
}

export type SolicitudesFilter = FiltrosSolicitudes

export interface FiltrosEstadisticas {
  area?: string
  ano?: number
}

function unwrap<T>(response: any): T {
  return response?.data?.data ?? response?.data?.results ?? response?.data ?? response
}

function asArray<T>(value: any): T[] {
  if (Array.isArray(value)) return value
  if (Array.isArray(value?.results)) return value.results
  return []
}

function normalizePeriodo(raw: any): PeriodoVacacional {
  return {
    id: raw.periodo_id ?? raw.id,
    empleado: raw.empleado,
    empleado_nombre: raw.empleado_nombre,
    ano_periodo: raw.ano_periodo,
    periodo_label: raw.periodo_label,
    fecha_inicio_periodo: raw.fecha_inicio_periodo,
    fecha_fin_periodo: raw.fecha_fin_periodo,
    fecha_vencimiento: raw.fecha_vencimiento,
    dias_correspondientes: raw.dias_correspondientes,
    dias_adicionales: raw.dias_adicionales,
    dias_totales: raw.dias_totales,
    dias_gozados: raw.dias_gozados,
    dias_pendientes: raw.dias_pendientes,
    dias_vencidos: raw.dias_vencidos,
    estado_periodo: raw.estado_periodo,
    contrato: raw.contrato ?? null,
    contrato_numero: raw.contrato_numero ?? null,
    contrato_fecha_inicio: raw.contrato_fecha_inicio ?? null,
    contrato_fecha_fin: raw.contrato_fecha_fin ?? null,
    contrato_estado: raw.contrato_estado ?? null,
  }
}

function splitEmployeeName(fullName?: string) {
  const value = (fullName || '').trim()
  if (!value) return { nombres: '', apellidos: '' }
  const parts = value.split(' ')
  if (parts.length === 1) return { nombres: parts[0], apellidos: '' }
  return { nombres: parts.slice(0, -2).join(' ') || parts[0], apellidos: parts.slice(-2).join(' ') }
}

function normalizeSolicitud(raw: any): SolicitudVacaciones {
  const parsed = splitEmployeeName(raw.empleado_nombre)
  return {
    id: raw.solicitud_id ?? raw.id,
    empleado: {
      id: raw.empleado,
      nombres: parsed.nombres,
      apellidos: parsed.apellidos,
      numero_identificacion: raw.empleado_rut,
    },
    empleado_nombre: raw.empleado_nombre,
    empleado_nombre_completo: raw.empleado_nombre,
    area: { nombre_area: raw.area_nombre },
    area_nombre: raw.area_nombre,
    periodo_vacacional: {
      id: raw.periodo_vacacional,
      ano_periodo: raw.ano_periodo,
    },
    periodo_ano: raw.periodo_label,
    tipo_solicitud: raw.tipo_solicitud,
    fecha_inicio: raw.fecha_inicio,
    fecha_fin: raw.fecha_fin,
    fecha_inicio_solicitud: raw.fecha_inicio,
    fecha_fin_solicitud: raw.fecha_fin,
    dias_solicitados: raw.dias_solicitados,
    medio_dia: raw.medio_dia ?? false,
    dias_calendario: raw.dias_calendario,
    dias_habiles: raw.dias_habiles,
    estado_solicitud: raw.estado_solicitud,
    fecha_envio: raw.fecha_envio,
    created_at: raw.created_at,
    observaciones_solicitud: raw.observaciones_empleado,
    fraccionamiento: raw.tipo_solicitud === 'fraccionamiento',
  }
}

const timeOffService = {
  async getConfiguraciones(): Promise<ConfiguracionVacaciones[]> {
    const response = await apiClient.get('/api/v1/time-off/configurations/')
    return asArray<any>(unwrap(response))
  },

  async getConfiguracion(id: string): Promise<ConfiguracionVacaciones> {
    const response = await apiClient.get(`/api/v1/time-off/configurations/${id}/`)
    return unwrap(response)
  },

  async createConfiguracion(data: ConfiguracionVacacionesForm): Promise<ConfiguracionVacaciones> {
    const response = await apiClient.post('/api/v1/time-off/configurations/', data)
    return unwrap(response)
  },

  async updateConfiguracion(id: string, data: Partial<ConfiguracionVacacionesForm>): Promise<ConfiguracionVacaciones> {
    const response = await apiClient.patch(`/api/v1/time-off/configurations/${id}/`, data)
    return unwrap(response)
  },

  async deleteConfiguracion(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/time-off/configurations/${id}/`)
  },

  async getPeriodos(empleadoId?: string): Promise<PeriodoVacacional[]> {
    const url = empleadoId ? `/api/v1/time-off/periods/?empleado=${empleadoId}` : '/api/v1/time-off/periods/'
    const response = await apiClient.get(url)
    return asArray<any>(unwrap(response)).map(normalizePeriodo)
  },

  async getPeriodo(id: string): Promise<PeriodoVacacional> {
    const response = await apiClient.get(`/api/v1/time-off/periods/${id}/`)
    return normalizePeriodo(unwrap(response))
  },

  async getPeriodosByEmpleado(empleadoId: string): Promise<PeriodoVacacional[]> {
    return this.getPeriodos(empleadoId)
  },

  async generarPeriodos(ano: number): Promise<{ message: string; periodos_creados: number }> {
    const response = await apiClient.post('/api/v1/time-off/periods/generar-masivo/', { ano })
    return unwrap(response)
  },

  async ajustarDiasPeriodo(periodoId: number, nuevos_dias: number, motivo: string): Promise<PeriodoVacacional> {
    const response = await apiClient.post(`/api/v1/time-off/periods/${periodoId}/ajustar-dias/`, {
      nuevos_dias,
      motivo,
    })
    return normalizePeriodo(unwrap(response))
  },

  async getSolicitudes(filtros?: FiltrosSolicitudes): Promise<any> {
    const params = new URLSearchParams()
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value === undefined || value === null || value === '') return
        if (key === 'estado') params.append('estado_solicitud', String(value))
        else if (key === 'ano') params.append('ano_periodo', String(value))
        else params.append(key, String(value))
      })
    }
    const response = await apiClient.get(`/api/v1/time-off/requests/${params.toString() ? `?${params}` : ''}`)
    const raw = unwrap<any>(response)
    const results = asArray<any>(raw).map(normalizeSolicitud)
    if (raw?.results) return { ...raw, results }
    return results
  },

  async getSolicitud(id: string): Promise<SolicitudVacaciones> {
    const response = await apiClient.get(`/api/v1/time-off/requests/${id}/`)
    return normalizeSolicitud(unwrap(response))
  },

  async createSolicitud(data: SolicitudVacacionesForm): Promise<SolicitudVacaciones> {
    const payload = {
      empleado: data.empleado ?? data.empleado_id,
      periodo_vacacional: data.periodo_vacacional ?? data.periodo_vacacional_id,
      tipo_solicitud: data.fraccionamiento ? 'fraccionamiento' : data.tipo_solicitud || 'vacaciones',
      fecha_inicio: data.fecha_inicio ?? data.fecha_inicio_solicitud,
      fecha_fin: data.fecha_fin ?? data.fecha_fin_solicitud,
      motivo_solicitud: data.motivo_solicitud || '',
      observaciones_empleado: data.observaciones_empleado ?? data.observaciones_solicitud ?? '',
      medio_dia: data.medio_dia ?? false,
    }
    const response = await apiClient.post('/api/v1/time-off/requests/', payload)
    return normalizeSolicitud(unwrap(response))
  },

  async updateSolicitud(id: string, data: Partial<SolicitudVacacionesForm>): Promise<SolicitudVacaciones> {
    const response = await apiClient.patch(`/api/v1/time-off/requests/${id}/`, data)
    return normalizeSolicitud(unwrap(response))
  },

  async deleteSolicitud(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/time-off/requests/${id}/`)
  },

  async enviarSolicitud(id: string): Promise<SolicitudVacaciones> {
    const response = await apiClient.post(`/api/v1/time-off/requests/${id}/enviar/`)
    return normalizeSolicitud(unwrap(response))
  },

  async aprobarSolicitud(id: string, data: AprobacionSolicitudForm): Promise<SolicitudVacaciones> {
    const payload = { accion: data.accion ?? data.accion_aprobacion ?? 'aprobar', motivo: data.motivo ?? data.motivo_aprobacion ?? '' }
    try {
      const response = await apiClient.post(`/api/v1/time-off/requests/${id}/aprobar-jefe/`, payload)
      return normalizeSolicitud(unwrap(response))
    } catch {
      const response = await apiClient.post(`/api/v1/time-off/requests/${id}/aprobar-rrhh/`, payload)
      return normalizeSolicitud(unwrap(response))
    }
  },

  async rechazarSolicitud(id: string, data: AprobacionSolicitudForm): Promise<SolicitudVacaciones> {
    return this.aprobarSolicitud(id, {
      accion: 'rechazar',
      motivo: data.motivo ?? data.motivo_aprobacion ?? '',
    })
  },

  async cancelarSolicitud(id: string, motivo?: string): Promise<SolicitudVacaciones> {
    const response = await apiClient.post(`/api/v1/time-off/requests/${id}/cancelar/`, { motivo })
    return normalizeSolicitud(unwrap(response))
  },

  async getSolicitudesPendientes(): Promise<SolicitudVacaciones[]> {
    const response = await apiClient.get('/api/v1/time-off/requests/pendientes-rrhh/')
    return asArray<any>(unwrap(response)).map(normalizeSolicitud)
  },

  async getSolicitudesPendientesJefe(): Promise<SolicitudVacaciones[]> {
    const response = await apiClient.get('/api/v1/time-off/requests/pendientes-jefe/')
    return asArray<any>(unwrap(response)).map(normalizeSolicitud)
  },

  async getMisSolicitudes(): Promise<SolicitudVacaciones[]> {
    const response = await apiClient.get('/api/v1/time-off/requests/mis-solicitudes/')
    return asArray<any>(unwrap(response)).map(normalizeSolicitud)
  },

  async getGoces(solicitudId?: string): Promise<GoceVacaciones[]> {
    const url = solicitudId ? `/api/v1/time-off/grants/?solicitud_vacaciones=${solicitudId}` : '/api/v1/time-off/grants/'
    const response = await apiClient.get(url)
    return asArray<any>(unwrap(response))
  },

  async getGoce(id: string): Promise<GoceVacaciones> {
    const response = await apiClient.get(`/api/v1/time-off/grants/${id}/`)
    return unwrap(response)
  },

  async createGoce(data: GoceVacacionesForm): Promise<GoceVacaciones> {
    const response = await apiClient.post('/api/v1/time-off/grants/', data)
    return unwrap(response)
  },

  async updateGoce(id: string, data: Partial<GoceVacacionesForm>): Promise<GoceVacaciones> {
    const response = await apiClient.patch(`/api/v1/time-off/grants/${id}/`, data)
    return unwrap(response)
  },

  async deleteGoce(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/time-off/grants/${id}/`)
  },

  async getHistorialSolicitud(solicitudId: string): Promise<HistorialSolicitudVacaciones[]> {
    const response = await apiClient.get(`/api/v1/time-off/history/?solicitud_vacaciones=${solicitudId}`)
    return asArray<any>(unwrap(response))
  },

  async getEstadisticas(filtros?: FiltrosEstadisticas): Promise<any> {
    const params = new URLSearchParams()
    if (filtros?.ano) params.append('ano', filtros.ano.toString())
    if (filtros?.area) params.append('area_id', filtros.area.toString())
    const response = await apiClient.get(`/api/v1/time-off/reports/estadisticas/${params.toString() ? `?${params}` : ''}`)
    return unwrap(response)
  },

  async getEmpleadosDiasVencidos(ano?: number): Promise<EmpleadoDiasVencidos[]> {
    const response = await apiClient.get(`/api/v1/time-off/reports/dias-vencidos/${ano ? `?ano=${ano}` : ''}`)
    return asArray<any>(unwrap(response)).map((row) => ({
      empleado_id: row.empleado_id,
      empleado_nombre_completo: row.empleado_nombre,
      empleado_numero_empleado: row.empleado_rut,
      area_nombre: row.area_nombre,
      ano: row.ano_periodo,
      dias_correspondientes: row.dias_correspondientes,
      dias_vencidos: row.dias_vencidos,
      porcentaje_uso: Number(row.porcentaje_uso || 0),
      fecha_vencimiento: row.fecha_vencimiento,
    }))
  },

  async getEstadisticasPorArea(ano?: number): Promise<EstadisticasVacaciones[]> {
    const raw = await this.getEstadisticas({ ano })
    const periodos = raw?.periodos || {}
    return [
      {
        area_nombre: 'General',
        ano: raw?.ano || (ano || new Date().getFullYear()),
        total_empleados: periodos.total_empleados || 0,
        total_solicitudes: raw?.solicitudes?.total_solicitudes || 0,
        total_dias_correspondientes: periodos.total_dias_correspondientes || 0,
        total_dias_pendientes: periodos.total_dias_pendientes || 0,
        total_goces: raw?.goces?.total_goces || 0,
      },
    ]
  },

  async getResumenPeriodo(empleadoId?: string, periodoId?: string): Promise<ResumenPeriodo | null> {
    const periodos = await this.getPeriodos(empleadoId)
    const periodo = (periodoId ? periodos.find((p) => p.id === periodoId) : periodos[0]) || null
    if (!periodo) return null
    const vencimiento = new Date(periodo.fecha_vencimiento)
    const hoy = new Date()
    const diff = (vencimiento.getTime() - hoy.getTime()) / (1000 * 60 * 60 * 24)
    return {
      dias_correspondientes: periodo.dias_correspondientes,
      dias_gozados: periodo.dias_gozados,
      dias_pendientes: periodo.dias_pendientes,
      dias_vencidos: 0,
      vencimiento_proximo: diff >= 0 && diff <= 30,
    }
  },
}

export default timeOffService
