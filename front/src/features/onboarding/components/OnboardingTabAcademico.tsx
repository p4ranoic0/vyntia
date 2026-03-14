import { DocumentInfo } from '../types/onboarding'
import { DocumentUploadZone } from './DocumentUploadZone'

interface OnboardingTabAcademicoProps {
  empleadoId: number
  docs: DocumentInfo[]
}

export function OnboardingTabAcademico({ empleadoId, docs }: OnboardingTabAcademicoProps) {
  return (
    <div className="space-y-6">
      <DocumentUploadZone
        tipoDocumento="certificado_estudios"
        label="Certificado de estudios"
        existingDoc={docs.find(d => d.tipo_documento === 'certificado_estudios') ?? null}
        empleadoId={empleadoId}
      />
      <DocumentUploadZone
        tipoDocumento="titulo_profesional"
        label="Título profesional"
        existingDoc={docs.find(d => d.tipo_documento === 'titulo_profesional') ?? null}
        empleadoId={empleadoId}
      />
      <DocumentUploadZone
        tipoDocumento="diploma"
        label="Diploma"
        existingDoc={docs.find(d => d.tipo_documento === 'diploma') ?? null}
        empleadoId={empleadoId}
      />
    </div>
  )
}
