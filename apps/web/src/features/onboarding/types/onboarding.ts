// Local onboarding types — supplement generated types from front/src/generated/api/

export type EstadoOnboarding =
  | 'pendiente_datos'
  | 'pendiente_documentos'
  | 'pendiente_validacion'
  | 'observado'
  | 'completado'

export type TipoDocumento =
  | 'foto'
  | 'dni'
  | 'carnet_extranjeria'
  | 'dni_familiar'
  | 'certificado_nacimiento'
  | 'acta_matrimonio'
  | 'certificado_estudios'
  | 'titulo_profesional'
  | 'diploma'
  | 'certificado_capacitacion'
  | 'constancia_trabajo'
  | 'declaracion_jurada'
  | 'cv'
  | 'certificado_trabajo'
  | 'carta_recomendacion'

export interface DocumentInfo {
  id: string
  tipo_documento: TipoDocumento
  nombre_documento: string
  estado_documento: 'pendiente_revision' | 'aprobado' | 'rechazado'
  fecha_subida: string | null
  archivo_url?: string | null
  observaciones?: string | null
}

export interface OnboardingStatus {
  id: string
  empleado: string
  empleado_nombre: string
  empleado_documento: string
  estado_onboarding: EstadoOnboarding
  progreso_porcentaje: number
  dni_subido: boolean
  declaraciones_juradas_subidas: boolean
  certificados_academicos_subidos: boolean
  certificados_trabajo_subidos: boolean
  documentos_familiares_subidos: boolean
  datos_personales_completos: boolean
  email_bienvenida_enviado: boolean
  fecha_email_bienvenida: string | null
  last_login: string | null
  observaciones: string | null
  fecha_inicio: string
}

export interface UploadDocumentResponse {
  id: string
  tipo_documento: string
  estado_documento: string
  fecha_subida: string | null
  nombre_documento: string
  archivo_url?: string | null
}

export type SectionStatus = 'completo' | 'en_revision' | 'observado' | 'pendiente'

/** Returns true when the employee has not logged in and 5+ days have passed since welcome email. */
export function computeAlert(o: Pick<OnboardingStatus, 'fecha_email_bienvenida' | 'last_login'>): boolean {
  if (!o.fecha_email_bienvenida) return false
  if (o.last_login != null) return false
  // Use plain JS date math
  const ms = Date.now() - new Date(o.fecha_email_bienvenida).getTime()
  const days = ms / (1000 * 60 * 60 * 24)
  return days >= 5
}
