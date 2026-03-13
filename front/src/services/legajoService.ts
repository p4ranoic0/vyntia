import { apiClient } from '@/lib/api'
import { getErrorMessage } from '@/lib/errorUtils'

export interface Documento {
  documento_id: number
  empleado: number
  empleado_nombre?: string
  tipo_documento: string
  categoria: string
  nombre_documento: string
  descripcion_documento?: string
  archivo?: string
  nombre_archivo_original?: string
  formato_archivo?: string
  tamano_archivo?: number
  fecha_emision?: string
  fecha_vencimiento?: string
  entidad_emisora?: string
  numero_referencia?: string
  estado_documento: string
  nivel_acceso: string
  fecha_creacion: string
  fecha_actualizacion: string
}

export interface DocumentoFormData {
  empleado: number
  tipo_documento: string
  categoria: string
  nombre_documento: string
  descripcion_documento?: string
  archivo?: File
  fecha_emision?: string
  fecha_vencimiento?: string
  entidad_emisora?: string
  numero_referencia?: string
  estado_documento?: string
  nivel_acceso?: string
}

export const TIPO_DOCUMENTO_LABELS: Record<string, string> = {
  dni: 'DNI',
  pasaporte: 'Pasaporte',
  carnet_extranjeria: 'Carnet de Extranjeria',
  licencia_conducir: 'Licencia de Conducir',
  certificado_nacimiento: 'Certificado de Nacimiento',
  certificado_estudios: 'Certificado de Estudios',
  titulo_profesional: 'Titulo Profesional',
  diploma: 'Diploma',
  certificado_trabajo: 'Certificado de Trabajo',
  carta_recomendacion: 'Carta de Recomendacion',
  cv: 'Curriculum Vitae',
  foto: 'Fotografia',
  certificado_medico: 'Certificado Medico',
  certificado_antecedentes: 'Certificado de Antecedentes',
  declaracion_jurada: 'Declaracion Jurada',
  contrato_trabajo: 'Contrato de Trabajo',
  adenda_contrato: 'Adenda de Contrato',
  memorandum: 'Memorandum',
  carta_amonestacion: 'Carta de Amonestacion',
  solicitud_vacaciones: 'Solicitud de Vacaciones',
  certificado_capacitacion: 'Certificado de Capacitacion',
  evaluacion_desempeno: 'Evaluacion de Desempeno',
  // Documentos institucionales
  boleta_pago: 'Boleta de Pago',
  constancia_trabajo: 'Constancia de Trabajo',
  constancia_participacion: 'Constancia de Participacion',
  constancia_haberes: 'Constancia de Haberes',
  resolucion_encargatura: 'Resolucion de Encargatura',
  resolucion_licencia: 'Resolucion de Licencia',
  resolucion_sancion: 'Resolucion de Sancion',
  carta_cese: 'Carta de Cese',
  otros: 'Otros',
}

export const CATEGORIA_LABELS: Record<string, string> = {
  personal: 'Personal',
  academico: 'Academico',
  laboral: 'Laboral',
  medico: 'Medico',
  legal: 'Legal',
  administrativo: 'Administrativo',
  capacitacion: 'Capacitacion',
  evaluacion: 'Evaluacion',
  remuneraciones: 'Remuneraciones',
  ubicacion: 'Ubicacion',
  otros: 'Otros',
}

// Tipos de documento que son institucionales (generados por la entidad)
export const TIPOS_INSTITUCIONALES = [
  'boleta_pago', 'contrato_trabajo', 'adenda_contrato',
  'constancia_trabajo', 'constancia_participacion', 'constancia_haberes',
  'resolucion_encargatura', 'resolucion_licencia', 'resolucion_sancion',
  'memorandum', 'carta_amonestacion', 'carta_cese',
  'evaluacion_desempeno',
]

/** Mapeo tipo_documento -> categoria por defecto (auto-asignacion) */
export const TIPO_CATEGORIA_MAP: Record<string, string> = {
  dni: 'personal',
  pasaporte: 'personal',
  carnet_extranjeria: 'personal',
  licencia_conducir: 'personal',
  certificado_nacimiento: 'personal',
  foto: 'personal',
  cv: 'personal',
  declaracion_jurada: 'legal',
  certificado_estudios: 'academico',
  titulo_profesional: 'academico',
  diploma: 'academico',
  certificado_capacitacion: 'capacitacion',
  certificado_trabajo: 'laboral',
  carta_recomendacion: 'laboral',
  certificado_medico: 'medico',
  certificado_antecedentes: 'legal',
  solicitud_vacaciones: 'laboral',
  boleta_pago: 'remuneraciones',
  contrato_trabajo: 'laboral',
  adenda_contrato: 'laboral',
  constancia_trabajo: 'laboral',
  constancia_participacion: 'laboral',
  constancia_haberes: 'remuneraciones',
  resolucion_encargatura: 'administrativo',
  resolucion_licencia: 'administrativo',
  resolucion_sancion: 'administrativo',
  memorandum: 'administrativo',
  carta_amonestacion: 'administrativo',
  carta_cese: 'administrativo',
  evaluacion_desempeno: 'evaluacion',
  otros: 'otros',
}

