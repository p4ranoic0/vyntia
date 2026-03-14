import { LockKeyhole } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DocumentInfo } from '../types/onboarding'
import { DocumentUploadZone } from './DocumentUploadZone'

interface DatosLaborales {
  cargo?: string
  area?: string
  regimen?: string
}

interface OnboardingTabLaboralProps {
  empleadoId: number
  docs: DocumentInfo[]
  datosLaborales?: DatosLaborales
}

export function OnboardingTabLaboral({ empleadoId, docs, datosLaborales }: OnboardingTabLaboralProps) {
  return (
    <div className="space-y-6">
      {/* Read-only laboral data card */}
      <Card className="border-muted bg-muted/20">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <LockKeyhole className="h-4 w-4" />
            Datos gestionados por RRHH
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Cargo</p>
              <p className="text-sm font-medium text-muted-foreground">
                {datosLaborales?.cargo ?? '—'}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Área</p>
              <p className="text-sm font-medium text-muted-foreground">
                {datosLaborales?.area ?? '—'}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Régimen laboral</p>
              <p className="text-sm font-medium text-muted-foreground">
                {datosLaborales?.regimen ?? '—'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <hr className="border-border" />

      {/* Document upload zones */}
      <DocumentUploadZone
        tipoDocumento="declaracion_jurada"
        label="Declaración Jurada"
        existingDoc={docs.find(d => d.tipo_documento === 'declaracion_jurada') ?? null}
        empleadoId={empleadoId}
      />
      <DocumentUploadZone
        tipoDocumento="cv"
        label="Currículum Vitae"
        existingDoc={docs.find(d => d.tipo_documento === 'cv') ?? null}
        empleadoId={empleadoId}
      />
      <DocumentUploadZone
        tipoDocumento="certificado_trabajo"
        label="Certificado de trabajo anterior"
        existingDoc={docs.find(d => d.tipo_documento === 'certificado_trabajo') ?? null}
        empleadoId={empleadoId}
      />
      <DocumentUploadZone
        tipoDocumento="carta_recomendacion"
        label="Carta de recomendación"
        existingDoc={docs.find(d => d.tipo_documento === 'carta_recomendacion') ?? null}
        empleadoId={empleadoId}
      />
    </div>
  )
}
