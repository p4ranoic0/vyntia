import { DocumentInfo } from '../types/onboarding'
import { DocumentUploadZone } from './DocumentUploadZone'

interface OnboardingTabFamiliarProps {
  empleadoId: number
  docs: DocumentInfo[]
}

export function OnboardingTabFamiliar({ empleadoId, docs }: OnboardingTabFamiliarProps) {
  return (
    <div className="space-y-6">
      <DocumentUploadZone
        tipoDocumento="dni_familiar"
        label="DNI de familiar"
        existingDoc={docs.find(d => d.tipo_documento === 'dni_familiar') ?? null}
        empleadoId={empleadoId}
      />
      <DocumentUploadZone
        tipoDocumento="certificado_nacimiento"
        label="Partida de nacimiento"
        existingDoc={docs.find(d => d.tipo_documento === 'certificado_nacimiento') ?? null}
        empleadoId={empleadoId}
      />
    </div>
  )
}
