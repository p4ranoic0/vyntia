import { apiClient } from '@/lib/api'
import { getErrorMessage } from '@/lib/errorUtils'

export type TipoPlantilla =
  | 'certificado_trabajo'
  | 'constancia_laboral'
  | 'contrato'
  | 'adenda'

export interface PlantillaDocumento {
  plantilla_id: number
  tipo: TipoPlantilla
  tipo_texto: string
  nombre: string
  descripcion: string
  activa: boolean
  fecha_creacion: string
  variables_disponibles: string[]
  archivo_nombre: string | null
}

export interface SubirPlantillaData {
  nombre: string
  tipo: TipoPlantilla
  descripcion: string
  archivo: File
}

export interface GenerarDesdeTemplateData {
  plantilla_id: number
  empleado_id?: number
  contrato_id?: number
  formato: 'docx' | 'pdf'
  guardar_documento: boolean
  proposito?: string
  incluir_salario?: boolean
}

export interface GenerarDesdeTemplateResult {
  documento_id?: number
  archivo_url?: string
  nombre_archivo?: string
  formato?: string
}

export const TIPO_PLANTILLA_LABELS: Record<TipoPlantilla, string> = {
  certificado_trabajo: 'Certificado de Trabajo',
  constancia_laboral: 'Constancia Laboral',
  contrato: 'Contrato',
  adenda: 'Adenda',
}

export const TIPO_PLANTILLA_BADGE: Record<TipoPlantilla, string> = {
  certificado_trabajo: 'bg-blue-100 text-blue-800',
  constancia_laboral: 'bg-green-100 text-green-800',
  contrato: 'bg-purple-100 text-purple-800',
  adenda: 'bg-orange-100 text-orange-800',
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function extractData(raw: any): any {
  return raw?.data?.results ?? raw?.results ?? raw?.data ?? raw
}

export const plantillasService = {
  async getAll(tipo?: TipoPlantilla): Promise<PlantillaDocumento[]> {
    try {
      const params: Record<string, string> = {}
      if (tipo) params.tipo = tipo
      const response = await apiClient.get(
        '/api/v1/rrhh/documentos/plantillas-word/',
        params,
      )
      const data = extractData(response.data)
      return Array.isArray(data) ? data : []
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async subir(data: SubirPlantillaData): Promise<PlantillaDocumento> {
    try {
      const formData = new FormData()
      formData.append('nombre', data.nombre)
      formData.append('tipo', data.tipo)
      formData.append('descripcion', data.descripcion)
      formData.append('archivo', data.archivo)
      const response = await apiClient.post(
        '/api/v1/rrhh/documentos/plantillas-word/subir/',
        formData,
      )
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data
      return raw?.data ?? raw
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async eliminar(id: number): Promise<void> {
    try {
      await apiClient.delete(
        `/api/v1/rrhh/documentos/plantillas-word/${id}/eliminar/`,
      )
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async descargar(id: number, nombreArchivo: string): Promise<void> {
    try {
      const response = await apiClient.getBlob(
        `/api/v1/rrhh/documentos/plantillas-word/${id}/descargar/`,
      )
      const url = URL.createObjectURL(response.data)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = nombreArchivo || `plantilla_${id}.docx`
      document.body.appendChild(anchor)
      anchor.click()
      anchor.remove()
      URL.revokeObjectURL(url)
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async generarDesdeTemplateWord(
    data: GenerarDesdeTemplateData,
  ): Promise<GenerarDesdeTemplateResult> {
    try {
      const response = await apiClient.post(
        '/api/v1/rrhh/documentos/generar-desde-plantilla-word/',
        data,
      )
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data
      return raw?.data ?? raw
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}
