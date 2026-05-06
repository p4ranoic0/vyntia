import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { LockKeyhole, Plus, Briefcase, Upload, X } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { DocumentUploadZone } from './DocumentUploadZone'
import { DocumentPreviewModal } from './DocumentPreviewModal'
import { getConstanciasTrabajo } from '../services/onboardingDataService'
import { subirDocumento } from '../services/onboardingUploadService'
import { cn } from '@/lib/utils'

interface DatosLaboralesInfo {
  cargo?: string
  area?: string
  regimen?: string
}

interface OnboardingTabLaboralProps {
  empleadoId: number
  docs?: import('../types/onboarding').DocumentInfo[]
  datosLaborales?: DatosLaboralesInfo
}

interface ExpLaboralForm {
  empresa: string
  fecha_inicio: string
  fecha_fin: string
}

const EMPTY_FORM: ExpLaboralForm = { empresa: '', fecha_inicio: '', fecha_fin: '' }

export function OnboardingTabLaboral({ empleadoId, docs = [], datosLaborales }: OnboardingTabLaboralProps) {
  const queryClient = useQueryClient()
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [form, setForm] = useState<ExpLaboralForm>(EMPTY_FORM)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Two-phase upload state
  const [pendingDoc, setPendingDoc] = useState<{ file: File; tipo: string; label: string } | null>(null)
  const [stagedFile, setStagedFile] = useState<File | null>(null)
  const [isDocPreviewOpen, setIsDocPreviewOpen] = useState(false)

  const { data: constancias = [] } = useQuery({
    queryKey: ['constancias-trabajo', empleadoId],
    queryFn: () => getConstanciasTrabajo(empleadoId),
  })

  const handleFileSelected = (file: File) => {
    setStagedFile(file)
    setIsDocPreviewOpen(true)
  }

  const handlePreviewConfirm = () => {
    if (stagedFile) setPendingDoc({ file: stagedFile, tipo: 'constancia_trabajo', label: 'Constancia de trabajo' })
    setStagedFile(null)
    setIsDocPreviewOpen(false)
  }

  const handlePreviewCancel = () => {
    setStagedFile(null)
    setIsDocPreviewOpen(false)
  }

  const handleDialogClose = () => {
    setPendingDoc(null)
    setStagedFile(null)
    setIsDocPreviewOpen(false)
    setForm(EMPTY_FORM)
    setIsAddDialogOpen(false)
  }

  const handleSubmit = async () => {
    if (!form.empresa) {
      toast.error('Ingrese el nombre de la empresa')
      return
    }
    if (!pendingDoc) {
      toast.error('Seleccione una constancia de trabajo')
      return
    }
    setIsSubmitting(true)
    try {
      await subirDocumento(
        empleadoId,
        'constancia_trabajo',
        'laboral',
        `Constancia - ${form.empresa}`,
        pendingDoc.file,
        {
          ...(form.fecha_inicio ? { fecha_inicio: form.fecha_inicio } : {}),
          ...(form.fecha_fin ? { fecha_fin: form.fecha_fin } : {}),
        }
      )
      queryClient.invalidateQueries({ queryKey: ['constancias-trabajo', empleadoId] })
      queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
      queryClient.invalidateQueries({ queryKey: ['legajo-docs', empleadoId] })
      toast.success('Constancia de trabajo guardada exitosamente')
      handleDialogClose()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg ?? 'Error al guardar constancia de trabajo')
    } finally {
      setIsSubmitting(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
    disabled: isSubmitting || !!pendingDoc,
    onDropAccepted: ([file]) => handleFileSelected(file),
    onDropRejected: ([rejection]) => {
      const code = rejection.errors[0]?.code
      if (code === 'file-too-large') toast.error('El archivo supera los 10 MB permitidos')
      else toast.error('Solo se permiten archivos PDF')
    },
  })

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
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Area</p>
              <p className="text-sm font-medium text-muted-foreground">
                {datosLaborales?.area ?? '—'}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Regimen laboral</p>
              <p className="text-sm font-medium text-muted-foreground">
                {datosLaborales?.regimen ?? '—'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <hr className="border-border" />

      {/* Static upload zones */}
      <DocumentUploadZone
        tipoDocumento="declaracion_jurada"
        label="Declaracion Jurada"
        existingDoc={docs.find(d => d.tipo_documento === 'declaracion_jurada') ?? null}
        empleadoId={empleadoId}
      />
      <DocumentUploadZone
        tipoDocumento="cv"
        label="Curriculum Vitae"
        existingDoc={docs.find(d => d.tipo_documento === 'cv') ?? null}
        empleadoId={empleadoId}
      />
      <DocumentUploadZone
        tipoDocumento="carta_recomendacion"
        label="Carta de recomendacion"
        existingDoc={docs.find(d => d.tipo_documento === 'carta_recomendacion') ?? null}
        empleadoId={empleadoId}
      />

      <hr className="border-border" />

      {/* Experiencia Laboral Accordion */}
      <Accordion type="single" collapsible className="w-full">
        <AccordionItem value="experiencia-laboral">
          <AccordionTrigger>
            <div className="flex items-center gap-2">
              <Briefcase className="h-4 w-4" />
              Experiencia Laboral
              {(constancias as Record<string, unknown>[]).length > 0 && (
                <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">
                  {(constancias as Record<string, unknown>[]).length}
                </span>
              )}
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-3">
              {(constancias as Record<string, unknown>[]).length === 0 && (
                <p className="text-sm text-muted-foreground">
                  No ha agregado constancias de trabajo aun.
                </p>
              )}
              {(constancias as Record<string, unknown>[]).map((constancia: Record<string, unknown>, idx: number) => (
                <Card key={(constancia.id as string) ?? idx} className="border">
                  <CardHeader className="pb-2">
                    <p className="font-medium text-sm">
                      {(constancia.entidad_emisora as string) ?? (constancia.nombre_documento as string) ?? 'Constancia de trabajo'}
                    </p>
                    {(constancia.fecha_emision || constancia.fecha_vencimiento) && (
                      <p className="text-xs text-muted-foreground">
                        {constancia.fecha_emision as string ?? ''}
                        {constancia.fecha_emision && constancia.fecha_vencimiento ? ' — ' : ''}
                        {constancia.fecha_vencimiento as string ?? ''}
                      </p>
                    )}
                  </CardHeader>
                  <CardContent className="pt-0">
                    <DocumentUploadZone
                      tipoDocumento="constancia_trabajo"
                      label="Constancia de trabajo (PDF)"
                      empleadoId={empleadoId}
                      onUploadSuccess={() => {
                        queryClient.invalidateQueries({ queryKey: ['constancias-trabajo', empleadoId] })
                        queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
                        queryClient.invalidateQueries({ queryKey: ['legajo-docs', empleadoId] })
                      }}
                    />
                  </CardContent>
                </Card>
              ))}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsAddDialogOpen(true)}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Agregar certificado de trabajo
              </Button>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      {/* Add Constancia Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={(open) => { if (!open) handleDialogClose() }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Agregar constancia de trabajo</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label htmlFor="empresa">Empresa *</Label>
              <Input
                id="empresa"
                value={form.empresa}
                onChange={(e) => setForm(f => ({ ...f, empresa: e.target.value }))}
                placeholder="Nombre de la empresa"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="exp-inicio">Fecha inicio</Label>
                <Input
                  id="exp-inicio"
                  type="date"
                  value={form.fecha_inicio}
                  onChange={(e) => setForm(f => ({ ...f, fecha_inicio: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="exp-fin">Fecha fin</Label>
                <Input
                  id="exp-fin"
                  type="date"
                  value={form.fecha_fin}
                  onChange={(e) => setForm(f => ({ ...f, fecha_fin: e.target.value }))}
                />
              </div>
            </div>
            <div className="space-y-1">
              <Label>Constancia de trabajo (PDF) *</Label>
              {pendingDoc ? (
                <div className="flex items-center gap-2 rounded border border-primary/30 bg-primary/5 px-3 py-2">
                  <span className="flex-1 text-xs truncate">{pendingDoc.file.name}</span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-5 w-5 p-0"
                    onClick={() => setPendingDoc(null)}
                    disabled={isSubmitting}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              ) : (
                <div
                  {...getRootProps()}
                  className={cn(
                    'rounded-lg border-2 border-dashed p-6 text-center cursor-pointer transition-colors mt-1',
                    isDragActive
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50 hover:bg-muted/50',
                    isSubmitting && 'opacity-50 cursor-not-allowed'
                  )}
                >
                  <input {...getInputProps()} />
                  <div className="flex flex-col items-center gap-2 text-sm text-muted-foreground">
                    <Upload className="h-5 w-5" />
                    <span className="font-medium">
                      {isDragActive ? 'Suelte el archivo aqui' : 'Arrastre o haga clic para subir PDF'}
                    </span>
                    <span className="text-xs">PDF, max. 10 MB</span>
                  </div>
                </div>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={handleDialogClose} disabled={isSubmitting}>
              Cancelar
            </Button>
            <Button onClick={handleSubmit} disabled={isSubmitting || !pendingDoc}>
              {isSubmitting ? 'Guardando...' : 'Guardar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Document Preview Modal */}
      <DocumentPreviewModal
        file={stagedFile}
        archivoUrl={null}
        label="Constancia de trabajo"
        isOpen={isDocPreviewOpen}
        onConfirm={handlePreviewConfirm}
        onCancel={handlePreviewCancel}
      />
    </div>
  )
}