export const legajoService = {
  /**
   * Obtener documentos de un empleado específico
   */
  async getByEmpleado(empleadoId: number, categoria?: string): Promise<Documento[]> {
    try {
      const params: Record<string, string | number> = { empleado: empleadoId }
      if (categoria) params.categoria = categoria
      const response = await apiClient.get('/api/v1/rrhh/documentos-digitales/', params)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data
      const data = raw?.data?.results ?? raw?.results ?? raw?.data ?? raw
      return Array.isArray(data) ? data : []
    } catch (error) {
      console.error('Error fetching documentos:', error)
      throw new Error(getErrorMessage(error))
    }
  },

  /**
   * Obtener un documento por ID
   */
  async getById(id: number): Promise<Documento> {
    try {
      const response = await apiClient.get(`/api/v1/rrhh/documentos-digitales/${id}/`)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data
      return raw?.data ?? raw
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  /**
   * Subir un nuevo documento (usa FormData para soportar archivos)
   * Axios detecta FormData y establece multipart/form-data automáticamente
   */
  async create(data: DocumentoFormData): Promise<Documento> {
    try {
      const formData = new FormData()
      formData.append('empleado', String(data.empleado))
      formData.append('tipo_documento', data.tipo_documento)
      formData.append('categoria', data.categoria)
      formData.append('nombre_documento', data.nombre_documento)
      if (data.descripcion_documento) formData.append('descripcion_documento', data.descripcion_documento)
      if (data.archivo) formData.append('archivo', data.archivo)
      if (data.fecha_emision) formData.append('fecha_emision', data.fecha_emision)
      if (data.fecha_vencimiento) formData.append('fecha_vencimiento', data.fecha_vencimiento)
      if (data.entidad_emisora) formData.append('entidad_emisora', data.entidad_emisora)
      if (data.numero_referencia) formData.append('numero_referencia', data.numero_referencia)
      formData.append('estado_documento', data.estado_documento ?? 'activo')
      formData.append('nivel_acceso', data.nivel_acceso ?? 'restringido')

      // apiClient.post only accepts 2 args; axios handles FormData content-type automatically
      const response = await apiClient.post('/api/v1/rrhh/documentos-digitales/', formData)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data
      return raw?.data ?? raw
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  /**
   * Eliminar un documento
   */
  async delete(id: number): Promise<void> {
    try {
      await apiClient.delete(`/api/v1/rrhh/documentos-digitales/${id}/`)
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  /**
   * Validar un documento (RRHH)
   */
  async validar(id: number, observaciones?: string): Promise<void> {
    try {
      await apiClient.post(`/api/v1/rrhh/documentos-digitales/${id}/validar/`, {
        observaciones: observaciones || '',
      })
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  /**
   * Rechazar un documento (RRHH)
   */
  async rechazar(id: number, motivo: string): Promise<void> {
    try {
      await apiClient.post(`/api/v1/rrhh/documentos-digitales/${id}/rechazar/`, {
        motivo,
      })
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  /**
   * Subir documento institucional al legajo de un empleado (RRHH)
   */
  async subirInstitucional(data: {
    empleado: number
    tipo_documento: string
    nombre_documento?: string
    descripcion?: string
    fecha_emision?: string
    periodo?: string
    archivos: File[]
  }): Promise<Documento[]> {
    try {
      const formData = new FormData()
      formData.append('empleado', String(data.empleado))
      formData.append('tipo_documento', data.tipo_documento)
      if (data.nombre_documento) formData.append('nombre_documento', data.nombre_documento)
      if (data.descripcion) formData.append('descripcion', data.descripcion)
      if (data.fecha_emision) formData.append('fecha_emision', data.fecha_emision)
      if (data.periodo) formData.append('periodo', data.periodo)
      for (const archivo of data.archivos) {
        formData.append('archivos', archivo)
      }

      const response = await apiClient.post('/api/v1/rrhh/documentos-digitales/subir_institucional/', formData)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data
      const result = raw?.data ?? raw
      return Array.isArray(result) ? result : [result]
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}
