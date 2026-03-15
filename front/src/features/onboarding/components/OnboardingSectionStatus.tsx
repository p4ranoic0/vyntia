import { CheckCircle2, Clock, AlertCircle, Circle } from 'lucide-react'
import { DocumentInfo, SectionStatus } from '../types/onboarding'

const SECTION_DOC_TYPES: Record<string, string[]> = {
  personal: ['foto', 'dni', 'carnet_extranjeria'],
  familiar: ['dni_familiar', 'certificado_nacimiento', 'acta_matrimonio'],
  academico: ['certificado_estudios', 'titulo_profesional', 'certificado_capacitacion', 'diploma'],
  laboral: ['declaracion_jurada', 'cv', 'constancia_trabajo', 'carta_recomendacion', 'certificado_trabajo'],
}

export function computeStatus(docs: DocumentInfo[], tipos: string[]): SectionStatus {
  const sectionDocs = docs.filter(d => tipos.includes(d.tipo_documento))
  if (sectionDocs.length === 0) return 'pendiente'
  if (sectionDocs.some(d => d.estado_documento === 'rechazado')) return 'observado'
  if (sectionDocs.every(d => d.estado_documento === 'aprobado')) return 'completo'
  return 'en_revision'
}

const STATUS_CONFIG: Record<SectionStatus, { icon: React.ReactNode; label: string; color: string }> = {
  completo: {
    icon: <CheckCircle2 className="h-4 w-4 text-green-600" />,
    label: 'Completo',
    color: 'text-green-600',
  },
  en_revision: {
    icon: <Clock className="h-4 w-4 text-yellow-600" />,
    label: 'En revisión',
    color: 'text-yellow-600',
  },
  observado: {
    icon: <AlertCircle className="h-4 w-4 text-red-600" />,
    label: 'Observado',
    color: 'text-red-600',
  },
  pendiente: {
    icon: <Circle className="h-4 w-4 text-gray-400" />,
    label: 'Pendiente',
    color: 'text-gray-400',
  },
}

const SECTION_LABELS: Record<string, string> = {
  personal: 'Personal',
  familiar: 'Familiar',
  academico: 'Académico',
  laboral: 'Laboral',
}

interface OnboardingSectionStatusProps {
  docs: DocumentInfo[]
}

export function OnboardingSectionStatus({ docs }: OnboardingSectionStatusProps) {
  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
      {Object.keys(SECTION_DOC_TYPES).map(section => {
        const status = computeStatus(docs, SECTION_DOC_TYPES[section])
        const config = STATUS_CONFIG[status]
        return (
          <div
            key={section}
            className="flex flex-col items-center gap-1 rounded-lg border bg-card p-3 text-center shadow-sm"
          >
            <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              {SECTION_LABELS[section]}
            </span>
            <div className="flex items-center gap-1">
              {config.icon}
              <span className={`text-xs font-medium ${config.color}`}>{config.label}</span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
